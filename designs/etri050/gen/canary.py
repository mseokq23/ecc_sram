#!/usr/bin/env python3
"""Canary block of the reliability monitor: eight latches on the array supply VDDA that lose their set state
at graded voltages above the 8T cells' retention voltage (retention early warning), with read-out gates.

Canary k (k = 0 .. 7, CAN[0] has the lowest threshold):
  latch, VDDA   CINV_k: P1 (W 1.8 um, L = LADDER[k][0]) from VDDA, N1 (W = LADDER[k][1], L 0.6 um) to VSS,
                input B_k, output A_k. A weak PMOS against the off-state leakage of a wide short NMOS.
                XL_k: kit NOR2X1, A = A_k, B = CSET, Y = B_k: the latch's other inverter and its set
                (CSET = 1 forces B_k = 0, so A_k goes to VDDA: the set state A = 1, B = 0).
  read-out, VDD XR_k: kit NOR2X1, A = A_k, B = CRD_N, Y = CAN_k. CAN_k = not A_k while CRD_N = 0 (canary
                view), 0 otherwise; with CRD_N = 1 its series PMOS is off, so no current flows while A_k sits
                between 0.7 V and VDD (VDDA lowered).
After a set at 5 V, lowering VDDA below the canary's retention voltage lets P1's subthreshold current lose
against N1's leakage: A_k falls and the latch keeps the other state when VDDA comes back (CAN_k = 1).
sim/cell/canary_sim.py simulates these sizes.

Layout (lambda = 0.3 um, block origin = lower left): two standard-cell rows sharing their gnd rail (y 120):
  row 0 (flipped)  read-out gates XR_k; VDD rail at y 0 (bottom), N-well at the bottom
  row 1 (normal)   latches: CINV_k and XL_k side by side, XL_k over XR_k; VDDA rail at y 240 (top), N-well at
                   the top
The two N-wells (VDDA, VDD) are 134 lambda apart (rule 1.NWL.S.2: 4.0 um for different potentials).
CINV_k is drawn here (rectangles), in the frame of a kit cell: rails, taps, well, metal2 pins with a via1 pad.
Wiring: metal3 tracks over each row, metal2 stubs to the pins (gen/stdrow.py); A_k crosses the shared gnd rail
in metal2 from XR_k's A pin to XL_k's A pin (the two cells stand one above the other). CAN_k leaves through a
metal2 line down to the block's bottom edge; CSET and CRD_N run on a track each along their row to a channel line
at the west end that leaves the bottom edge too. Supplies, all with ports on the bottom edge: VDD on its rail
(row 0, bottom), VSS and VDDA through metal2 straps at the west end with a via1 on their rails (the shared gnd
rail at y 120, the VDDA rail at y 240).

usage: python3 designs/etri050/gen/canary.py [--check] [--netlist-only]
       -> designs/etri050/monitor/build/canary.mag, canary_flat.gds, sch/canary.spice, canary_pins.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stdrow as sr  # noqa: E402
from stdrow import Block, CELL_W, LAMBDA_UM, REPO, STUB_X, etri_check  # noqa: E402

NAME = "canary"
DEFAULT_OUT = REPO / "designs/etri050/monitor/build"

# ---- circuit (um) ------------------------------------------------------------------------------------
LADDER = [(2.4, 3.6), (4.8, 3.6), (4.8, 6.0), (9.6, 6.0), (9.6, 9.0), (14.4, 9.0), (19.2, 12.0), (30.0, 18.0)]
N = len(LADDER)
P1_W, N1_L = 1.8, 0.6
NOR_P, NOR_N = (12.0, 0.6), (3.0, 0.6)          # kit NOR2X1 (khu_etri050_stdcells.spice)


def sizes(k):
    l1, w1 = LADDER[k]
    return dict(P1=(P1_W, l1), N1=(w1, N1_L), NP=NOR_P, NN=NOR_N)


def devices(a, b, can, mid_l, mid_r, cset, crdn, vdd, vdda, vss):
    """Transistors of one canary as drawn (CINV + the two NOR2X1 expanded as in the kit netlist):
    {name: (drain, gate, source, bulk, 'p' | 'n', size key)}."""
    return {
        "p1": (a, b, vdda, vdda, "p", "P1"), "n1": (a, b, vss, vss, "n", "N1"),
        # latch NOR2X1: series PMOS (A at the supply side), parallel NMOS
        "lpa": (mid_l, a, vdda, vdda, "p", "NP"), "lpb": (b, cset, mid_l, vdda, "p", "NP"),
        "lna": (b, a, vss, vss, "n", "NN"), "lnb": (b, cset, vss, vss, "n", "NN"),
        # read-out NOR2X1 in the VDD domain
        "rpa": (mid_r, a, vdd, vdd, "p", "NP"), "rpb": (can, crdn, mid_r, vdd, "p", "NP"),
        "rna": (can, a, vss, vss, "n", "NN"), "rnb": (can, crdn, vss, vss, "n", "NN"),
    }


# ---- CINV, the skewed inverter, in a kit-cell frame (lambda, normal orientation) ------------------------
# N1 as one or two fingers (W <= 9 um: one), output A on the west contact of both devices so that one metal1
# column joins them; P1's gate runs east from the shared gate line over the P diffusion (length L).
NY0 = 8                       # N diffusion bottom
PY0, PW = 93, 6               # P diffusion bottom and width (P1 W = 1.8 um)
X_OUT = (2, 8)                # output contact column (A) in both devices
X_GATE = (10, 12)             # gate line (input B)
PIN_A = (14, 44, 21, 51)      # input pin (B): via1 tile, metal2 square above it ... see cinv_shapes()
DX = 2                        # the drawing below starts 2 lambda into the cell (diffusion spacing to the
                              # neighbour cells' diffusion, Magic: 6 lambda)
CINV_STUB = {"A": DX + 17.0, "Y": DX + 5.0}


def input_y(k):
    """Bottom of the input poly contact: 4 lambda over the poly bar of a two-finger N1 (Magic 5.5.b)."""
    nf, wf, _, _ = cinv_geom(k)
    return 44 if nf == 1 else max(44, NY0 + wf + 4 + 4)


def cinv_pins(k):
    """Metal2 pin + via1 pad of CINV_k (lambda, cell coordinates): input A (net B_k), output Y (net A_k)."""
    yc = input_y(k)
    return {"A": (DX + 13.5, yc + 7.5, DX + 20.5, yc + 21.5), "Y": (DX + 1.5, 51.5, DX + 8.5, 65.5)}


def lam(v_um):
    n = round(v_um / LAMBDA_UM)
    if abs(n * LAMBDA_UM - v_um) > 1e-6:
        raise ValueError(f"{v_um} um is not on the lambda grid")
    return n


def cinv_geom(k):
    """Finger count, finger width, P1 length (lambda) and the cell width of CINV_k."""
    l1, w1 = LADDER[k]
    wl = lam(w1)
    nf = 1 if wl <= 30 else 2
    if wl % nf:
        raise ValueError(f"N1 width {w1} um does not split into {nf} fingers")
    l1l = lam(l1)
    width = DX + max(20 if nf == 1 else 32, l1l + 18) + 4    # diffusion 6 lambda from the neighbours'
    width += width % 2
    return nf, wl // nf, l1l, width


def cinv_shapes(k, x0, y0, a_net, b_net, vdda="VDDA", vss="VSS"):
    """Rectangles (net, layer, x0, y0, x1, y1) of CINV_k with its lower left at (x0, y0), normal orientation
    (gnd rail at the bottom, the supply rail on top), with its own rail taps and N-well like a kit cell."""
    nf, wf, l1, width = cinv_geom(k)
    S = []

    def r(net, layer, a, b, c, d):
        S.append((net, layer, x0 + DX + a, y0 + b, x0 + DX + c, y0 + d))
    ny1 = NY0 + wf
    # N1: [A | g | VSS] or [A | g | VSS | g | A]
    xs = [X_OUT[0]]
    r(None, "ndiffusion", X_OUT[0], NY0, X_OUT[0] + (20 if nf == 1 else 32) - 2, ny1)
    r(a_net, "ndcontact", 2, NY0, 8, ny1)
    r(vss, "ndcontact", 14, NY0, 20, ny1)
    r(vss, "metal1", 14, 4, 20, NY0)                    # source to the gnd rail (rail y -4..4)
    r(b_net, "polysilicon", 10, NY0 - 2, 12, ny1 + 2)
    if nf == 2:
        r(a_net, "ndcontact", 26, NY0, 32, ny1)
        r(b_net, "polysilicon", 22, NY0 - 2, 24, ny1 + 2)
        r(b_net, "polysilicon", 10, ny1 + 2, 24, ny1 + 4)            # joins the two gates over the strip
        r(a_net, "metal1", 26, ny1, 32, 88)                            # second A contact: column up and a
        r(a_net, "metal1", 2, 84, 32, 88)                              # bar to the output column under P1
    # P1: [A | gate (L) | VDDA]
    px1 = 10 + l1 + 2 + 6
    r(None, "pdiffusion", 2, PY0, px1, PY0 + PW)
    r(a_net, "pdcontact", 2, PY0, 8, PY0 + PW)
    r(vdda, "pdcontact", px1 - 6, PY0, px1, PY0 + PW)
    r(vdda, "metal1", px1 - 6, PY0 + PW, px1, 116)      # source to the vdd rail (rail y 116..124)
    r(b_net, "polysilicon", 10, PY0 - 2, 10 + l1, PY0 + PW + 2)
    # gate line from the N gate to P1's gate
    r(b_net, "polysilicon", 10, ny1 + 2, 12, PY0 - 2)
    # output column: N contact up to P contact
    r(a_net, "metal1", 2, ny1, 8, PY0)
    # input: poly stub east of the gate line, poly contact, via1 and the metal2 pin over it
    yc = input_y(k)
    r(b_net, "polysilicon", 10, yc, 21, yc + 6)
    r(b_net, "polycontact", 14, yc, 20, yc + 6)
    r(b_net, "metal1", 13, yc - 1, 21, yc + 15)
    r(b_net, "m2contact", 13.5, yc + 7.5, 20.5, yc + 14.5)
    r(b_net, "metal2", 13.5, yc + 7.5, 20.5, yc + 21.5)
    # output pin: via1 on the output column, metal2 above it
    r(a_net, "metal1", 1, 50.5, 9, 59.5)
    r(a_net, "m2contact", 1.5, 51.5, 8.5, 58.5)
    r(a_net, "metal2", 1.5, 51.5, 8.5, 65.5)
    # rail taps and N-well as in a kit cell (rails themselves: the block)
    r(vss, "psubstratepcontact", 0, -3, width, 3)
    r(vdda, "nsubstratencontact", 0, 117, width, 123)
    r(None, "nwell", -6, 67, width + 6, 126)
    return S, width


def netlist(with_cells: bool = True) -> str:
    """Schematic netlist of the block, written from the circuit above (not from the drawing): CINV as two
    transistors, the NOR gates as kit cells."""
    ports = ["CSET", "CRD_N"] + [f"CAN{k}" for k in range(N)] + ["VDD", "VDDA", "VSS"]
    out = [f"* {NAME}: {N} canary latches on VDDA with read-out gates (see gen/canary.py)"]
    if with_cells:
        out.append(sr.kit_stdcells_spice(("NOR2X1",)))
    out.append(f".subckt {NAME} " + " ".join(ports))
    for k in range(N):
        s = sizes(k)
        a, b = f"A{k}", f"B{k}"
        out.append(f"Mp1_{k} {a} {b} VDDA VDDA pfet W={s['P1'][0]:g}u L={s['P1'][1]:g}u")
        nf = cinv_geom(k)[0]
        for f in range(nf):                     # drawn as nf fingers (Netgen compares per device)
            out.append(f"Mn1_{k}_{f} {a} {b} VSS VSS nfet W={s['N1'][0] / nf:g}u L={s['N1'][1]:g}u")
        out.append(f"XL{k} {a} CSET {b} VDDA VSS NOR2X1")
        out.append(f"XR{k} {a} CRD_N CAN{k} VDD VSS NOR2X1")
    out.append(".ends")
    return "\n".join(out) + "\n"


# ---- block layout ------------------------------------------------------------------------------------
ROW_H = sr.ROW_H
X0 = 72                                    # first column
X_VDDA = (20, 30)                          # metal2 strap, via1 on the VDDA rail (y 240), port at the bottom
X_VSS = (34, 44)                           # metal2 strap, via1 on the shared gnd rail (y 120)
X_CRD = (50, 54)                           # CRD_N line (row 0 track -> bottom edge)
X_CSET = (60, 64)                          # CSET line (row 1 track -> bottom edge)
PORT_Y = -10
TRACKS_N = [77, 86, 95, 104, 113]          # over a normal row's pins
TRACKS_F = [42, 33, 24, 15, 6]             # under a flipped row's pins
NOR_STUB = STUB_X["NOR2X1"]


def place(blk):
    """Columns from X0: CINV_k then XL_k in row 1, XR_k under XL_k in row 0. Returns column records."""
    cols = []
    x = X0
    for k in range(N):
        a, b = f"A{k}", f"B{k}"
        shapes, w = cinv_shapes(k, x, ROW_H, a, b)
        for net, layer, x0_, y0_, x1_, y1_ in shapes:
            if layer in ("metal1", "metal2", "m2contact"):
                blk.r(net, layer, x0_, y0_, x1_, y1_)
            else:
                blk.paint(layer, x0_, y0_, x1_, y1_)
        cp = {pin: (x + p[0], ROW_H + p[1], x + p[2], ROW_H + p[3]) for pin, p in cinv_pins(k).items()}
        for pin, net in (("Y", a), ("A", b)):
            blk.pinrects.append((net, "metal2", *cp[pin]))
        xl = x + w
        pl = blk.cell("NOR2X1", xl, ROW_H, False, f"XL{k}")
        pr = blk.cell("NOR2X1", xl, 0, True, f"XR{k}")
        for pins, nets in ((pl, {"A": a, "B": "CSET", "Y": b}), (pr, {"A": a, "B": "CRD_N", "Y": f"CAN{k}"})):
            for pin, rect in pins.items():
                blk.pinrects.append((nets[pin], "metal2", *rect))
        cols.append(dict(k=k, x=x, w=w, xl=xl, cinv_pins=cp, pl=pl, pr=pr))
        x = xl + CELL_W["NOR2X1"]
    return cols, x


def track(blk, net, x_lo, x_hi, ty):
    blk.r(net, "metal3", x_lo - 3.5, ty, x_hi + 3.5, ty + 4)


def stub_up(blk, net, xc, pin_top, ty):
    blk.r(net, "metal2", xc - 2, pin_top - 1, xc + 2, ty + 2)
    blk.via2(net, xc, ty + 2)


def stub_down(blk, net, xc, pin_bot, ty):
    blk.r(net, "metal2", xc - 2, ty + 2, xc + 2, pin_bot + 1)
    blk.via2(net, xc, ty + 2)


def route(blk, cols, x_end):
    # row 1 (latches): CSET on track 0 over the whole row, A_k on track 1, B_k on track 2
    t_cset, t_a, t_b = (ROW_H + TRACKS_N[i] for i in (0, 1, 2))
    xs = [c["xl"] + NOR_STUB["B"] for c in cols]
    track(blk, "CSET", (X_CSET[0] + X_CSET[1]) / 2, max(xs), t_cset)
    blk.via2("CSET", (X_CSET[0] + X_CSET[1]) / 2, t_cset + 2)
    blk.r("CSET", "metal2", X_CSET[0], PORT_Y, X_CSET[1], t_cset + 5.5)
    blk.port("CSET", "metal2", X_CSET[0], PORT_Y, X_CSET[1], PORT_Y + 4)
    for c in cols:
        k, x, xl = c["k"], c["x"], c["xl"]
        a, b = f"A{k}", f"B{k}"
        top = lambda rect: rect[3]
        stub_up(blk, "CSET", xl + NOR_STUB["B"], top(c["pl"]["B"]), t_cset)
        xa1, xa2 = x + CINV_STUB["Y"], xl + NOR_STUB["A"]
        track(blk, a, xa1, xa2, t_a)
        stub_up(blk, a, xa1, top(c["cinv_pins"]["Y"]), t_a)
        stub_up(blk, a, xa2, top(c["pl"]["A"]), t_a)
        xb1, xb2 = x + CINV_STUB["A"], xl + NOR_STUB["Y"]
        track(blk, b, xb1, xb2, t_b)
        stub_up(blk, b, xb1, top(c["cinv_pins"]["A"]), t_b)
        stub_up(blk, b, xb2, top(c["pl"]["Y"]), t_b)
        # A_k down across the shared gnd rail into the read-out gate's A pin (same x)
        blk.r(a, "metal2", xa2 - 2, c["pr"]["A"][3] - 1, xa2 + 2, c["pl"]["A"][1] + 1)
        # CAN_k: metal2 from the read-out gate's Y pin straight down to the bottom edge
        xc = xl + NOR_STUB["Y"]
        blk.r(f"CAN{k}", "metal2", xc - 2, PORT_Y, xc + 2, c["pr"]["Y"][1] + 1)
        blk.port(f"CAN{k}", "metal2", xc - 2, PORT_Y, xc + 2, PORT_Y + 4)
    # row 0 (read-out): CRD_N on the track nearest the pins
    t_crd = TRACKS_F[0]
    xs = [c["xl"] + NOR_STUB["B"] for c in cols]
    track(blk, "CRD_N", (X_CRD[0] + X_CRD[1]) / 2, max(xs), t_crd)
    blk.via2("CRD_N", (X_CRD[0] + X_CRD[1]) / 2, t_crd + 2)
    blk.r("CRD_N", "metal2", X_CRD[0], PORT_Y, X_CRD[1], t_crd + 5.5)
    blk.port("CRD_N", "metal2", X_CRD[0], PORT_Y, X_CRD[1], PORT_Y + 4)
    for c in cols:
        stub_down(blk, "CRD_N", c["xl"] + NOR_STUB["B"], c["pr"]["B"][1], t_crd)


def power(blk, x_end):
    rail_x1 = x_end + 4
    blk.r("VDD", "metal1", 4, -4, rail_x1, 4)                       # row 0 supply rail (bottom)
    blk.r("VSS", "metal1", X_VSS[0] - 2, ROW_H - 4, rail_x1, ROW_H + 4)   # shared gnd rail
    blk.r("VDDA", "metal1", 4, 2 * ROW_H - 4, rail_x1, 2 * ROW_H + 4)      # row 1 supply rail (top)
    blk.via1("VSS", (X_VSS[0] + X_VSS[1]) / 2, ROW_H)
    blk.r("VSS", "metal2", X_VSS[0], PORT_Y, X_VSS[1], ROW_H + 4)
    blk.port("VSS", "metal2", X_VSS[0], PORT_Y, X_VSS[1], PORT_Y + 4)
    blk.via1("VDDA", (X_VDDA[0] + X_VDDA[1]) / 2, 2 * ROW_H)
    blk.r("VDDA", "metal2", X_VDDA[0], PORT_Y, X_VDDA[1], 2 * ROW_H + 4)
    blk.port("VDDA", "metal2", X_VDDA[0], PORT_Y, X_VDDA[1], PORT_Y + 4)
    blk.port("VDD", "metal1", 4, -4, 16, 4)


def build():
    blk = Block(NAME)
    cols, x_end = place(blk)
    power(blk, x_end)
    route(blk, cols, x_end)
    return blk, dict(cols=cols, x_end=x_end)


def pins_json(blk, info):
    um = lambda v: round(v * LAMBDA_UM, 3)
    pins = {name: {"layer": layer, "box": [um(x0), um(y0), um(x1), um(y1)]}
            for name, layer, x0, y0, x1, y1 in blk.ports}
    x0, y0, x1, y1 = blk.bbox()
    return {"cell": NAME, "unit": "um, block coordinates (origin: lower left)",
            "bbox": [um(x0), um(y0), um(x1), um(y1)], "pins": pins,
            "ladder_um": LADDER, "rails": {"VDD": [um(-4), um(4)], "VSS": [um(116), um(124)],
                                           "VDDA": [um(236), um(244)]}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--netlist-only", action="store_true")
    ap.add_argument("--sizes", action="store_true")
    args = ap.parse_args(argv)
    if args.sizes:
        for k in range(N):
            print(k, sizes(k), cinv_geom(k))
        return 0
    out = args.out
    (out / "sch").mkdir(parents=True, exist_ok=True)
    (out / "sch" / f"{NAME}.spice").write_text(netlist())
    if args.netlist_only:
        return 0
    blk, info = build()
    errs = sr.spacing_errors(blk)
    for m, a, b in errs[:30]:
        print(f"  spacing {m}: {a} -- {b}")
    if errs:
        sys.exit(f"{len(errs)} spacing errors in the routing")
    sr.write_flat_gds(blk, out)
    (out / f"{NAME}_pins.json").write_text(json.dumps(pins_json(blk, info), indent=1))
    x0, y0, x1, y1 = blk.bbox()
    print(f"{NAME}: {(x1 - x0) * LAMBDA_UM:.1f} x {(y1 - y0) * LAMBDA_UM:.1f} um, {len(blk.rects)} rectangles, "
          f"{len(blk.cells)} standard cells, {len(blk.ports)} ports; columns end at x {info['x_end']}")
    if args.check:
        n, why = sr.flat_drc(out, NAME)
        print(f"  Magic DRC, flattened: {n}" + "".join(f"\n    {w}" for w in why))
        ok, line = etri_check(NAME, str(out / "sch" / f"{NAME}.spice"), out)
        print("  " + line + "   (hierarchical Magic DRC counts the kit cells' abutting rails)")
        return 0 if (ok or "LVS MATCH" in line) and n == 0 else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
