#!/usr/bin/env python3
"""8T SRAM bit cell and array for the ETRI 0.5 um process, generated from code and drawn by Magic.

Python works out every rectangle on Magic's lambda grid (1 lambda = 0.3 um) and writes a Magic Tcl
script; Magic draws it with the kit technology (cuts, implants and wells come from the ETRI GDS
style), then the same code writes the schematic netlist for LVS.

  python3 designs/etri050/gen/sram8t.py cell --check        # one cell: Magic DRC, KLayout DRC, LVS
  python3 designs/etri050/gen/sram8t.py array --check       # 15 x 8 array (flat), same checks

Cell (lambda, origin = lower-left; rows are mirrored about y = 0 and y = 91 in the array):

  y 88-94  VSS rail (metal1) + p+ tap            <- shared with the mirrored row above
  y 84-86  RWL (poly, runs across the row)
  y 69-79  read strip   VSS | RD1 (gate QB) | RD2 (gate RWL) | RBL     (NMOS 3.0/0.6)
  y 53-60  VDDA rail (metal1) + n+ well tap       (N-well y 38-63, whole row)
  y 44-50  PMOS strip   Q | PU_L (QB) | VDDA | PU_R (Q) | QB         (PMOS 1.8/0.6)
  y 25-41  cross-couple: QB poly contact (y 25-31), Q poly contact (y 35-41)
  y 12-22  NMOS strip   BL | PG_L (WWL) | Q | PD_L (QB) | VSS | PD_R (Q) | QB | PG_R (WWL) | BLB
                        PG 1.8/0.6 (strip 6 tall), PD 3.0/0.6 (strip 10 tall)
  y  5-7   WWL (poly, runs across the row)
  y -3-3   VSS rail (metal1) + p+ tap            <- shared with the mirrored row below

  metal2 (vertical): BL x 1-5 (via x 0-7), RBL x 38-42 (via x 37-44), BLB x 49-53 (via x 47-54)
  cell pitch 60 x 91 lambda = 18.0 x 27.3 um

The read port is gated by QB, so RBL follows Q: a stored 0 discharges RBL, a stored 1 leaves it high.
Magic rules are stricter than the NSPL ones (contact tile 6, diffusion space 6, N/P diffusion 12),
so a layout that passes Magic DRC also clears most official values; metal2 is kept at 4 wide and
>= 4 apart (official 1.0 um), and the cut-to-ACT distance of the poly contacts is 1.5 um (>= 1.0).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

LAMBDA_UM = 0.3
REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "designs/etri050/sram/build"

PITCH_X = 60
PITCH_Y = 91

# device sizes (um) of the drawn cell, used by the netlists
SIZES = dict(PU=(1.8, 0.6), PD=(3.0, 0.6), PG=(1.8, 0.6), RD1=(3.0, 0.6), RD2=(3.0, 0.6))


def um(n: float) -> str:
    return f"{n * LAMBDA_UM:.2f}um"


@dataclass
class Layout:
    """Rectangles in lambda with a net name each (None = device or well shape)."""
    name: str
    rects: list = field(default_factory=list)      # (net, layer, x0, y0, x1, y1)
    ports: list = field(default_factory=list)      # (name, layer, x0, y0, x1, y1)

    def r(self, net, layer, x0, y0, x1, y1):
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        if x1 <= x0 or y1 <= y0:
            raise ValueError(f"empty {layer} rectangle {x0},{y0},{x1},{y1}")
        self.rects.append((net, layer, x0, y0, x1, y1))

    def port(self, name, layer, x0, y0, x1, y1):
        self.ports.append((name, layer, x0, y0, x1, y1))

    def bbox(self):
        xs = [v for r in self.rects for v in (r[2], r[4])]
        ys = [v for r in self.rects for v in (r[3], r[5])]
        return min(xs), min(ys), max(xs), max(ys)

    ORDER = ["nwell", "ndiffusion", "pdiffusion", "polysilicon", "ndcontact", "pdcontact",
             "psubstratepcontact", "nsubstratencontact", "polycontact", "metal1", "metal2",
             "m2contact", "metal3", "m3contact"]

    def magic_tcl(self) -> str:
        out = [f"load {self.name}", "snap internal"]
        for _, lyr, *_ in self.rects:
            if lyr not in self.ORDER:
                raise ValueError(f"unknown layer {lyr}")
        for layer in self.ORDER:     # contacts after plain layers, so a contact is never overwritten
            for _, lyr, x0, y0, x1, y1 in self.rects:
                if lyr == layer:
                    out += [f"box {um(x0)} {um(y0)} {um(x1)} {um(y1)}", f"paint {layer}"]
        for name, layer, x0, y0, x1, y1 in self.ports:
            out += [f"box {um(x0)} {um(y0)} {um(x1)} {um(y1)}", f"label {name} c {layer}"]
        bx0, by0, bx1, by1 = self.bbox()
        out += [f"box {um(bx0 - 1)} {um(by0 - 1)} {um(bx1 + 1)} {um(by1 + 1)}", "port makeall",
                f"save {self.name}"]
        return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------------------------
# the bit cell in its own coordinates (lambda). Shapes on the mirror lines (rails, taps) are drawn
# whole; in the array the two rows draw the same rectangle, which merges.
def cell_shapes(bl="BL", blb="BLB", rbl="RBL", wwl="WWL", rwl="RWL", q="Q", qb="QB",
                vdda="VDDA", vss="VSS", width=PITCH_X):
    S = []

    def r(net, layer, x0, y0, x1, y1):
        S.append((net, layer, x0, y0, x1, y1))

    # rails, taps, well (full cell width so that neighbours merge)
    r(vss, "metal1", 0, -3, width, 3)
    r(vss, "psubstratepcontact", 24, -3, 30, 3)
    r(vss, "metal1", 0, 88, width, 94)
    r(vss, "psubstratepcontact", 12, 88, 18, 94)
    r(None, "nwell", 0, 38, width, 63)
    r(vdda, "metal1", 0, 53, width, 60)
    r(vdda, "nsubstratencontact", 24, 54, 30, 60)

    # word lines (poly across the cell)
    r(wwl, "polysilicon", 0, 5, width, 7)
    r(rwl, "polysilicon", 0, 84, width, 86)

    # NMOS strip: BL | PG_L | Q | PD_L | VSS | PD_R | QB | PG_R | BLB
    r(None, "ndiffusion", 0, 12, 54, 18)          # PG parts, 6 tall (W 1.8 um)
    r(None, "ndiffusion", 12, 12, 42, 22)         # PD part, 10 tall (W 3.0 um)
    r(bl, "ndcontact", 0, 12, 6, 18)
    r(q, "ndcontact", 12, 12, 18, 22)
    r(vss, "ndcontact", 24, 12, 30, 22)
    r(qb, "ndcontact", 36, 12, 42, 22)
    r(blb, "ndcontact", 48, 12, 54, 18)
    r(wwl, "polysilicon", 8, 5, 10, 20)           # PG_L gate, joined to WWL below
    r(wwl, "polysilicon", 44, 5, 46, 20)          # PG_R gate
    # PMOS strip: Q | PU_L | VDDA | PU_R | QB
    r(None, "pdiffusion", 12, 44, 42, 50)
    r(q, "pdcontact", 12, 44, 18, 50)
    r(vdda, "pdcontact", 24, 44, 30, 50)
    r(qb, "pdcontact", 36, 44, 42, 50)
    # read strip: VSS | RD1 (QB) | RD2 (RWL) | RBL
    r(None, "ndiffusion", 12, 69, 35, 79)
    r(vss, "ndcontact", 12, 69, 18, 79)
    r(rbl, "ndcontact", 29, 69, 35, 79)
    # gate polys: QB runs PD_L -> PU_L -> RD1; Q runs PD_R -> PU_R; RD2 joins RWL
    r(qb, "polysilicon", 20, 10, 22, 81)
    r(q, "polysilicon", 32, 10, 34, 52)
    r(rwl, "polysilicon", 25, 67, 27, 86)

    # Q and QB nodes: NMOS contact <-> PMOS contact, then the cross-coupling poly contacts
    r(q, "metal1", 12, 22, 18, 44)
    r(qb, "metal1", 36, 22, 42, 44)
    r(qb, "polycontact", 21, 25, 27, 31)
    r(qb, "metal1", 21, 25, 42, 31)
    r(q, "polycontact", 27, 35, 33, 41)
    r(q, "metal1", 12, 35, 33, 41)

    # supplies: NMOS source down to the VSS rail, PMOS source up to VDDA, read source up to VSS
    r(vss, "metal1", 24, 3, 30, 12)
    r(vdda, "metal1", 24, 50, 30, 53)
    r(vss, "metal1", 12, 79, 18, 88)

    # bit lines: contact -> metal1 -> via1 -> metal2 column. Plain metal1 surrounds every via1 tile
    # by 1 lambda: Magic's ETRI style pulls via metal edges that touch no other metal back by 0.05 um,
    # which otherwise leaves 0.6 um slivers next to the contact (8.MET1.W).
    r(bl, "metal1", -1, 18, 8, 28)
    r(bl, "m2contact", 0, 20, 7, 27)
    r(bl, "metal2", 1, -3, 5, 94)
    r(blb, "metal1", 46, 18, 55, 28)
    r(blb, "m2contact", 47, 20, 54, 27)
    r(blb, "metal2", 49, -3, 53, 94)
    r(rbl, "metal1", 35, 70, 45, 79)
    r(rbl, "m2contact", 37, 71, 44, 78)
    r(rbl, "metal2", 38, -3, 42, 94)
    return S


def place_cell(lay: Layout, x0, y0, flip, **nets):
    """Cell at (x0, y0); flip mirrors it about its lower edge (the row then grows downwards)."""
    for net, layer, a, b, c, d in cell_shapes(**nets):
        if flip:
            b, d = -d, -b
        lay.r(net, layer, x0 + a, y0 + b, x0 + c, y0 + d)


def cell_netlist(name="sram8t", model_n="nfet", model_p="pfet", ports="BL BLB RBL WWL RWL VDDA VSS",
                 bl="BL", blb="BLB", rbl="RBL", wwl="WWL", rwl="RWL", q="Q", qb="QB", nmid="NMID",
                 vdda="VDDA", vss="VSS", prefix="", subckt=True) -> str:
    def m(n, d, g, s, b, mod, wl):
        return f"M{prefix}{n} {d} {g} {s} {b} {mod} W={wl[0]:g}u L={wl[1]:g}u"
    body = [
        m("pul", q, qb, vdda, vdda, model_p, SIZES["PU"]),
        m("pur", qb, q, vdda, vdda, model_p, SIZES["PU"]),
        m("pdl", q, qb, vss, vss, model_n, SIZES["PD"]),
        m("pdr", qb, q, vss, vss, model_n, SIZES["PD"]),
        m("pgl", bl, wwl, q, vss, model_n, SIZES["PG"]),
        m("pgr", blb, wwl, qb, vss, model_n, SIZES["PG"]),
        m("rd1", nmid, qb, vss, vss, model_n, SIZES["RD1"]),
        m("rd2", rbl, rwl, nmid, vss, model_n, SIZES["RD2"]),
    ]
    if not subckt:
        return "\n".join(body) + "\n"
    return f".subckt {name} {ports}\n" + "\n".join(body) + "\n.ends\n"


# ---------------------------------------------------------------------------------------------
ROWS, COLS = 15, 8

# array edges (lambda, x relative to the array's left / right edge)
WL_X = dict(poly=-12, pc=(-18, -12), m1=(-29, -11), v1=(-28, -21), m2=(-39, -20), v2=(-38, -31),
            m3=(-52, -30))
BUS = dict(VSS=(6, 18), VDDA=(24, 36))          # metal2 power buses, x from the array's right edge
BOTTOM = -12                                     # bottom end of the bit lines and buses (pins)


def row_origin(rr):
    """(y0, flip) of row rr: even rows grow up from y0, odd rows are mirrored and grow down."""
    flip = rr % 2 == 1
    return ((rr + 1) * PITCH_Y if flip else rr * PITCH_Y), flip


def local_y(rr, y):
    y0, flip = row_origin(rr)
    return y0 - y if flip else y0 + y


def wl_stack(lay: Layout, net, yc):
    """Word line pin at the left edge: poly -> poly contact -> metal1 -> via1 -> metal2 -> via2 -> metal3."""
    W = WL_X
    lay.r(net, "polysilicon", W["poly"], yc - 1, 0, yc + 1)
    lay.r(net, "metal1", W["m1"][0], yc - 4, W["m1"][1], yc + 4)
    lay.r(net, "polycontact", W["pc"][0], yc - 3, W["pc"][1], yc + 3)
    lay.r(net, "m2contact", W["v1"][0], yc - 3.5, W["v1"][1], yc + 3.5)
    lay.r(net, "metal2", W["m2"][0], yc - 4, W["m2"][1], yc + 4)
    lay.r(net, "m3contact", W["v2"][0], yc - 3.5, W["v2"][1], yc + 3.5)
    lay.r(net, "metal3", W["m3"][0], yc - 4, W["m3"][1], yc + 4)
    lay.port(net, "metal3", W["m3"][0], yc - 2, W["m3"][0] + 4, yc + 2)


def array_layout(rows=ROWS, cols=COLS, name="sram_array") -> Layout:
    """Flat array with its edges: WL pins (metal3) on the left, VSS and VDDA buses (metal2) on the
    right, bit lines (metal2) ending at the bottom for the column circuits."""
    lay = Layout(name)
    xr = cols * PITCH_X
    for rr in range(rows):
        y0, flip = row_origin(rr)
        for c in range(cols):
            place_cell(lay, c * PITCH_X, y0, flip,
                       bl=f"BL{c}", blb=f"BLB{c}", rbl=f"RBL{c}", wwl=f"WWL{rr}", rwl=f"RWL{rr}",
                       q=f"Q{rr}_{c}", qb=f"QB{rr}_{c}", vdda="VDDA", vss="VSS")
        wl_stack(lay, f"WWL{rr}", local_y(rr, 6))
        wl_stack(lay, f"RWL{rr}", local_y(rr, 85))
        # VDDA rail of the row -> VDDA bus (crosses the VSS bus in metal1)
        ya, yb = sorted((local_y(rr, 53), local_y(rr, 60)))
        lay.r("VDDA", "metal1", xr, ya, xr + 6, yb)
        lay.r("VDDA", "metal1", xr + 6, ya - 1, xr + BUS["VDDA"][1] + 1, yb + 1)
        vx = xr + (BUS["VDDA"][0] + BUS["VDDA"][1]) / 2
        lay.r("VDDA", "m2contact", vx - 3.5, (ya + yb) / 2 - 3.5, vx + 3.5, (ya + yb) / 2 + 3.5)
    # VSS rails sit on the mirror lines y = k * PITCH_Y
    for k in range(rows + 1):
        y = k * PITCH_Y
        lay.r("VSS", "metal1", xr, y - 3, xr + 6, y + 3)
        lay.r("VSS", "metal1", xr + 6, y - 4, xr + BUS["VSS"][1] + 1, y + 4)
        vx = xr + (BUS["VSS"][0] + BUS["VSS"][1]) / 2
        lay.r("VSS", "m2contact", vx - 3.5, y - 3.5, vx + 3.5, y + 3.5)
    top = rows * PITCH_Y + 3
    for net, (a, b) in BUS.items():
        lay.r(net, "metal2", xr + a, BOTTOM, xr + b, top)
        lay.port(net, "metal2", xr + a, BOTTOM, xr + b, BOTTOM + 3)
    for c in range(cols):
        x = c * PITCH_X
        for net, (a, b) in ((f"BL{c}", (1, 5)), (f"RBL{c}", (38, 42)), (f"BLB{c}", (49, 53))):
            lay.r(net, "metal2", x + a, BOTTOM, x + b, -3)
            lay.port(net, "metal2", x + a, BOTTOM, x + b, BOTTOM + 3)
    return lay


def array_netlist(rows=ROWS, cols=COLS, name="sram_array") -> str:
    ports = ([f"WWL{r}" for r in range(rows)] + [f"RWL{r}" for r in range(rows)]
             + [f"BL{c}" for c in range(cols)] + [f"BLB{c}" for c in range(cols)]
             + [f"RBL{c}" for c in range(cols)] + ["VDDA", "VSS"])
    lines = [f".subckt {name} " + " ".join(ports)]
    for r in range(rows):
        for c in range(cols):
            lines.append(cell_netlist(prefix=f"_{r}_{c}_", subckt=False,
                                      bl=f"BL{c}", blb=f"BLB{c}", rbl=f"RBL{c}", wwl=f"WWL{r}",
                                      rwl=f"RWL{r}", q=f"Q{r}_{c}", qb=f"QB{r}_{c}",
                                      nmid=f"NMID{r}_{c}").rstrip())
    lines.append(".ends")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------------
def magicrc() -> str:
    rc = os.environ.get("ETRI050_MAGICRC")
    if not rc:
        dk = os.environ.get("ETRI050_DK", str(REPO / ".pdk/ETRI050_DesignKit"))
        rc = os.path.join(dk, "tech/etri050.magicrc")
    if not os.path.isfile(rc):
        sys.exit(f"Magic startup file not found: {rc}\n(run: bash scripts/setup-etri050.sh)")
    return rc


def run_magic(script: str, cwd: Path, log: str) -> None:
    res = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", magicrc()],
                         input=script + "quit -noprompt\n", text=True, cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (cwd / log).write_text(res.stdout)


def etri_check(cell: str, sch: str | None, cwd: Path) -> tuple[bool, str]:
    """etri-check helper (Magic DRC, ETRI GDS, KLayout DRC with the kit deck, Netgen LVS)."""
    cmd = 'source "$0" && etri-check "$1" "$2"'
    res = subprocess.run(["bash", "-c", cmd, str(REPO / "scripts/etri050-env.sh"), cell, sch or ""],
                         cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    line = next((s for s in res.stdout.splitlines() if s.startswith("ETRI-CHECK")), res.stdout.strip())
    return res.returncode == 0, line


def build(lay: Layout, netlist: str, out: Path, check: bool) -> bool:
    out.mkdir(parents=True, exist_ok=True)
    for ext in (".mag", ".ext", ".spice", ".gds"):
        (out / f"{lay.name}{ext}").unlink(missing_ok=True)
    run_magic(lay.magic_tcl(), out, f"{lay.name}_build.log")
    if not (out / f"{lay.name}.mag").exists():
        sys.exit(f"Magic did not write {lay.name}.mag (see {out / (lay.name + '_build.log')})")
    (out / "sch").mkdir(exist_ok=True)
    sch = out / "sch" / f"{lay.name}.spice"
    sch.write_text(netlist)
    bx0, by0, bx1, by1 = lay.bbox()
    print(f"{lay.name}: {len(lay.rects)} rectangles, {(bx1 - bx0) * LAMBDA_UM:.1f} x "
          f"{(by1 - by0) * LAMBDA_UM:.1f} um -> {out / (lay.name + '.mag')}")
    if not check:
        return True
    ok, line = etri_check(lay.name, f"sch/{lay.name}.spice", out)
    print(("PASS  " if ok else "FAIL  ") + line)
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=["cell", "array", "all"])
    ap.add_argument("--rows", type=int, default=ROWS)
    ap.add_argument("--cols", type=int, default=COLS)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    ok = True
    if a.what in ("cell", "all"):      # one cell with the array edges (its rails, taps and pins)
        ok &= build(array_layout(1, 1, "sram8t"), array_netlist(1, 1, "sram8t"), a.out, a.check)
    if a.what in ("array", "all"):
        ok &= build(array_layout(a.rows, a.cols), array_netlist(a.rows, a.cols), a.out, a.check)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
