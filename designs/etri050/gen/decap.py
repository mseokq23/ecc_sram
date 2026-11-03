#!/usr/bin/env python3
"""On-chip decoupling for the array supplies: NMOS gate-oxide capacitors, gate = the supply, source, drain and
substrate = VSS (drawn by Magic, like gen/sram8t.py).

  python3 designs/etri050/gen/decap.py --check                      # decap_vddw and decap_vdda
  python3 designs/etri050/gen/decap.py --name decap_x --net X --rows 4 --fingers 3 --check

Both supplies reach the core through the series resistor of a PANA pad (PADR), so the charge the bit line
drivers draw on a write comes from here: about 0.1 pF of bit line per column, 8 columns, 0.5 pC each at 5 V.
Tox 110 A gives 3.1 fF/um2; a finger is a 12 x 12 um gate (0.45 pF in inversion, above about 1 V).

Row (lambda, from its bottom): VSS rail 0-7 with p+ taps | n+ strip 13-53 (finger W 40) with VSS contact
columns every 50 (6 wide) and gates 40 long between them | poly bar 55-65 joining the gates, poly contacts
at the gate centres | supply rail (metal1) 56-64. Rows repeat every 68. The VSS rails meet a metal2 bus on
the left, the supply rails one on the right (pins at the bottom of both).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sram8t as s8  # noqa: E402

PITCH_F, GATE_L, GATE_W, ROW = 50, 40, 40, 68
CAP_PER_FINGER_PF = (GATE_L * 0.3) * (GATE_W * 0.3) * 3.14e-3


def decap_layout(name, net, rows, fingers) -> s8.Layout:
    lay = s8.Layout(name)
    r = lay.r
    x1 = fingers * PITCH_F + 6                       # right end of the strip (last contact column)
    bl, br = -26, x1 + 14                            # left (VSS) and right (supply) metal2 buses
    for k in range(rows):
        y = k * ROW
        r("VSS", "metal1", bl, y, x1, y + 7)
        r("VSS", "metal1", bl, y - 0.5, bl + 12, y + 7.5)
        r("VSS", "m2contact", bl + 2.5, y, bl + 9.5, y + 7)
        r(None, "ndiffusion", 0, y + 13, x1, y + 53)
        for f in range(fingers + 1):
            x = f * PITCH_F
            r("VSS", "ndcontact", x, y + 13, x + 6, y + 53)
            r("VSS", "metal1", x, y + 7, x + 6, y + 13)
            if f % 3 == 0:
                r("VSS", "psubstratepcontact", x, y, x + 6, y + 6)
        for f in range(fingers):
            xg = f * PITCH_F + 8
            r(net, "polysilicon", xg, y + 11, xg + GATE_L, y + 57)
        r(net, "polysilicon", 8, y + 55, x1 - 8, y + 65)
        for f in range(fingers):
            xc = f * PITCH_F + 8 + GATE_L // 2
            r(net, "polycontact", xc - 3, y + 57, xc + 3, y + 63)
        r(net, "metal1", 8, y + 56, br + 12, y + 64)
        r(net, "m2contact", br + 2.5, y + 56.5, br + 9.5, y + 63.5)
    top = (rows - 1) * ROW + 65
    r("VSS", "metal2", bl, -6, bl + 12, top)
    r(net, "metal2", br, -6, br + 12, top)
    lay.port("VSS", "metal2", bl, -6, bl + 12, -3)
    lay.port(net, "metal2", br, -6, br + 12, -3)
    return lay


def decap_netlist(name, net, rows, fingers) -> str:
    w = l = GATE_L * 0.3
    body = [f"Mc{k}_{f} VSS {net} VSS VSS nfet W={w:g}u L={l:g}u" for k in range(rows) for f in range(fingers)]
    return f".subckt {name} {net} VSS\n" + "\n".join(body) + "\n.ends\n"


DEFAULT = [("decap_vddw", "VDDW", 14, 9), ("decap_vdda", "VDDA", 7, 9)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--name")
    ap.add_argument("--net")
    ap.add_argument("--rows", type=int)
    ap.add_argument("--fingers", type=int)
    ap.add_argument("--out", type=Path, default=s8.OUT)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    jobs = [(a.name, a.net, a.rows, a.fingers)] if a.name else DEFAULT
    ok = True
    for name, net, rows, fingers in jobs:
        print(f"{name}: {rows} x {fingers} fingers, {rows * fingers * CAP_PER_FINGER_PF:.1f} pF (gate oxide)")
        ok &= s8.build(decap_layout(name, net, rows, fingers), decap_netlist(name, net, rows, fingers), a.out, a.check)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
