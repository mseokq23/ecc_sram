#!/usr/bin/env bash
# Rebuild the chip from its sources and run every check, block by block and on the whole chip.
# With --save, a chip that passes everything is stored in final/ (GDS, sha256, this report).
#
#   bash designs/etri050/chip/check_all.sh [--save]
#
# Blocks   control block: RTL, gate-level and frozen-netlist testbenches; frozen GDS: official KLayout
#          DRC + extra checks. Cell, array, SRAM macro, decoupling: regenerated, Magic DRC, official
#          KLayout DRC, Netgen LVS (etri-check) + extra checks
# Ring     pad ring with ETRI's GPIO cells, official KLayout DRC
# Chip     assembly; official KLayout DRC (the kit's conversion of ETRI's Calibre deck); the 73 Calibre
#          checks the KLayout deck leaves out; rules 7-12 with the rule document values; antenna rules;
#          transistor-level LVS of the core against the design netlists; submission GDS checks
# Rules 7-12 also report what ETRI's own GPIO cells contain; those markers are counted against the
# pad ring alone (the same cells, unchanged) and only markers that the ring does not have fail.
# Report: build/check_report.txt
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
# shellcheck disable=SC1091
source "$REPO/scripts/etri050-env.sh" >/dev/null 2>&1
unset DISPLAY
B="$HERE/build"
mkdir -p "$B/check"
R="$B/check_report.txt"
SAVE=0
[ "${1:-}" = "--save" ] && SAVE=1
D="$REPO/designs/etri050"
SB="$D/sram/build"
fail=0
: > "$R"
say() { echo "$*" | tee -a "$R"; }
# check <name> <pass-regex> <command...>: run, keep the log, PASS if the log matches the regex
check() {
  local name="$1" want="$2"; shift 2
  local log="$B/check/${name// /_}.log"
  (cd "$REPO" && "$@") > "$log" 2>&1
  local rc=$?
  if [ $rc -eq 0 ] && grep -qE "$want" "$log"; then
    say "PASS  $name"
  else
    say "FAIL  $name (exit $rc, see build/check/${name// /_}.log)"; fail=1
  fi
}
kl() { KLAYOUT_PATH="${KLAYOUT_HOME:-$HOME/.klayout}" klayout -b "$@"; }
drc_count() {   # official KLayout deck on a GDS -> number of markers
  local gds="$1" db="$B/check/$(basename "${1%.gds}")_drc.lyrdb"
  kl -r "$ETRI050_DRC_DECK" -rd gdsfile="$gds" -rd resultsfile="$db" > /dev/null 2>&1
  python3 "$REPO/scripts/lyrdb_summary.py" "$db" 0 2>/dev/null | head -1 | grep -oE "[0-9]+ markers" | grep -oE "[0-9]+"
}

say "ECC 8T SRAM chip check, $(date '+%Y-%m-%d %H:%M %Z'), repo $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null)$(git -C "$REPO" diff --quiet 2>/dev/null || echo ' (modified)')"
say "kit $(git -C "$ETRI050_DK" log -1 --format='%h %cs' 2>/dev/null), $(klayout -v 2>&1), magic $(magic --version 2>/dev/null), $(ngspice -v 2>&1 | grep -o 'ngspice-[0-9]*' | head -1)"
say ""
say "== control block"
check "ctrl RTL testbench" "TB RESULT: PASS" make -C designs/etri050/ctrl sim
check "ctrl gate-level testbench" "TB RESULT: PASS" make -C designs/etri050/ctrl gatesim
check "ctrl frozen netlist testbench" "TB RESULT: PASS" make -C designs/etri050/ctrl macrosim
gzip -dc "$D/ctrl/macro/ecc_fi_ctrl.gds.gz" > "$B/check/ecc_fi_ctrl.gds"
n=$(drc_count "$B/check/ecc_fi_ctrl.gds")
if [ "$n" = "0" ]; then say "PASS  ctrl frozen GDS official DRC (0 markers)"; else say "FAIL  ctrl frozen GDS official DRC ($n markers)"; fail=1; fi
check "ctrl frozen GDS extra checks" "extra checks: all clean" bash scripts/extra_checks.sh "$B/check/ecc_fi_ctrl.gds"

