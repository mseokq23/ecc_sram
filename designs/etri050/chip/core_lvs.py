#!/usr/bin/env python3
"""Transistor-level LVS of the chip core: everything inside the pad ring (build/ecc_sram_core.gds from
assemble.py) against the circuit it was built from.

  python3 designs/etri050/chip/core_lvs.py

Layout side: the core GDS is flattened and its block labels are removed; the pad cells' core-side ports
(metal2 rectangles from pad_pins.json) are drawn in and labelled with the pad's pin name (pins.csv), so the
core wiring must reach each port. Magic reads it with the kit's ETRI GDS style, extracts every device and
writes a flat netlist. A supply with several pads that the core does not join itself (VDD N4 and S7, VSS E4)
is joined by the pad ring; that is checked on the pad ring's own metal (ring_supplies) and the supply's pads
are then one node in the netlist (merge_supplies).
Reference side, written from the design and not from the drawing:
  control block   ctrl/macro/ecc_fi_ctrl.spc + the kit's standard cell netlist (khu_etri050_stdcells.spice)
  decoder block   ctrl/macro/ecc_dec.spc (the same cells); its inputs are the control block's R, VIEW, V_DIR,
                  HALF, its outputs the output pads
  SRAM macro      gen/colper.py (sram/build/sch/sram_macro.spice), decoupling gen/decap.py
  chip            the pad pins (pins.csv) and the block-to-block nets below
Netgen compares the two with the kit's setup (etri050_setup.tcl). Results: build/lvs/core_lvs.out.
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import klayout.db as kdb

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
D = REPO / "designs/etri050"
B = HERE / "build"
L = B / "lvs"
KIT = Path(os.environ.get("ETRI050_DK", REPO / ".pdk/ETRI050_DesignKit"))


def layout_gds():
    ly = kdb.Layout()
    ly.read(str(B / "ecc_sram_core.gds"))
    top = ly.top_cell()
    ly.flatten(top.cell_index(), -1, True)
    for li in ly.layer_indexes():
        texts = [s for s in top.shapes(li).each() if s.is_text()]
        for s in texts:
            top.shapes(li).erase(s)
    # the pad cells' core-side ports (metal2, pad_pins.json) are drawn in and labelled at their centres, so a
    # core wire that stops short of its port leaves the label on a separate node and the comparison fails
    m2 = ly.layer(34, 0)
    names = set()
    pads = json.loads((B / "pad_pins.json").read_text())["pads"]
    for p in pads:
        name = {"PVDD": "VDD", "PVSS": "VSS"}.get(p["cell"], p["pin"])
        x1, y1, x2, y2 = (round(v * 1000) for v in p["rect"])
        top.shapes(m2).insert(kdb.Box(x1, y1, x2, y2))
        top.shapes(m2).insert(kdb.Text(name, kdb.Trans(kdb.Vector((x1 + x2) // 2, (y1 + y2) // 2))))
        names.add(name)
    L.mkdir(parents=True, exist_ok=True)
    out = L / "ecc_sram_core_lvs.gds"
    ly.write(str(out))
    return out, sorted(names), pads


def extract(gds: Path):
    script = f"""cif istyle lambda=0.30(ETRI)
