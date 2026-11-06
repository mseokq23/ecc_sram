#!/usr/bin/env python3
"""Ring-oscillator bank of the reliability monitor: INV, NAND and NOR rings for the process corner.

Every ring has 31 stages. Stage 0 is NAND2X1(A = stage 30, B = en<i>): a stopped ring holds a known state
(its tap at 1) and starts in its fundamental mode. A tap INVX1 -> INVX4 on stage 0's output drives in<i>
(to the divider block ro_div: the AND of the three taps divided by 256 goes to the control block).

  index 0  inv   stages 1-30 INVX1                 overall speed (SS / FF)
  index 1  nand  stages 1-30 NAND2X1, B = en1      two NMOS in series pull down: NMOS-weighted
  index 2  nor   stages 1-30 NOR2X1, B = not en2   two PMOS in series pull up: PMOS-weighted
While a ring runs, its B inputs sit at VDD (NAND) or VSS (NOR) as in the pdkv chip, where they were tied to
the supplies; here they come from the enable (NOR: through an INVX1, XE2) so that no gate hangs on VDD or VSS
(the antenna rules of the rule document v1.1 divide a net's metal by its gate area, and the supply nets carry
the most metal of the chip). A stopped NAND / NOR ring holds every stage (outputs 1 / 0).
The NAND / NOR frequency ratio moves with the N/P skew (SF, FS) and hardly with SS / FF, the INV ring with
SS / FF: together the three place a die on the corner map. The rings run only one at a time and only in the
ring-oscillator view of the control block (RO_EN).

The layout is the RO bank of the earlier pdkv chip (repository mychip, gen/etri050_ro.py) without its wire
and resistor rings: the same cells, order, folding and wiring, so the drawn wiring per stage is the same. The
B inputs' row tracks end on a metal2 line at the west edge (en1 rows 1-2, enb2 rows 3-4) instead of the
supply straps, and XE2 sits east of the NOR ring's taps.

Layout (lambda = 0.3 um, block origin = lower left): five standard-cell rows of 120 lambda, odd rows flipped
so that neighbours share a rail (gnd at y 0, 240, 480; vdd at 120, 360, 600):
  row 0     inv ring, interleaved (S15 S16 S14 ... S1 S30 S0 from the west): connections span <= 2 cells
  rows 1-2  nand ring folded: S15..S0 in row 1, S16..S30 above them in row 2; the turn (S15 -> S16,
            west end) and the closure (S30 -> S0, east end) cross the shared gnd rail in metal2
  rows 3-4  nor ring folded the same way
Stage 0 and the tap sit at the east end of each ring, next to the channel. Connections run on metal3 tracks
over the cells with metal2 stubs to the pins (pads 4 lambda clear of the pins, tracks 9 lambda apart).
en<i> and in<i> go to an east channel of six metal2 lines that leave the block's bottom edge. VDD comes up a
metal1 strap at the west edge that joins the vdd rails; VSS joins the gnd rails through a metal2 strap with a
via1 on each (west of the cells: the cells' own rails are tap contacts, no via1 on them). VDD and VSS ports
are at the bottom ends of the two straps.

usage: python3 designs/etri050/gen/robank.py [--check] [--netlist-only]
       -> designs/etri050/monitor/build/robank.mag, robank_flat.gds, sch/robank.spice, robank_pins.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stdrow as sr  # noqa: E402
from stdrow import Block, CELL_W, LAMBDA_UM, PINS, STUB_X, REPO, etri_check  # noqa: E402,F401

NAME = "robank"
DEFAULT_OUT = REPO / "designs/etri050/monitor/build"
W, H = 1160, 656
NST = 31
KINDS = {0: "inv", 1: "nand", 2: "nor"}
STAGE_CELL = {"inv": "INVX1", "nand": "NAND2X1", "nor": "NOR2X1"}
ROWS = 5
X0 = 66                                   # first cell of every row
VDD_STRAP = (4, 26)                       # metal1, west edge: joins the vdd rails, block VDD at its bottom
GND_X0 = 32                               # gnd rails start east of the VDD strap
VSS_STRAP = (34, 44)                      # metal2 over the rails, a via1 on every gnd rail
RAIL_X1 = 1090                            # rails end west of the channel
CHANNEL = ["en0", "en1", "en2", "in0", "in1", "in2"]
CH_X = {n: 1094 + 11 * k for k, n in enumerate(CHANNEL)}    # channel line x0 (4 lambda wide, pads 3.5 clear)
PORT_Y = -10                              # channel lines and the two straps reach down to here
TIE = {"nand": "en1", "nor": "enb2"}      # the B inputs of stages 1-30
TIE_X = (50, 54)                          # metal2 line joining a ring's two B tracks (west edge)
TRACKS_N = [77, 86, 95, 104, 113]         # normal rows: track y over the pins (pin tops <= 68.5)
TRACKS_F = [42, 33, 24, 15, 6]            # flipped rows: track y under the pins (pin bottoms >= 51.5)


def row_y(r):
    return 120 * r


def flipped(r):
    return r % 2 == 1


# ==== circuit =======================================================================================
def stage_nets(i, kind):
    """Instances of ring i: [(inst, cell, {pin: net})], stage outputs r<i>_<s>."""
    n = lambda s: f"r{i}_{s % NST}"
    out = [(f"XS{i}_0", "NAND2X1", {"A": n(NST - 1), "B": f"en{i}", "Y": n(0)})]
    for s in range(1, NST):
        pins = {"A": n(s - 1), "Y": n(s)}
        if kind in TIE:
            pins["B"] = TIE[kind]
        out.append((f"XS{i}_{s}", STAGE_CELL[kind], pins))
    out.append((f"XT{i}a", "INVX1", {"A": n(0), "Y": f"t{i}"}))
    out.append((f"XT{i}b", "INVX4", {"A": f"t{i}", "Y": f"in{i}"}))
    if kind == "nor":
        out.append((f"XE{i}", "INVX1", {"A": f"en{i}", "Y": f"enb{i}"}))
    return out


def netlist(with_cells: bool = True) -> str:
    """Schematic netlist of the block, written from the circuit above (not from the drawing)."""
    ports = CHANNEL + ["VDD", "VSS"]
    out = [f"* {NAME}: ring oscillators {', '.join(f'{i} {k}' for i, k in KINDS.items())} (see gen/robank.py)"]
    if with_cells:
        out.append(sr.kit_stdcells_spice())
    out.append(f".subckt {NAME} " + " ".join(ports))
    for i, kind in KINDS.items():
        for inst, cell, pins in stage_nets(i, kind):
            out.append(f"{inst} " + " ".join(pins[p] for p in sr.PIN_ORDER[cell].split()) + f" VDD VSS {cell}")
    out.append(".ends")
    return "\n".join(out) + "\n"


# ==== placement =====================================================================================
def interleaved(i, kind):
    """Single-row order from the west: S15 S16 S14 S17 ... S1 S30 S0, then the taps."""
    insts = {inst: (cell, pins) for inst, cell, pins in stage_nets(i, kind)}
    order = []
    for k in range(16):
        order.append(f"XS{i}_{k}")
        if k < 15:
            order.append(f"XS{i}_{NST - 1 - k}")
    order = order[::-1] + [f"XT{i}a", f"XT{i}b"]
    return [(inst, *insts[inst]) for inst in order]


def folded(i, kind):
    """Two rows from the west: [S15 .. S0, taps] and [S16 .. S30] above it (S16 over S15, S30 over S1)."""
    insts = {inst: (cell, pins) for inst, cell, pins in stage_nets(i, kind)}
    lower = [f"XS{i}_{s}" for s in range(15, -1, -1)] + [f"XT{i}a", f"XT{i}b"]
    if kind == "nor":
        lower.append(f"XE{i}")
    upper = [f"XS{i}_{s}" for s in range(16, NST)]
    return [(n, *insts[n]) for n in lower], [(n, *insts[n]) for n in upper]


def place_row(blk, r, cells, x_start, where, at=None):
    """Cells side by side from x_start; at = {inst: x} places a cell at a given x instead."""
    x = x_start
    for inst, cell, pins in cells:
        x = (at or {}).get(inst, x)
        p = blk.cell(cell, x, row_y(r), flipped(r), inst)
        where[inst] = dict(cell=cell, x=x, row=r, pins=p, nets=pins)
        for pin, rect in p.items():
            blk.pinrects.append((pins[pin], "metal2", *rect))
        x += CELL_W[cell]
    return x


def placement(blk):
    where, ends = {}, {}
    ends[0] = place_row(blk, 0, interleaved(0, "inv"), X0, where)
    # folded rings: the upper row starts 10 lambda east and S30 sits 10 lambda west of S0, so that the
    # turn (S15 Y -> S16 A) and the closure (S30 Y -> S0 A) are straight metal2 lines across the rail
    for i, r in ((1, 1), (2, 3)):
        lo, up = folded(i, KINDS[i])
        ends[r] = place_row(blk, r, lo, X0, where)
        ends[r + 1] = place_row(blk, r + 1, up, X0 + 10, where, at={f"XS{i}_30": where[f"XS{i}_0"]["x"] - 10})
    for r, e in ends.items():
        if e > RAIL_X1 - 4:
            raise SystemExit(f"row {r} ends at {e}, past the rails ({RAIL_X1})")
    return where, ends


# ==== routing =======================================================================================
def stub(blk, net, w, pin, ty):
    """4 lambda metal2 stub from inside the pin to a via2 on the track at ty; returns the via x."""
    x0, y0, x1, y1 = w["pins"][pin]
    xc = w["x"] + STUB_X[w["cell"]][pin]
    if ty + 2 > y1:
        blk.r(net, "metal2", xc - 2, y1 - 1, xc + 2, ty + 2)
    else:
        blk.r(net, "metal2", xc - 2, ty + 2, xc + 2, y0 + 1)
    blk.via2(net, xc, ty + 2)
    return xc


def cross_rail(blk, net, wa, pa, wb, pb):
    """Net between a pin of a flipped row (wa) and a pin of the normal row above it (wb), across their
    shared gnd rail: metal2 up from wa's pin, along the rail, up into wb's pin (stub-wide, 4 lambda)."""
    ya = wa["pins"][pa][3]
    yb = wb["pins"][pb][1]
    rail = row_y(wb["row"])
    xa = wa["x"] + STUB_X[wa["cell"]][pa]
    xb = wb["x"] + STUB_X[wb["cell"]][pb]
    blk.r(net, "metal2", xa - 2, ya - 1, xa + 2, rail + 2)
    blk.r(net, "metal2", min(xa, xb) - 2, rail - 2, max(xa, xb) + 2, rail + 2)
    blk.r(net, "metal2", xb - 2, rail - 2, xb + 2, yb + 1)


def route(blk, where):
    """Every net: metal3 track(s) in its row(s), or a metal2 crossing for the folded rings' turns."""
    nets = {}
    for inst, w in where.items():
        for pin, net in w["nets"].items():
            nets.setdefault(net, []).append((inst, pin))
    done = set()
    for i in (1, 2):
        for src, dst in ((f"XS{i}_15", f"XS{i}_16"), (f"XS{i}_30", f"XS{i}_0")):
            net = where[src]["nets"]["Y"]
            wa, wb = where[src], where[dst]
            if flipped(wa["row"]):
                cross_rail(blk, net, wa, "Y", wb, "A")
            else:
                cross_rail(blk, net, wb, "A", wa, "Y")
            done.add(net)
    # tracks per row: left-edge assignment. en / in run on to their channel line (en1 from row 1, where
    # stage 0 sits); a ring's B inputs (en1, enb2) take a track in each of its rows, joined at the west edge
    busy = {r: {t: [] for t in range(len(TRACKS_N))} for r in range(ROWS)}
    tracks = {}
    plan = []
    tie_y = {}
    for net, pins in nets.items():
        if net in done:
            continue
        by_row = {}
        for inst, pin in pins:
            by_row.setdefault(where[inst]["row"], []).append((inst, pin))
        if len(by_row) != 1 and net not in TIE.values():
            raise SystemExit(f"net {net} spans rows {sorted(by_row)} without a crossing")
        for r, rp in by_row.items():
            xs = [where[inst]["x"] + STUB_X[where[inst]["cell"]][pin] for inst, pin in rp]
            to_ch = net in CH_X and r == min(by_row)
            if net in TIE.values() and len(by_row) > 1:
                xs.append((TIE_X[0] + TIE_X[1]) / 2)
            if to_ch:
                xs.append(CH_X[net] + 2)
            plan.append((min(xs) - 3.5, max(xs) + 3.5, net, r, rp, to_ch, len(by_row) > 1))
    for lo, hi, net, r, pins, to_ch, tie in sorted(plan, key=lambda p: (p[1] - p[0] < 600, p[0])):
        for t in range(len(TRACKS_N)):
            if all(hi + sr.SP <= a or lo >= b + sr.SP for a, b in busy[r][t]):
                busy[r][t].append((lo, hi))
                tracks[(net, r)] = t
                break
        else:
            raise SystemExit(f"row {r}: no track for {net}")
        ty = row_y(r) + (TRACKS_F if flipped(r) else TRACKS_N)[t]
        blk.r(net, "metal3", lo, ty, hi, ty + 4)
        for inst, pin in pins:
            stub(blk, net, where[inst], pin, ty)
        if tie:
            blk.via2(net, (TIE_X[0] + TIE_X[1]) / 2, ty + 2)
            tie_y.setdefault(net, []).append(ty + 2)
        if to_ch:
            x = CH_X[net]
            blk.via2(net, x + 2, ty + 2)
            blk.r(net, "metal2", x, PORT_Y, x + 4, ty + 5.5)
            blk.port(net, "metal2", x, PORT_Y, x + 4, PORT_Y + 4)
    for net, ys in tie_y.items():                 # the B tracks of a ring's two rows, joined at the west edge
        blk.r(net, "metal2", TIE_X[0], min(ys) - 3.5, TIE_X[1], max(ys) + 3.5)
    return tracks


