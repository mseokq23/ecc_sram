#!/usr/bin/env python3
"""Floating metal: metal pieces that reach no contact and no bonding pad.

Metal1-3 and their vias are joined into nets; a net with at least one contact (CONT, to diffusion or poly)
or a PAD opening is connected to something, every other net is a floating piece (left-over wire, stub).
LVS does not see these (no device on them), DRC does not either (they can be legal shapes).

  python3 scripts/float_metal.py [gds]    (default: designs/etri050/chip/build/ecc_sram_Top.gds)

Prints the number of metal nets and lists the floating ones inside the core (442-1458 um) and in the ring.
Exit 1 if any is found.
"""
import sys
from pathlib import Path

import klayout.db as kdb

REPO = Path(__file__).resolve().parents[1]
CORE = (442.0, 442.0, 1458.0, 1458.0)


def main() -> int:
    gds = sys.argv[1] if len(sys.argv) > 1 else str(REPO / "designs/etri050/chip/build/ecc_sram_Top.gds")
    ly = kdb.Layout()
    ly.read(gds)
    top = ly.top_cell()
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
    lay = {n: l2n.make_layer(ly.layer(l, 0), n) for n, l in
           (("cont", 31), ("m1", 32), ("via1", 33), ("m2", 34), ("via2", 35), ("m3", 36), ("pad", 37))}
    for n in lay.values():
        l2n.connect(n)
    for a, b in (("cont", "m1"), ("m1", "via1"), ("via1", "m2"), ("m2", "via2"), ("via2", "m3"), ("m3", "pad")):
        l2n.connect(lay[a], lay[b])
    l2n.extract_netlist()
    nl = l2n.netlist()
    nl.flatten()
    core = kdb.Box(*(round(v / ly.dbu) for v in CORE))
    total, found = 0, []
    for net in nl.top_circuit().each_net():
        metal = kdb.Region()
        for n in ("m1", "m2", "m3"):
            metal += l2n.shapes_of_net(net, lay[n], True)
        if metal.is_empty():
            continue
        total += 1
        if l2n.shapes_of_net(net, lay["cont"], True).is_empty() and l2n.shapes_of_net(net, lay["pad"], True).is_empty():
            bb = metal.bbox()
            where = "core" if core.contains(bb.p1) and core.contains(bb.p2) else "ring"
            found.append((where, metal.area() * ly.dbu ** 2,
                          [round(v * ly.dbu, 2) for v in (bb.left, bb.bottom, bb.right, bb.top)]))
    print(f"{Path(gds).name}: {total} metal nets, {len(found)} floating "
          f"({sum(1 for f in found if f[0] == 'core')} in the core)")
    for where, area, box in sorted(found, key=lambda f: -f[1])[:30]:
        print(f"  {where} {area:.2f} um2 at {box}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
