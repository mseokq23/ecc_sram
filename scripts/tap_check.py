#!/usr/bin/env python3
"""Supply connection of every substrate and well tap in the chip core, followed through metal (KLayout).

The transistor-level LVS (chip/core_lvs.py) takes the NMOS bulk as VSS whatever the drawing does, so a block
whose gnd rail reached VSS only through the substrate would still match. This check follows the metal:
each p+ substrate tap (CONT on ACT and PSD outside N-well) must be on the metal net of a VSS pad port, each n+
well tap (CONT on ACT and NSD inside N-well) on the metal net of a VDD, VDDA or VDDW pad port.

  python3 scripts/tap_check.py [gds]  (after chip/core_lvs.py: reads chip/build/lvs/ecc_sram_core_lvs.gds,
                                       where the pad ports are drawn in, and chip/build/pad_pins.json)
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import klayout.db as kdb

REPO = Path(__file__).resolve().parents[1]
CHIP = REPO / "designs/etri050/chip"
METAL = dict(m1=32, v1=33, m2=34, v2=35, m3=36)
NWELL, ACT, NSD, PSD, CONT = 2, 11, 14, 15, 31


def main() -> int:
    ly = kdb.Layout()
    ly.read(sys.argv[1] if len(sys.argv) > 1 else str(CHIP / "build/lvs/ecc_sram_core_lvs.gds"))
    top = ly.top_cell()
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
    lay = {k: l2n.make_layer(ly.layer(n, 0), k) for k, n in METAL.items()}
    for layer in lay.values():
        l2n.connect(layer)
    for a, b in (("m1", "v1"), ("v1", "m2"), ("m2", "v2"), ("v2", "m3")):
        l2n.connect(lay[a], lay[b])
    l2n.extract_netlist()

    supply = {}                                       # metal net id -> supply name
    for p in json.loads((CHIP / "build/pad_pins.json").read_text())["pads"]:
        name = {"PVDD": "VDD", "PVSS": "VSS"}.get(p["cell"], p["pin"])
        if name in ("VDD", "VSS", "VDDA", "VDDW"):
            x1, y1, x2, y2 = p["rect"]
            net = l2n.probe_net(lay["m2"], kdb.DPoint((x1 + x2) / 2, (y1 + y2) / 2))
            if net is None:
                print(f"pad {p['pad']} ({name}): no metal at its port")
                return 1
            supply[net.cluster_id] = name

    def region(n):
        return kdb.Region(top.begin_shapes_rec(ly.layer(n, 0)))
    nw, act, nsd, psd, cont = (region(n) for n in (NWELL, ACT, NSD, PSD, CONT))
    taps = {"p+ substrate taps": (((cont & act & psd) - nw).merged(), ("VSS",)),
            "n+ well taps": ((cont & act & nsd & nw).merged(), ("VDD", "VDDA", "VDDW"))}
    bad = []
    for kind, (reg, allowed) in taps.items():
        count = Counter()
        for poly in reg.each():
            c = poly.bbox().center()
            net = l2n.probe_net(lay["m1"], kdb.DPoint(c.x * ly.dbu, c.y * ly.dbu))
            name = supply.get(net.cluster_id) if net is not None else None
            count[name or "not a supply"] += 1
            if name not in allowed:
                bad.append((kind, round(c.x * ly.dbu, 2), round(c.y * ly.dbu, 2), name or "not a supply"))
        print(f"{kind}: {sum(count.values())} ({', '.join(f'{k} {v}' for k, v in sorted(count.items()))})")
    for b in bad[:20]:
        print("off supply:", b)
    if bad:
        print(f"tap check: {len(bad)} taps not on the right supply metal")
        return 1
    print("tap check: all taps on supply metal nets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
