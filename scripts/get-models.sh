#!/usr/bin/env bash
# Extracts the official NSPL 0.5 um SPICE models of PDK 260820 from the kit's copy of the PDK
# (docs/ETRI_0p5um_NSPL_260820/NSPL_05CMOS_PDK_260820.tar.gz, fetched with ETRI050_WITH_DOCS=1)
# into designs/etri050/sim/models (git-ignored: the PDK must not be redistributed).
#   05cmos_mosfet_corner.lib   TT/SS/FF/SF/FS corners, devices nmos4 / pmos4
#   05cmos_model_260210.lib    MOS + DIODE, BJT, RES, CAP sections
set -euo pipefail

WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIT="${ETRI050_DK:-$WS/.pdk/ETRI050_DesignKit}"
TGZ="$KIT/docs/ETRI_0p5um_NSPL_260820/NSPL_05CMOS_PDK_260820.tar.gz"
OUT="$WS/designs/etri050/sim/models"

if [ ! -f "$TGZ" ]; then
  echo "[models] $TGZ not found: run ETRI050_WITH_DOCS=1 bash scripts/setup-etri050.sh"
  exit 1
fi
mkdir -p "$OUT"
tar xzf "$TGZ" -C "$OUT" --strip-components=2 \
  NSPL_05CMOS_PDK_260820/Model_Parameter/05cmos_mosfet_corner.lib \
  NSPL_05CMOS_PDK_260820/Model_Parameter/05cmos_model_260210.lib
printf 'set num_threads=1\n' > "$OUT/.spiceinit"
sha256sum "$OUT"/*.lib | sed "s#$OUT/##"
echo "[models] $OUT"
