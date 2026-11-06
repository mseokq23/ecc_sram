#!/usr/bin/env python3
"""Full-custom blocks built from the kit's standard cells: rows of cells placed by code, wired by code.

Shared by gen/robank.py (ring oscillators) and gen/canary.py (canary latches). Python places kit cells
(INVX1, INVX4, NAND2X1, NOR2X1) on Magic's lambda grid (0.3 um) and adds rectangles with a net name each;
Magic draws the block with the kit technology. The same approach and code as the RO bank and the CBCM block
of the earlier pdkv chip (repository mychip, gen/etri050_ro.py and gen/etri050_cbcm.py), which passed the
official KLayout deck, the rule-document checks and LVS there.

Kit cell facts used here (digital_ETRI/*.mag, magscale 1 2): cell height 120 lambda, gnd rail y -4..4,
vdd rail y 116..124 (normal orientation), both rails are tap contacts along the whole cell (so no via1 may
sit on them inside a cell: rule document, via1 on contact), N-well y 67..126. Pins are metal2 squares with
the via1 pad next to them (PINS, lambda, normal orientation).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from etri050_mos import LAMBDA_UM, REPO, etri_check, run_magic, um  # noqa: E402,F401

CT = 6           # diffusion / poly / tap contact tile (one 0.6 um cut, 0.6 um border)
VIA = 7          # m2contact / m3contact tile (0.8 um cut, 0.6 um border; 2.1 um)
GAP = 2          # contact tile to gate
CAP = 2          # poly beyond active
SP = 3.5         # metal2 / metal3 spacing used for the added routing (1.05 um >= 1.0 um)
ROW_H = 120      # standard-cell row height

CELL_W = {"INVX1": 30, "INVX4": 40, "NOR2X1": 40, "NAND2X1": 40}
# metal2 pins of the kit cells (lambda, normal orientation): m2p pin plus the via1 pad next to it
PINS = {"INVX1": {"A": (1.5, 31.5, 8.5, 45.5), "Y": (11.5, 44.5, 18.5, 58.5)},
        "INVX4": {"A": (1.5, 44.5, 8.5, 58.5), "Y": (21.5, 44.5, 28.5, 58.5)},
        "NOR2X1": {"A": (1.5, 41.5, 8.5, 55.5), "B": (21.5, 41.5, 28.5, 55.5), "Y": (11.5, 31.5, 18.5, 45.5)},
        "NAND2X1": {"A": (1.5, 54.5, 8.5, 68.5), "B": (21.5, 54.5, 28.5, 68.5), "Y": (11.5, 51.5, 18.5, 65.5)}}
# stub centre per pin (4 lambda wide stubs, kept 6 lambda from the cell's other pins)
STUB_X = {"INVX1": {"A": 3.5, "Y": 15}, "INVX4": {"A": 5, "Y": 25},
          "NOR2X1": {"A": 5, "B": 25, "Y": 15}, "NAND2X1": {"A": 4.5, "B": 25.5, "Y": 15}}
PIN_ORDER = {"INVX1": "A Y", "INVX4": "A Y", "NAND2X1": "A B Y", "NOR2X1": "A B Y"}


def kit_stdcells_spice(cells=("INVX1", "INVX4", "NAND2X1", "NOR2X1")) -> str:
    """The kit's LVS netlist of the standard cells a block uses (nfet / pfet)."""
    import os
    dk = os.environ.get("ETRI050_DK", str(REPO / ".pdk/ETRI050_DesignKit"))
    if not Path(dk).is_dir():
        dk = str(Path.home() / "ETRI050_DesignKit")
    txt = (Path(dk) / "digital_ETRI/khu_etri050_stdcells.spice").read_text()
    out = []
    for cell in cells:
        m = re.search(r"^\.subckt %s .*?^\.ends.*?$" % cell, txt, re.S | re.M | re.I)
        if not m:
            raise SystemExit(f"{cell} not in the kit standard-cell netlist")
        out.append(m.group(0))
    return "\n".join(out) + "\n"


@dataclass
class Layout:
    name: str
    rects: list = field(default_factory=list)
    ports: list = field(default_factory=list)       # (name, layer, x0, y0, x1, y1)

    def paint(self, layer, x0, y0, x1, y1):
        if x1 <= x0 or y1 <= y0:
            raise ValueError(f"empty {layer} rectangle {x0},{y0},{x1},{y1}")
        self.rects.append((layer, x0, y0, x1, y1))

    def port(self, name, layer, x0, y0, x1, y1):
        self.ports.append((name, layer, x0, y0, x1, y1))

    def bbox(self):
        xs = [v for r in self.rects for v in (r[1], r[3])]
        ys = [v for r in self.rects for v in (r[2], r[4])]
        return min(xs), min(ys), max(xs), max(ys)

    ORDER = ["nwell", "ndiffusion", "pdiffusion", "polysilicon", "ndcontact", "pdcontact",
             "psubstratepcontact", "nsubstratencontact", "polycontact", "metal1", "metal2",
             "m2contact", "metal3", "m3contact"]

    def magic_tcl(self) -> str:
        out = [f"load {self.name}", "snap internal"]
        for lyr, *_ in self.rects:
            if lyr not in self.ORDER:
                raise ValueError(f"unknown layer {lyr}")
        for layer in self.ORDER:     # contacts after plain layers, so a contact is never overwritten
            for lyr, x0, y0, x1, y1 in self.rects:
                if lyr == layer:
                    out += [f"box {um(x0)} {um(y0)} {um(x1)} {um(y1)}", f"paint {layer}"]
        for name, layer, x0, y0, x1, y1 in self.ports:
            out += [f"box {um(x0)} {um(y0)} {um(x1)} {um(y1)}", f"label {name} c {layer}"]
        bx0, by0, bx1, by1 = self.bbox()
        out += [f"box {um(bx0 - 1)} {um(by0 - 1)} {um(bx1 + 1)} {um(by1 + 1)}", "port makeall",
                f"save {self.name}"]
        return "\n".join(out) + "\n"


