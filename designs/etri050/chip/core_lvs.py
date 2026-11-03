#!/usr/bin/env python3
"""Transistor-level LVS of the chip core: everything inside the pad ring (build/ecc_sram_core.gds from
assemble.py) against the circuit it was built from.

  python3 designs/etri050/chip/core_lvs.py

Layout side: the core GDS is flattened and its block labels are removed; the pad cells' core-side ports
(metal2 rectangles from pad_pins.json) are drawn in and labelled with the pad's pin name (pins.csv), so the
core wiring must reach each port. Magic reads it with the kit's ETRI GDS style, extracts every device and
writes a flat netlist.
Reference side, written from the design and not from the drawing:
  control block   ctrl/macro/ecc_fi_ctrl.spc + the kit's standard cell netlist (khu_etri050_stdcells.spice)
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
    for p in json.loads((B / "pad_pins.json").read_text())["pads"]:
        name = {"PVDD": "VDD", "PVSS": "VSS"}.get(p["cell"], p["pin"])
        x1, y1, x2, y2 = (round(v * 1000) for v in p["rect"])
        top.shapes(m2).insert(kdb.Box(x1, y1, x2, y2))
        top.shapes(m2).insert(kdb.Text(name, kdb.Trans(kdb.Vector((x1 + x2) // 2, (y1 + y2) // 2))))
        names.add(name)
    L.mkdir(parents=True, exist_ok=True)
    out = L / "ecc_sram_core_lvs.gds"
    ly.write(str(out))
    return out, sorted(names)


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


def bus(name):
    """Control block pin -> chip net: ADDR[2] -> ADDR2, DED_FLAG -> DED, vdd -> VDD, gnd -> VSS."""
    return {"vdd": "VDD", "gnd": "VSS", "DED_FLAG": "DED", "SEC_FLAG": "SEC"}.get(name, re.sub(r"\[(\d+)\]", r"\1", name))


def reference(pins):
    ctrl = (D / "ctrl/macro/ecc_fi_ctrl.spc").read_text()
    head = re.search(r"^\.subckt ecc_fi_ctrl (.*?)\n(?!\+)", ctrl, re.S | re.M)
    cports = head.group(1).replace("\n+", " ").split()
    macro = (D / "sram/build/sch/sram_macro.spice").read_text()
    mports = re.search(r"^\.subckt sram_macro (.*)$", macro, re.M).group(1).split()
    parts = [f"* reference netlist of the chip core (written by core_lvs.py)",
             (KIT / "digital_ETRI/khu_etri050_stdcells.spice").read_text(), ctrl, macro,
             (D / "sram/build/sch/decap_vddw.spice").read_text(), (D / "sram/build/sch/decap_vdda.spice").read_text(),
             f".subckt ecc_sram_core {' '.join(pins)}",
             "Xctrl " + " ".join(bus(p) for p in cports) + " ecc_fi_ctrl",
             "Xmacro " + " ".join(mports) + " sram_macro",
             "Xdw VDDW VSS decap_vddw",
             "Xda VDDA VSS decap_vdda",
             ".ends"]
    ref = L / "core_ref.spice"
    ref.write_text("\n".join(parts) + "\n")
    return ref


def main() -> int:
    gds, pins = layout_gds()
    want = sorted({r["pin"] if r["cell"] not in ("PVDD", "PVSS") else {"PVDD": "VDD", "PVSS": "VSS"}[r["cell"]]
                   for r in csv.DictReader(open(HERE / "pins.csv", encoding="utf-8"))})
    if pins != want:
        sys.exit(f"pin labels {pins} differ from pins.csv {want}")
    extract(gds)
    ref = reference(pins)
    setup = KIT / "tech/etri050_setup.tcl"
    p = subprocess.run(["netgen", "-batch", "lvs", "ecc_sram_core.spice ecc_sram_core", f"{ref.name} ecc_sram_core",
                        str(setup), "core_lvs.out"], cwd=L, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (L / "netgen.log").write_text(p.stdout)
    out = (L / "core_lvs.out").read_text() if (L / "core_lvs.out").exists() else ""
    lines = [l for l in out.splitlines() if re.search(r"Number of devices|Number of nets|match|Cell pin lists", l)]
    print("\n".join(lines[-6:]))
    ok = "Circuits match uniquely" in out or "Netlists match uniquely" in out
    print(f"core LVS: {'MATCH' if ok else 'NOT MATCHED'} (build/lvs/core_lvs.out)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