gds read {gds.name}
load ecc_sram_core
select top cell
port makeall
extract do local
extract all
ext2spice lvs
ext2spice -o ecc_sram_core.spice
quit -noprompt
"""
    rc = KIT / "tech/etri050.magicrc"
    p = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", str(rc)], input=script, text=True, cwd=L,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (L / "extract.log").write_text(p.stdout)
    if not (L / "ecc_sram_core.spice").exists():
        sys.exit(f"Magic did not write the netlist (see {L / 'extract.log'})")


SUPPLY_CELLS = {"PVDD": "VDD", "PVSS": "VSS"}


def ring_supplies(pads):
    """Supplies with more than one pad, after checking that the pad ring's own metal joins their pads.

    The core does not join every pad of a supply itself: it feeds the control and decoder blocks from the VDD
    pad N4 and the macro from S7, and leaves the VSS pad E4 to the ring (assemble.py). On the chip the supply
    buses that run through the ETRI pad cells join them. This reads the pad ring alone (build/ecc_sram_Pad.gds),
    flattened, connects metal1-metal3 through the vias and requires all ports of a supply on one net and the
    supplies on different nets.
    """
    groups = {}
    for p in pads:
        if p["cell"] in SUPPLY_CELLS:
            groups.setdefault(SUPPLY_CELLS[p["cell"]], []).append(p)
    ly = kdb.Layout()
    ly.read(str(B / "ecc_sram_Pad.gds"))
    top = ly.top_cell()
    ly.flatten(top.cell_index(), -1, True)
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
    lay = {n: l2n.make_layer(ly.layer(g, 0), n) for n, g in (("m1", 32), ("v1", 33), ("m2", 34), ("v2", 35), ("m3", 36))}
    for x in lay.values():
        l2n.connect(x)
    for a, b in (("m1", "v1"), ("v1", "m2"), ("m2", "v2"), ("v2", "m3")):
        l2n.connect(lay[a], lay[b])
    l2n.extract_netlist()
    net_of = {}
    for name, ps in groups.items():
        nets = set()
        for p in ps:
            x1, y1, x2, y2 = p["rect"]
            n = l2n.probe_net(lay["m2"], kdb.DPoint((x1 + x2) / 2, (y1 + y2) / 2))
            nets.add(n.cluster_id if n else None)
        if None in nets or len(nets) != 1:
            sys.exit(f"pad ring: the {name} pads {[p['pad'] for p in ps]} are not on one metal net")
        net_of[name] = nets.pop()
    if len(set(net_of.values())) != len(net_of):
        sys.exit(f"pad ring: two supplies on one metal net {net_of}")
    return {n: sorted(p["pad"] for p in ps) for n, ps in groups.items() if len(ps) > 1}


def merge_supplies(spice: Path, names):
    """Make the nodes Magic split off a supply (VDD_uq0, VSS_uq0, ...) that supply again.

    They are pads of the supply that the pad ring joins (ring_supplies). Magic 8.3.105 joined labels of the same
    name itself; Magic 8.3.685 (IIC-OSIC-TOOLS 2026.10) keeps them apart. A supply part that reaches no pad has
    no label and stays a separate node.
    """
    if not names:
        return []
    pat = re.compile(r"^(%s)_uq\d+$" % "|".join(map(re.escape, names)))
    merged, out = set(), []
    for line in spice.read_text().replace("\n+", " ").splitlines():
        toks = line.split()
        new = []
        for t in toks:
            m = pat.match(t)
            if m:
                merged.add(t)
                t = m.group(1)
            new.append(t)
        if new and new[0].lower() == ".subckt":
            new = new[:2] + list(dict.fromkeys(new[2:]))
        out.append(" ".join(new) if toks else line)
    spice.write_text("\n".join(out) + "\n")
    return sorted(merged)


def bus(name):
    """Block pin -> chip net: ADDR[2] -> ADDR2, R[5] -> R5, DED_FLAG -> DED, vdd -> VDD, gnd -> VSS."""
    return {"vdd": "VDD", "gnd": "VSS", "DED_FLAG": "DED", "SEC_FLAG": "SEC"}.get(name, re.sub(r"\[(\d+)\]", r"\1", name))


def ports(text, name):
    """Port list of subcircuit name (continuation lines joined)."""
    head = re.search(r"^\.subckt %s (.*?)\n(?!\+)" % re.escape(name), text, re.S | re.M)
    return head.group(1).replace("\n+", " ").split()


def reference(pins):
    ctrl = (D / "ctrl/macro/ecc_fi_ctrl.spc").read_text()
    cports = ports(ctrl, "ecc_fi_ctrl")
    decs = (D / "ctrl/macro/ecc_dec.spc").read_text()
    dports = ports(decs, "ecc_dec")
    macro = (D / "sram/build/sch/sram_macro.spice").read_text()
    mports = re.search(r"^\.subckt sram_macro (.*)$", macro, re.M).group(1).split()
    parts = [f"* reference netlist of the chip core (written by core_lvs.py)",
             (KIT / "digital_ETRI/khu_etri050_stdcells.spice").read_text(), ctrl, decs, macro,
             (D / "sram/build/sch/decap_vddw.spice").read_text(), (D / "sram/build/sch/decap_vdda.spice").read_text(),
             f".subckt ecc_sram_core {' '.join(pins)}",
             "Xctrl " + " ".join(bus(p) for p in cports) + " ecc_fi_ctrl",
             "Xdec " + " ".join(bus(p) for p in dports) + " ecc_dec",
             "Xmacro " + " ".join(mports) + " sram_macro",
             "Xdw VDDW VSS decap_vddw",
             "Xda VDDA VSS decap_vdda",
             ".ends"]
    ref = L / "core_ref.spice"
    ref.write_text("\n".join(parts) + "\n")
    return ref


def main() -> int:
    gds, pins, pads = layout_gds()
    want = sorted({r["pin"] if r["cell"] not in ("PVDD", "PVSS") else {"PVDD": "VDD", "PVSS": "VSS"}[r["cell"]]
                   for r in csv.DictReader(open(HERE / "pins.csv", encoding="utf-8"))})
    if pins != want:
        sys.exit(f"pin labels {pins} differ from pins.csv {want}")
    joined = ring_supplies(pads)
    extract(gds)
    merged = merge_supplies(L / "ecc_sram_core.spice", list(joined))
    print("pad ring metal joins " + ", ".join(f"{n} pads {' '.join(v)}" for n, v in joined.items())
          + (f"; merged {', '.join(merged)}" if merged else ""))
    ref = reference(pins)
    setup = KIT / "tech/etri050_setup.tcl"
    p = subprocess.run(["netgen", "-batch", "lvs", "ecc_sram_core.spice ecc_sram_core", f"{ref.name} ecc_sram_core",
                        str(setup), "core_lvs.out"], cwd=L, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (L / "netgen.log").write_text(p.stdout)
    out = (L / "core_lvs.out").read_text() if (L / "core_lvs.out").exists() else ""
    lines = [l for l in out.splitlines() if re.search(r"Number of devices|Number of nets|match|Cell pin lists", l)]
    print("\n".join(lines[-6:]))
    ok = ("Circuits match uniquely" in out or "Netlists match uniquely" in out) and "port errors" not in out
    print(f"core LVS: {'MATCH' if ok else 'NOT MATCHED'} (build/lvs/core_lvs.out)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