# ==== power, wells ===================================================================================
def power(blk):
    for r in range(ROWS + 1):
        y = row_y(r)
        if r % 2 == 0:          # gnd rail
            blk.r("VSS", "metal1", GND_X0, y - 4, RAIL_X1, y + 4)
            blk.via1("VSS", (VSS_STRAP[0] + VSS_STRAP[1]) / 2, y)
        else:
            blk.r("VDD", "metal1", VDD_STRAP[0], y - 4, RAIL_X1, y + 4)
    top_vdd = max(row_y(r) for r in range(ROWS + 1) if r % 2 == 1)
    blk.r("VDD", "metal1", VDD_STRAP[0], PORT_Y, VDD_STRAP[1], top_vdd + 4)
    blk.r("VSS", "metal2", VSS_STRAP[0], PORT_Y, VSS_STRAP[1], row_y(ROWS) + 4)
    blk.port("VDD", "metal1", VDD_STRAP[0], PORT_Y, VDD_STRAP[1], PORT_Y + 4)
    blk.port("VSS", "metal2", VSS_STRAP[0], PORT_Y, VSS_STRAP[1], PORT_Y + 4)


def wells(blk, where):
    """One N-well around each vdd rail over the cells of both rows next to it: the wells of a normal cell
    and of the flipped cell above it would otherwise sit closer than the same-potential spacing."""
    for r in range(0, ROWS, 2):
        xs = [(w["x"], w["x"] + CELL_W[w["cell"]]) for w in where.values() if w["row"] in (r, r + 1)]
        y = row_y(r + 1)
        blk.paint("nwell", min(a for a, _ in xs) - 6, y - 53, max(b for _, b in xs) + 6, y + 53)


