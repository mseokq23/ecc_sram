#!/usr/bin/env python3
"""Column circuits under the 8T array, pitch-matched to its 60-lambda columns, and the SRAM macro
(array + column circuits) for DRC, LVS and post-layout simulation.

  python3 designs/etri050/gen/colper.py --check        # sram_macro: Magic DRC, KLayout DRC, LVS

Per column, from the array down (lambda; x from the column's left edge, y from the array's bottom row):

  read part, VDD (y -15 .. -170)
    RBL metal2 jogs from x 38-42 to x 27-31 (y -19..-15)
    VSS rail
    N strip   VSS | g1 | SENSE | g2 | VSS | g3 | SB | g4 | VSS      N 1.8/0.6 per finger
    channel   g1-g2 <- SB (y_a), g3-g4 <- RBL (y_b), vias of SENSE and SB to metal2 (y_c)
    P strip   VDD | g1 | SENSE | g2 | VDD | g3 | SB | g4 | VDD      P 4.5/0.6 per finger
    VDD rail
    P1 strip  VDD | keeper (SB) | RBL | precharge (PRE_N) | VDD     keeper 1.8/1.8, precharge 6.0/0.6
    RBL via (gamma 1), SB -> keeper gate (gamma 2), PRE_N rail
  write part, VDDA (y -184 .. -281)
    VDDA rail
    P strip   VDDA | g1 | BL | g2 | VDDA | g3 | BLB | g4 | VDDA    P 6.0/0.6 per finger
    channel   g1-g2 <- BLB (y_a), BL and BLB vias (y_c), g3-g4 <- WD (y_b)
    N strip   VSS  | g1 | BL | g2 | VSS  | g3 | BLB | g4 | VSS     N 3.0/0.6 per finger
    VSS rail
  pins at the bottom (y -292): SENSE x 13-17, WD x 27-31 (metal2)

So SENSE = not SB = RBL (same polarity as the stored Q), BLB = not WD, BL = not BLB = WD. The g1/g2 and
g3/g4 pairs are two fingers of one inverter. The source contacts on the column edges are shared with
the neighbouring column, so the strips run across all columns. Metal2 tracks per column: BL 1-5,
SENSE 13-17, RBL 27-31 below the jog, SB 38-42, BLB 49-53, WD 27-31 (write part only).
Supplies: VSS and VDDA buses of the array continue down; VDD bus at 42-54 right of the array.
The two N-wells (VDD, VDDA) are 46 lambda (13.8 um) apart, the rule for different potentials is 4.0 um.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sram8t as s8  # noqa: E402

PX = s8.PITCH_X
Y_BOT = -292
BUS = dict(s8.BUS, VDD=(42, 54))

# per-finger sizes (um) as drawn
SZ = dict(SAN=(1.8, 0.6), SAP=(4.5, 0.6), KEEP=(1.8, 1.8), PRE=(6.0, 0.6), WDN=(3.0, 0.6), WDP=(6.0, 0.6))

# strip pattern (x within a column): boundary source, g1, D1, g2, centre source, g3, D2, g4
# g2 sits 5 from D1 and 2 from the centre source, so that the y_a poly contact can enclose it (a poly
# contact must be 4 from other poly edges, Magic 5.5.b) and still keep metal1 3 from the D1 strap
SB_X, G1, D1, G2, SC, G3, D2, G4 = (-3, 3), (6, 8), (12, 18), (23, 25), (27, 33), (36, 38), (42, 48), (51, 53)

# read part
C = dict(jog=(-19, -15), vss=(-28, -21), n=(-40, -34),
         ya_pc=(-49, -43), ya_bar=(-47, -45),
         yb_m1=(-61, -52), yb_via=(-60, -53), yb_pc=(-59, -53), yb_bar=(-57, -55),
         yc_m1=(-73, -64), yc_via=(-72, -65),
         p=(-93, -78), vdd=(-106, -99), nwell=(-138, -66),
         keep=(-118, -112), pre=(-132, -112),
         g1_m1=(-143, -132), g1_via=(-142, -135),
         g2_m1=(-156, -147), g2_via=(-155, -148), g2_pc=(-155, -149),
         pren=(-170, -163), pren_pc=(-169, -163))
# write part
A = dict(nwell=(-226, -184), vdda=(-194, -187), p=(-220, -200),
         ya_pc=(-229, -223), ya_bar=(-227, -225),
         yc_m1=(-242, -233), yc_via=(-241, -234),
         yb_m1=(-255, -246), yb_via=(-254, -247), yb_pc=(-253, -247), yb_bar=(-251, -249),
         n=(-268, -258), vss=(-281, -274))


def draw(lay: s8.Layout, cols: int):
    r = lay.r
    xr = cols * PX
    xl = -9                                   # left end of rails and wells
    # ---------------------------------------------------------------- read part (VDD)
    # strips run across all columns (sources on column edges are shared)
    r(None, "ndiffusion", SB_X[0], C["n"][0], xr + SB_X[1], C["n"][1])
    r(None, "pdiffusion", SB_X[0], C["p"][0], xr + SB_X[1], C["p"][1])
    r(None, "nwell", xl, C["nwell"][0], xr - xl, C["nwell"][1])
    r("VSS", "metal1", xl, C["vss"][0], xr + BUS["VSS"][1] + 1, C["vss"][1])
    r("VDD", "metal1", xl, C["vdd"][0], xr + BUS["VDD"][1] + 1, C["vdd"][1])
    r("PRE_N", "metal1", -20, C["pren"][0], xr - 4, C["pren"][1])
    lay.port("PRE_N", "metal1", -20, C["pren"][0], -16, C["pren"][1])
    for k in range(cols + 1):                 # shared edge sources
        x = k * PX
        r("VSS", "ndcontact", x + SB_X[0], C["n"][0], x + SB_X[1], C["n"][1])
        r("VSS", "metal1", x + SB_X[0], C["n"][1], x + SB_X[1], C["vss"][0])
        r("VDD", "pdcontact", x + SB_X[0], C["p"][0], x + SB_X[1], C["p"][1])
        r("VDD", "metal1", x + SB_X[0], C["vdd"][1], x + SB_X[1], C["p"][0])
    for c in range(cols):
        x = c * PX
        sense, sb, rbl = f"SENSE{c}", f"SB{c}", f"RBL{c}"
        # taps
        r("VSS", "psubstratepcontact", x + 12, C["vss"][0] + 1, x + 18, C["vss"][1])
        r("VDD", "nsubstratencontact", x + 19, C["vdd"][0] + 1, x + 25, C["vdd"][1])
        # centre sources
        r("VSS", "ndcontact", x + SC[0], C["n"][0], x + SC[1], C["n"][1])
        r("VSS", "metal1", x + SC[0], C["n"][1], x + SC[1], C["vss"][0])
        r("VDD", "pdcontact", x + SC[0], C["p"][0], x + SC[1], C["p"][1])
        r("VDD", "metal1", x + SC[0], C["vdd"][1], x + SC[1], C["p"][0])
        # drains and their straps through the channel
        for net, (a, b) in ((sense, D1), (sb, D2)):
            r(net, "ndcontact", x + a, C["n"][0], x + b, C["n"][1])
            r(net, "pdcontact", x + a, C["p"][0], x + b, C["p"][1])
            r(net, "metal1", x + a, C["p"][1], x + b, C["n"][0])
        # gates: g1, g2 (input SB) and g3, g4 (input RBL), N strip to P strip
        for g in (G1, G2, G3, G4):
            r(sb if g in (G1, G2) else rbl, "polysilicon", x + g[0], C["p"][0] - 2, x + g[1], C["n"][1] + 2)
        # y_a: g1-g2 bar -> poly contact -> metal1 to SB strap
        r(sb, "polysilicon", x + G1[0], C["ya_bar"][0], x + 27, C["ya_bar"][1])
        r(sb, "polycontact", x + 21, C["ya_pc"][0], x + 27, C["ya_pc"][1])
        r(sb, "metal1", x + 21, C["ya_pc"][0], x + D2[1], C["ya_pc"][1])
        # y_b: g3-g4 bar -> poly contact -> metal1 -> via1 <- RBL track (27-31)
        r(rbl, "polysilicon", x + 33, C["yb_bar"][0], x + G4[1], C["yb_bar"][1])
        r(rbl, "polycontact", x + 33, C["yb_pc"][0], x + 39, C["yb_pc"][1])
        r(rbl, "metal1", x + 23, C["yb_m1"][0], x + 39, C["yb_m1"][1])
        r(rbl, "m2contact", x + 24, C["yb_via"][0], x + 31, C["yb_via"][1])
        # y_c: SENSE and SB down to metal2
        r(sense, "metal1", x + 11, C["yc_m1"][0], x + 20, C["yc_m1"][1])
        r(sense, "m2contact", x + 12, C["yc_via"][0], x + 19, C["yc_via"][1])
        r(sb, "metal1", x + 37, C["yc_m1"][0], x + D2[1], C["yc_m1"][1])
        r(sb, "m2contact", x + 38, C["yc_via"][0], x + 45, C["yc_via"][1])
        # P1 strip: VDD_a 5-11 | keeper 14-20 (L 6) | RBL 23-29 | precharge 32-34 | VDD_b 37-43
        r(None, "pdiffusion", x + 5, C["keep"][0], x + 23, C["keep"][1])
        r(None, "pdiffusion", x + 23, C["pre"][0], x + 43, C["pre"][1])
        r("VDD", "pdcontact", x + 5, C["keep"][0], x + 11, C["keep"][1])
        r("VDD", "pdcontact", x + 37, C["pre"][0], x + 43, C["pre"][1])
        r("VDD", "metal1", x + 5, C["keep"][1], x + 11, C["vdd"][0])
        r("VDD", "metal1", x + 37, C["pre"][1], x + 43, C["vdd"][0])
        r(rbl, "pdcontact", x + 23, C["pre"][0], x + 29, C["pre"][1])
        r(sb, "polysilicon", x + 14, C["g2_pc"][0], x + 20, C["keep"][1] + 2)
        r("PRE_N", "polysilicon", x + 32, C["pren_pc"][0], x + 34, C["pre"][1] + 2)
        # gamma 1: RBL contact -> via1 on the RBL track
        r(rbl, "metal1", x + 23, C["g1_m1"][0], x + 33, C["g1_m1"][1])
        r(rbl, "m2contact", x + 25, C["g1_via"][0], x + 32, C["g1_via"][1])
        # gamma 2: SB track -> via1 -> metal1 -> keeper gate
        r(sb, "metal1", x + 13, C["g2_m1"][0], x + 46, C["g2_m1"][1])
        r(sb, "m2contact", x + 38, C["g2_via"][0], x + 45, C["g2_via"][1])
        r(sb, "polycontact", x + 14, C["g2_pc"][0], x + 20, C["g2_pc"][0] + 6)
        # PRE_N rail contact
        r("PRE_N", "polycontact", x + 30, C["pren_pc"][0], x + 36, C["pren_pc"][1])
        # metal2: RBL jog and track, SB track, SENSE track to the bottom pin
        r(rbl, "metal2", x + 38, C["jog"][1], x + 42, s8.BOTTOM)
        r(rbl, "metal2", x + 27, C["jog"][0], x + 42, C["jog"][1])
        r(rbl, "metal2", x + 27, C["g1_via"][0], x + 31, C["jog"][0])
        r(sb, "metal2", x + 38, C["g2_via"][0], x + 42, C["yc_via"][1])
        r(sense, "metal2", x + 13, Y_BOT, x + 17, C["yc_via"][1])
        lay.port(sense, "metal2", x + 13, Y_BOT, x + 17, Y_BOT + 3)

    # ---------------------------------------------------------------- write part (VDDA)
    r(None, "pdiffusion", SB_X[0], A["p"][0], xr + SB_X[1], A["p"][1])
    r(None, "ndiffusion", SB_X[0], A["n"][0], xr + SB_X[1], A["n"][1])
    r(None, "nwell", xl, A["nwell"][0], xr - xl, A["nwell"][1])
    r("VDDA", "metal1", xl, A["vdda"][0], xr + BUS["VDDA"][1] + 1, A["vdda"][1])
    r("VSS", "metal1", xl, A["vss"][0], xr + BUS["VSS"][1] + 1, A["vss"][1])
    for k in range(cols + 1):
        x = k * PX
        r("VDDA", "pdcontact", x + SB_X[0], A["p"][0], x + SB_X[1], A["p"][1])
        r("VDDA", "metal1", x + SB_X[0], A["p"][1], x + SB_X[1], A["vdda"][0])
        r("VSS", "ndcontact", x + SB_X[0], A["n"][0], x + SB_X[1], A["n"][1])
        r("VSS", "metal1", x + SB_X[0], A["vss"][1], x + SB_X[1], A["n"][0])
    for c in range(cols):
        x = c * PX
        bl, blb, wd = f"BL{c}", f"BLB{c}", f"WD{c}"
        r("VDDA", "nsubstratencontact", x + 12, A["vdda"][0] + 1, x + 18, A["vdda"][1])
        r("VSS", "psubstratepcontact", x + 12, A["vss"][0] + 1, x + 18, A["vss"][1])
        r("VDDA", "pdcontact", x + SC[0], A["p"][0], x + SC[1], A["p"][1])
        r("VDDA", "metal1", x + SC[0], A["p"][1], x + SC[1], A["vdda"][0])
        r("VSS", "ndcontact", x + SC[0], A["n"][0], x + SC[1], A["n"][1])
        r("VSS", "metal1", x + SC[0], A["vss"][1], x + SC[1], A["n"][0])
        for net, (a, b) in ((bl, D1), (blb, D2)):
            r(net, "pdcontact", x + a, A["p"][0], x + b, A["p"][1])
            r(net, "ndcontact", x + a, A["n"][0], x + b, A["n"][1])
            r(net, "metal1", x + a, A["n"][1], x + b, A["p"][0])
        for g in (G1, G2, G3, G4):
            r(blb if g in (G1, G2) else wd, "polysilicon", x + g[0], A["n"][0] - 2, x + g[1], A["p"][1] + 2)
        # y_a: g1-g2 bar <- BLB strap
        r(blb, "polysilicon", x + G1[0], A["ya_bar"][0], x + 27, A["ya_bar"][1])
        r(blb, "polycontact", x + 21, A["ya_pc"][0], x + 27, A["ya_pc"][1])
        r(blb, "metal1", x + 21, A["ya_pc"][0], x + D2[1], A["ya_pc"][1])
        # y_c: BL and BLB straps -> via1 -> the bit lines from the array
        r(bl, "metal1", x - 1, A["yc_m1"][0], x + D1[1], A["yc_m1"][1])
        r(bl, "m2contact", x + 0, A["yc_via"][0], x + 7, A["yc_via"][1])
        r(blb, "metal1", x + D2[0], A["yc_m1"][0], x + 55, A["yc_m1"][1])
        r(blb, "m2contact", x + 47, A["yc_via"][0], x + 54, A["yc_via"][1])
        r(bl, "metal2", x + 1, A["yc_via"][0], x + 5, s8.BOTTOM)
        r(blb, "metal2", x + 49, A["yc_via"][0], x + 53, s8.BOTTOM)
        # y_b: WD track (27-31, from the bottom pin) -> via1 -> metal1 -> g3-g4 bar
        r(wd, "polysilicon", x + 33, A["yb_bar"][0], x + G4[1], A["yb_bar"][1])
        r(wd, "polycontact", x + 33, A["yb_pc"][0], x + 39, A["yb_pc"][1])
        r(wd, "metal1", x + 23, A["yb_m1"][0], x + 39, A["yb_m1"][1])
        r(wd, "m2contact", x + 24, A["yb_via"][0], x + 31, A["yb_via"][1])
        r(wd, "metal2", x + 27, Y_BOT, x + 31, A["yb_via"][1])
        lay.port(wd, "metal2", x + 27, Y_BOT, x + 31, Y_BOT + 3)

    # ---------------------------------------------------------------- supply buses (right of the array)
    def bus_via(net, ym):
        a, b = BUS[net]
        vx = xr + (a + b) / 2
        r(net, "metal1", xr + a, ym - 4, xr + b + 1, ym + 4)
        r(net, "m2contact", vx - 3.5, ym - 3.5, vx + 3.5, ym + 3.5)
    for net in ("VSS", "VDDA"):
        a, b = BUS[net]
        r(net, "metal2", xr + a, Y_BOT, xr + b, s8.BOTTOM)
    a, b = BUS["VDD"]
    r("VDD", "metal2", xr + a, Y_BOT, xr + b, C["vdd"][1] + 1)
    for net in ("VSS", "VDDA", "VDD"):
        a, b = BUS[net]
        lay.port(net, "metal2", xr + a, Y_BOT, xr + b, Y_BOT + 3)
    bus_via("VSS", sum(C["vss"]) / 2)
    bus_via("VDD", sum(C["vdd"]) / 2)
    bus_via("VDDA", sum(A["vdda"]) / 2)
    bus_via("VSS", sum(A["vss"]) / 2)


def macro_layout(rows=s8.ROWS, cols=s8.COLS, name="sram_macro") -> s8.Layout:
    lay = s8.array_layout(rows, cols, name, bottom_pins=False)
    draw(lay, cols)
    return lay


def periphery_netlist(cols=s8.COLS, model_n="nfet", model_p="pfet") -> str:
    L = []

    def m(n, d, g, s, b, mod, wl):
        L.append(f"M{n} {d} {g} {s} {b} {mod} W={wl[0]:g}u L={wl[1]:g}u")
    for c in range(cols):
        sense, sb, rbl, bl, blb, wd = f"SENSE{c}", f"SB{c}", f"RBL{c}", f"BL{c}", f"BLB{c}", f"WD{c}"
        for f in (1, 2):
            m(f"on{f}_{c}", sense, sb, "VSS", "VSS", model_n, SZ["SAN"])
            m(f"op{f}_{c}", sense, sb, "VDD", "VDD", model_p, SZ["SAP"])
            m(f"sn{f}_{c}", sb, rbl, "VSS", "VSS", model_n, SZ["SAN"])
            m(f"sp{f}_{c}", sb, rbl, "VDD", "VDD", model_p, SZ["SAP"])
            m(f"bln{f}_{c}", bl, blb, "VSS", "VSS", model_n, SZ["WDN"])
            m(f"blp{f}_{c}", bl, blb, "VDDA", "VDDA", model_p, SZ["WDP"])
            m(f"bbn{f}_{c}", blb, wd, "VSS", "VSS", model_n, SZ["WDN"])
            m(f"bbp{f}_{c}", blb, wd, "VDDA", "VDDA", model_p, SZ["WDP"])
        m(f"keep_{c}", rbl, sb, "VDD", "VDD", model_p, SZ["KEEP"])
        m(f"pre_{c}", rbl, "PRE_N", "VDD", "VDD", model_p, SZ["PRE"])
    return "\n".join(L) + "\n"


def macro_netlist(rows=s8.ROWS, cols=s8.COLS, name="sram_macro") -> str:
    ports = ([f"WWL{r}" for r in range(rows)] + [f"RWL{r}" for r in range(rows)]
             + [f"WD{c}" for c in range(cols)] + [f"SENSE{c}" for c in range(cols)]
             + ["PRE_N", "VDD", "VDDA", "VSS"])
    arr = s8.array_netlist(rows, cols, "x").splitlines()[1:-1]       # body of the array subcircuit
    return (f".subckt {name} " + " ".join(ports) + "\n" + "\n".join(arr) + "\n"
            + periphery_netlist(cols) + ".ends\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--rows", type=int, default=s8.ROWS)
    ap.add_argument("--cols", type=int, default=s8.COLS)
    ap.add_argument("--out", type=Path, default=s8.OUT)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    ok = s8.build(macro_layout(a.rows, a.cols), macro_netlist(a.rows, a.cols), a.out, a.check)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