say "== SRAM blocks (regenerated)"
check "8T cell and 15x8 array: Magic DRC, official DRC, LVS" "PASS  ETRI-CHECK sram_array" \
  python3 designs/etri050/gen/sram8t.py all --check
grep -q "FAIL" "$B/check/8T_cell_and_15x8_array:_Magic_DRC,_official_DRC,_LVS.log" && { say "FAIL  cell (see log)"; fail=1; }
check "SRAM macro (array + column circuits): Magic DRC, official DRC, LVS" "PASS  ETRI-CHECK sram_macro" \
  python3 designs/etri050/gen/colper.py --check
check "decoupling VDDW and VDDA: Magic DRC, official DRC, LVS" "PASS  ETRI-CHECK decap_vdda" \
  python3 designs/etri050/gen/decap.py --check
grep -q "FAIL" "$B/check/decoupling_VDDW_and_VDDA:_Magic_DRC,_official_DRC,_LVS.log" && { say "FAIL  decap (see log)"; fail=1; }
check "SRAM blocks extra checks" "extra checks: all clean" bash scripts/extra_checks.sh \
  "$SB/sram8t.gds" "$SB/sram_array.gds" "$SB/sram_macro.gds" "$SB/decap_vddw.gds" "$SB/decap_vdda.gds"

say "== pad ring and chip"
check "pad ring (ETRI GPIO cells) official DRC" "ecc_sram_Pad_klayout.lyrdb: 0 markers" bash designs/etri050/chip/run_pad_ring.sh
check "chip assembly" "wrote .*ecc_sram_Top.gds" python3 designs/etri050/chip/assemble.py
G="$B/ecc_sram_Top.gds"
n=$(drc_count "$G")
if [ "$n" = "0" ]; then say "PASS  chip official DRC (KLayout deck from ETRI's Calibre deck): 0 markers"; else say "FAIL  chip official DRC: $n markers"; fail=1; fi
check "chip extra checks (Calibre-only 73, rules 7-12, antenna)" "extra checks: all clean" \
  env BASELINE="$B/ecc_sram_Pad.gds" bash scripts/extra_checks.sh "$G"
grep -E "Calibre-only|rules 7-12|antenna" "$B/check/chip_extra_checks_(Calibre-only_73,_rules_7-12,_antenna).log" | sed 's/^ */      /' | tee -a "$R"
check "core LVS (transistor level, Magic + Netgen)" "core LVS: MATCH" python3 designs/etri050/chip/core_lvs.py
grep -E "Number of devices|Number of nets" "$B/lvs/core_lvs.out" | tail -2 | sed 's/|.*//; s/^/      /' | tee -a "$R"
check "submission GDS checks (mychip_gds_check.py)" "통과 \(실패 0, 경고 0\)" \
  python3 scripts/mychip_gds_check.py --top ecc_sram_Top "$G"

say ""
if [ $fail -eq 0 ]; then
  say "ALL CHECKS PASSED: ${G#"$REPO"/}"
  if [ $SAVE -eq 1 ]; then
    F="$HERE/final"
    mkdir -p "$F"
    gzip -9 -n -c "$G" > "$F/ecc_sram_Top.gds.gz"
    (cd "$B" && sha256sum ecc_sram_Top.gds) > "$F/ecc_sram_Top.gds.sha256"
    (cd "$F" && sha256sum ecc_sram_Top.gds.gz) >> "$F/ecc_sram_Top.gds.sha256"
    say "saved ${F#"$REPO"/}/ecc_sram_Top.gds.gz"
    cp "$R" "$F/check_report.txt"
  fi
else
  say "SOME CHECKS FAILED: the chip is not saved"
fi
exit $fail