def build():
    blk = Block(NAME)
    where, ends = placement(blk)
    wells(blk, where)
    power(blk)
    tracks = route(blk, where)
    return blk, dict(where=where, ends=ends, tracks=tracks)


def pins_json(blk):
    um = lambda v: round(v * LAMBDA_UM, 3)
    pins = {name: {"layer": layer, "box": [um(x0), um(y0), um(x1), um(y1)]}
            for name, layer, x0, y0, x1, y1 in blk.ports}
    x0, y0, x1, y1 = blk.bbox()
    return {"cell": NAME, "unit": "um, block coordinates (origin: lower left)", "bbox": [um(x0), um(y0), um(x1), um(y1)],
            "pins": pins, "kinds": {str(i): k for i, k in KINDS.items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--netlist-only", action="store_true")
    args = ap.parse_args(argv)
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
        sys.exit(f"{len(errs)} spacing errors in the added routing")
    x0, y0, x1, y1 = blk.bbox()
    if x0 < 0 or x1 > W or y1 > H or y0 < PORT_Y:
        sys.exit(f"drawing {blk.bbox()} leaves the frame 0..{W} x {PORT_Y}..{H}")
    sr.write_flat_gds(blk, out)
    (out / f"{NAME}_pins.json").write_text(json.dumps(pins_json(blk), indent=1))
    print(f"{NAME}: {(x1 - x0) * LAMBDA_UM:.1f} x {(y1 - y0) * LAMBDA_UM:.1f} um, {len(blk.rects)} rectangles, "
          f"{len(blk.cells)} standard cells, {len(blk.ports)} ports; row ends {info['ends']}")
    if args.check:
        n, why = sr.flat_drc(out, NAME)
        print(f"  Magic DRC, flattened: {n}" + "".join(f"\n    {w}" for w in why))
        ok, line = etri_check(NAME, str(out / "sch" / f"{NAME}.spice"), out)
        print("  " + line + "   (hierarchical Magic DRC counts the kit cells' abutting rails)")
        return 0 if (ok or "LVS MATCH" in line) and n == 0 else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
