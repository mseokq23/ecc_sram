#!/usr/bin/env bash
# Freeze the routed control block as the macro the chip assembly reads (after run_flow.sh):
#   macro/ecc_fi_ctrl.gds.gz      build/qflow/layout/ecc_fi_ctrl_F_grid.gds: flat, notches filled,
#                              snapped to the 0.01 um grid, official-rule KLayout DRC 0
#   macro/ecc_fi_ctrl_pins.txt    pin rectangles from the labels of the qflow layout (ecc_fi_ctrl.mag,
#                              scaled by its magscale line), before snapping; the assembly rounds them
#                              the way snap_grid.py rounded the GDS
#   macro/ecc_fi_ctrl.v           the gate netlist placed and routed (build/qflow/synthesis/
#                              ecc_fi_ctrl.rtlnopwr.v, after qflow's post-placement buffering; the
#                              netlist make qflowsim simulates)
#   macro/ecc_fi_ctrl.spc         its ecc_fi_ctrl subcircuit as qflow's LVS read it (synthesis/ecc_fi_ctrl.spc
#                              without the kit cell library it includes); chip/chip_lvs.py compares
#                              the macro inside the chip with it at device level
# The chip is assembled from the frozen macro, so a later qflow run cannot move its pins unnoticed.
# Compare a new run with the macro first: klayout -b -r scripts/gds_xor.py -rd a=... -rd b=...
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
L="$HERE/build/qflow/layout"
S="$HERE/build/qflow/synthesis"
[ -f "$L/ecc_fi_ctrl_F_grid.gds" ] || { echo "run run_flow.sh first ($L/ecc_fi_ctrl_F_grid.gds missing)"; exit 1; }
mkdir -p "$HERE/macro"
gzip -9 -n -c "$L/ecc_fi_ctrl_F_grid.gds" > "$HERE/macro/ecc_fi_ctrl.gds.gz"
cp "$S/ecc_fi_ctrl.rtlnopwr.v" "$HERE/macro/ecc_fi_ctrl.v"
sed -n '/^\.subckt ecc_fi_ctrl /,$p' "$S/ecc_fi_ctrl.spc" > "$HERE/macro/ecc_fi_ctrl.spc"
{
  echo '# ecc_fi_ctrl pins: name layer x1 y1 x2 y2 (um, coordinates of GDS cell ecc_fi_ctrl_F before the 0.01 um snap; flabels of qflow layout/ecc_fi_ctrl.mag scaled by its magscale)'
  # unit = 0.3 um x magscale ratio ("magscale 1 2" -> 0.15 um, "magscale 1 4" -> 0.075 um)
  awk 'NR==1{u=0.3} $1=="magscale"{u=0.3*$2/$3} $1=="flabel"{o=($3=="s")?1:0; printf "%s %s %.3f %.3f %.3f %.3f\n", $(NF), $2, $(3+o)*u, $(4+o)*u, $(5+o)*u, $(6+o)*u}' \
    "$L/ecc_fi_ctrl.mag" | sort -k1,1V
} > "$HERE/macro/ecc_fi_ctrl_pins.txt"
echo "macro: $(ls -l "$HERE/macro/ecc_fi_ctrl.gds.gz" | awk '{print $5}') bytes, $(($(wc -l < "$HERE/macro/ecc_fi_ctrl_pins.txt") - 1)) pins, $(grep -c '^X' "$HERE/macro/ecc_fi_ctrl.spc") cells"