class Block(Layout):
    """Layout plus standard-cell instances and a net name on every routing rectangle."""

    def __init__(self, name):
        super().__init__(name)
        self.cells = []          # (cell, x, y, flipped, instance)
        self.netrects = []       # (net, layer, x0, y0, x1, y1) for the spacing check
        self.pinrects = []       # kit cell pins (net, layer, x0, y0, x1, y1)

    def r(self, net, layer, x0, y0, x1, y1):
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        self.paint(layer, x0, y0, x1, y1)
        self.netrects.append((net, layer, x0, y0, x1, y1))

    def cell(self, cell, x, y, flipped, inst):
        self.cells.append((cell, x, y, flipped, inst))
        out = {}
        for pin, (a, b, c, d) in PINS[cell].items():
            if flipped:
                b, d = ROW_H - d, ROW_H - b
            out[pin] = (x + a, y + b, x + c, y + d)
        return out

    def magic_tcl(self) -> str:
        tcl = super().magic_tcl()
        head, rest = tcl.split("\n", 2)[:2], tcl.split("\n", 2)[2]
        lines = []
        for cell, x, y, flipped, inst in self.cells:
            lines += [f"box {x * LAMBDA_UM:.2f}um {y * LAMBDA_UM:.2f}um {x * LAMBDA_UM:.2f}um {y * LAMBDA_UM:.2f}um",
                      f"getcell {cell}{' v' if flipped else ''}", f"identify {inst}"]
        return "\n".join(head + lines) + "\n" + rest

    def via2(self, net, x, y):
        """via2 tile centred at (x, y)."""
        self.r(net, "m3contact", x - 3.5, y - 3.5, x + 3.5, y + 3.5)

    def via1(self, net, x, y):
        self.r(net, "m2contact", x - 3.5, y - 3.5, x + 3.5, y + 3.5)


MIN_SP = {"metal1": 3, "metal2": SP, "metal3": SP}
CUTS = {"m2contact": ("metal1", "metal2"), "m3contact": ("metal2", "metal3")}


def spacing_errors(blk, extra=()):
    """Added rectangles closer than MIN_SP to a rectangle of another net on the same metal (touching
    counts), including the kit cells' pins; the cells' own pin-to-pin gaps are the kit's. extra:
    further (net, layer, x0, y0, x1, y1, kind) shapes drawn without blk.r (custom devices)."""
    by_layer = {}
    for kind, rects in (("route", blk.netrects), ("pin", blk.pinrects)):
        for net, layer, x0, y0, x1, y1 in rects:
            for m in CUTS.get(layer, (layer,)):
                if m in MIN_SP:
                    by_layer.setdefault(m, []).append((net, x0, y0, x1, y1, kind))
    for net, layer, x0, y0, x1, y1, kind in extra:
        if layer in MIN_SP:
            by_layer.setdefault(layer, []).append((net, x0, y0, x1, y1, kind))
    errs = []
    for m, rs in by_layer.items():
        d = MIN_SP[m]
        rs.sort(key=lambda t: t[1])
        for k, a in enumerate(rs):
            for b in rs[k + 1:]:
                if b[1] >= a[3] + d:
                    break
                if a[0] == b[0] or (a[5] == "pin" and b[5] == "pin"):
                    continue
                dx = max(b[1] - a[3], a[1] - b[3], 0)
                dy = max(b[2] - a[4], a[2] - b[4], 0)
                if (dx * dx + dy * dy) ** 0.5 < d - 1e-9:
                    errs.append((m, a, b))
    return errs


def flat_drc(out: Path, name: str):
    """Magic DRC of a flattened copy (hierarchical checks count the kit cells' abutting rails)."""
    script = f"""drc off
load {name} -force
flatten {name}_flat
load {name}_flat
select top cell
drc on
drc check
drc catchup
set n [drc list count total]
puts "FLATDRC $n"
foreach {{why boxes}} [drc listall why] {{ puts "FLATWHY [llength $boxes] {{$why}}" }}
"""
    run_magic(script, out, f"{name}_flatdrc.log")
    txt = (out / f"{name}_flatdrc.log").read_text()
    m = re.search(r"^FLATDRC (\d+)", txt, re.M)
    return (int(m.group(1)) if m else -1), re.findall(r"^FLATWHY (.*)$", txt, re.M)


def write_flat_gds(blk: Block, out: Path) -> Path:
    """Magic draws the block, flattens it and writes <name>_flat.gds with the ETRI layer numbers (the
    chip uses the flat copy: kept hierarchical, each cell's rail taps come out separately and overlap)."""
    name = blk.name
    for ext in (".mag", ".ext", ".spice", ".gds"):
        (out / f"{name}{ext}").unlink(missing_ok=True)
    (out / f"{name}_flat.gds").unlink(missing_ok=True)
    run_magic(blk.magic_tcl() + f"flatten {name}_flat\nload {name}_flat\ncif ostyle lambda=0.30(ETRI)\n"
              f"gds write {name}_flat.gds\n", out, f"{name}_build.log")
    gds = out / f"{name}_flat.gds"
    if not gds.exists():
        sys.exit(f"Magic did not write {gds.name} (see {out / (name + '_build.log')})")
    return gds
