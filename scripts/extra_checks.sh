#!/usr/bin/env bash
# Rule checks that the kit's KLayout deck does not cover, for one or more GDS files:
#   calibre_rules.py   the 73 checks of ETRI's Calibre deck that the KLayout deck leaves out
#   metal_rules.py     rules 7-12 (contact, metal, via) with the rule document values, unshielded
#   antenna_rules.py   3.PL1.ANT, 8.MET1.ANT, 10.MET2.ANT, 12.MET3.ANT (no diode credit)
# usage: bash scripts/extra_checks.sh <file.gds> [<file.gds> ...]     (exit 1 if any check reports)
#   BASELINE=<ring.gds> bash scripts/extra_checks.sh <chip.gds>   markers also found at the same place in the
#   baseline (the pad ring alone: ETRI's GPIO cells) are listed but do not fail the check
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ $# -ge 1 ] || { echo "usage: bash scripts/extra_checks.sh <file.gds> [...]"; exit 2; }
kl() { KLAYOUT_PATH="${KLAYOUT_HOME:-$HOME/.klayout}" klayout -b "$@"; }
rc=0
for g in "$@"; do
  [ -f "$g" ] || { echo "$g: not found"; rc=1; continue; }
  echo "== $g"
  if [ -n "${BASELINE:-}" ]; then
    a=$(python3 "$here/calibre_rules.py" --gds "$g" --baseline "$BASELINE" 2>&1 | tail -1)
    b=$(kl -r "$here/metal_rules.py" -rd gds="$g" -rd baseline="$BASELINE" 2>&1 | tail -1)
  else
    a=$(python3 "$here/calibre_rules.py" --gds "$g" 2>&1 | tail -1)
    b=$(kl -r "$here/metal_rules.py" -rd gds="$g" 2>&1 | tail -1)
  fi
  c=$(kl -r "$here/antenna_rules.py" -rd gds="$g" 2>&1 | tail -1)
  printf '  %s\n  %s\n  %s\n' "$a" "$b" "$c"
  [[ "$a" == *": 0 markers in 73 Calibre-only checks"* || "$a" == *", 0 not in the baseline"* ]] || rc=1
  [[ "$b" == *": 0 markers in rules 7-12"* || "$b" == *", 0 not in the baseline"* ]] || rc=1
  [[ "$c" == *": 0 nets over the antenna limits"* ]] || rc=1
done
[ $rc -eq 0 ] && echo "extra checks: all clean" || echo "extra checks: see the lines above"
exit $rc
