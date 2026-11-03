#!/usr/bin/env python3
"""Top-level assembly of the ECC 8T SRAM chip (KLayout): ETRI GPIO pad ring, control block (qflow macro),
SRAM macro (array + column circuits), decoupling for VDDA and VDDW, and the wiring between them.

  python3 designs/etri050/chip/assemble.py        (after run_pad_ring.sh, colper.py, decap.py, freeze_macro.sh)

Writes build/ecc_sram_Top.gds (the chip), build/ecc_sram_core.gds (the same without the pad ring, for LVS)
and build/ecc_sram_nets.json (where each pad port meets the core wiring: the LVS pin labels).

Floorplan (die um, core window 442-1458):
  control block   lower-left (470, 560); inputs from W pads on its left side, from S pads on its bottom
                  left, from N pads on its top left; outputs on its top right; word lines on its right;
                  PRE_N, WD and SENSE on its bottom right
  SRAM macro      lower-left (1065, 567.4), word line pins (left) facing the control block
  decoupling      VDDW 57 pF at (1290, 470), VDDA 28.5 pF at (1290, 770), supply buses toward the E pads
Wiring (three layers, each net on its own track, so no two nets share a layer where they cross):
  word lines      control pin -> metal3 -> metal2 track (x 965 + 3 i) -> metal1 into the macro's word line
                  contact stack
  bottom channel  S pad inputs on metal3 tracks y 450-466 (below), PRE_N/WD/SENSE on tracks y 474-538,
                  metal2 up and down at the pins
  W channel       pad port -> metal2 -> metal1 track (x 446 + 3 i) -> metal2/metal3 into the control pin
  top channel     outputs on metal3 tracks y 1080-1100, N pad inputs on y 1108-1116; E pad outputs go down
                  or up metal2 lanes at x 1444-1452
  supplies        VSS: metal3 strap y 542-556 from the control block's gnd spine to the macro VSS bus,
                  the decap VSS buses and pads S6, E1; VDD: N4 -> metal3 y 1438-1450 -> control block vdd
                  spine, S7 -> macro VDD bus; VDDW: E2 -> decap -> macro (metal3 y 576-590); VDDA: E3 ->
                  decap -> macro (metal3 between two of the array's VDDA bus vias)
Rules used (rule document v1.1): metal1 >= 0.8, metal2 >= 1.0, metal3 >= 1.2 wide; cuts 0.8 with 0.6
enclosure, cut spacing 0.8, no VIA2 on VIA1; drawn here: metal1 1.2, metal2 1.2, metal3 1.6, via pads 2.0.
Every coordinate is rounded to 0.01 um.
"""
from __future__ import annotations

import gzip
import json
import shutil
import sys
from pathlib import Path

import klayout.db as kdb

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
D = REPO / "designs/etri050"
BUILD = HERE / "build"
sys.path.insert(0, str(D / "gen"))
import sram8t as s8  # noqa: E402

LY = dict(MET1=(32, 0), VIA1=(33, 0), MET2=(34, 0), VIA2=(35, 0), MET3=(36, 0))
W1, W2, W3, PAD, CUT, ENC = 1.2, 1.2, 1.6, 2.0, 0.8, 0.6

# block placement: lower-left corners of the blocks' bounding boxes (die um)
CTRL_LL = (470.0, 560.0)
MACRO_LL = (1065.0, 567.4)
DECAP_LL = {"decap_vddw": (1290.0, 470.0), "decap_vdda": (1290.0, 770.0)}


def g(v):
    return int(round(v * 100)) * 10            # um -> dbu (1 nm) on the 0.01 um grid


class Top:
    def __init__(self, name):
        self.ly = kdb.Layout()
        self.ly.dbu = 0.001
        self.top = self.ly.create_cell(name)
        self.li = {k: self.ly.layer(*v) for k, v in LY.items()}
        self.wires = []                              # (net, layer, box) for the record

    def box(self, layer, x0, y0, x1, y1, net=None):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        self.top.shapes(self.li[layer]).insert(kdb.Box(g(x0), g(y0), g(x1), g(y1)))
        self.wires.append((net, layer, (round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2))))

    def hline(self, layer, xa, xb, y, w, net=None, ext=0.0):
        x0, x1 = sorted((xa, xb))
        self.box(layer, x0 - ext, y - w / 2, x1 + ext, y + w / 2, net)

    def vline(self, layer, x, ya, yb, w, net=None, ext=0.0):
        y0, y1 = sorted((ya, yb))
        self.box(layer, x - w / 2, y0 - ext, x + w / 2, y1 + ext, net)

    def via(self, kind, x, y, net=None):
        lo, hi = ("MET1", "MET2") if kind == "VIA1" else ("MET2", "MET3")
        self.box(kind, x - CUT / 2, y - CUT / 2, x + CUT / 2, y + CUT / 2, net)
        for m in (lo, hi):
            self.box(m, x - PAD / 2, y - PAD / 2, x + PAD / 2, y + PAD / 2, net)

    def via_array(self, kind, x0, y0, x1, y1, net=None):
        """As many cuts as fit in the box with 0.6 enclosure and 0.8 spacing (box metal drawn by caller)."""
        def axis(a, b):
            n = int(((b - a) - 2 * ENC + CUT) // (2 * CUT))
            if n < 1:
                raise SystemExit(f"{kind} array does not fit in {a}-{b}")
            span = n * CUT + (n - 1) * CUT
            start = (a + b) / 2 - span / 2
            return [start + k * 2 * CUT for k in range(n)]
        for cx in axis(x0, x1):
            for cy in axis(y0, y1):
                self.box(kind, cx, cy, cx + CUT, cy + CUT, net)

    def place(self, path: Path, ll):
        src = kdb.Layout()
        src.read(str(path))
        cell = src.top_cell()
        bb = cell.dbbox()
        new = self.ly.create_cell(cell.name)
        new.copy_tree(cell)
        dx, dy = round(ll[0] - bb.left, 2), round(ll[1] - bb.bottom, 2)
        self.top.insert(kdb.CellInstArray(new.cell_index(), kdb.Trans(kdb.Vector(g(dx), g(dy)))))
        return dx, dy, cell.name


def ctrl_pins():
    pins = {}
    for line in (D / "ctrl/macro/ecc_fi_ctrl_pins.txt").read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        name, layer, *v = line.split()
        pins[name] = (layer, tuple(float(t) for t in v))
    return pins


def main() -> int:
    BUILD.mkdir(exist_ok=True)
    pads = {p["pin"] if p["cell"] not in ("PVDD", "PVSS") else p["pad"]: p
            for p in json.loads((BUILD / "pad_pins.json").read_text())["pads"]}
    ctrl_gds = BUILD / "ecc_fi_ctrl.gds"
    with gzip.open(D / "ctrl/macro/ecc_fi_ctrl.gds.gz") as f, open(ctrl_gds, "wb") as o:
        shutil.copyfileobj(f, o)

    core = Top("ecc_sram_core")
    ocx, ocy, _ = core.place(ctrl_gds, CTRL_LL)
    omx, omy, _ = core.place(D / "sram/build/sram_macro.gds", MACRO_LL)
    dec = {n: core.place(D / f"sram/build/{n}.gds", ll) for n, ll in DECAP_LL.items()}
    cp = ctrl_pins()
    labels = []                                      # (pin name, x, y) on metal2 where the core meets the pad port

    def cpin(name):                                  # control pin centre and its side
        layer, (x1, y1, x2, y2) = cp[name]
        return layer, ocx + (x1 + x2) / 2, ocy + (y1 + y2) / 2

    def port(key):
        x1, y1, x2, y2 = pads[key]["rect"]
        return x1, y1, x2, y2, (x1 + x2) / 2, (y1 + y2) / 2

    um = 0.3                                         # lambda
    # ------------------------------------------------------------------ word lines
    wl = []
    for i in range(15):
        for kind, ly_ in (("WWL", 6), ("RWL", 85)):
            _, xc, yc = cpin(f"{kind}[{i}]")
            wl.append((f"{kind}{i}", yc, omy + s8.local_y(i, ly_) * um))
    wl.sort(key=lambda t: t[1])
    x_pin_r = ocx + cp["WWL[0]"][1][0]               # left edge of the control block's right pins
    x_stack = omx + (-25) * um                       # inside the macro's word line metal1 (-29..-11 lambda)
    for k, (net, yc, ym) in enumerate(wl):
        if abs(yc - ym) < 2.6:
            raise SystemExit(f"{net}: control pin and macro word line {abs(yc - ym):.2f} um apart, move the macro")
        x = 965.0 + 3.0 * k
        core.hline("MET3", x_pin_r, x, yc, W3, net, ext=0)
        core.via("VIA2", x, yc, net)
        core.vline("MET2", x, yc, ym, W2, net)
        core.via("VIA1", x, ym, net)
        core.hline("MET1", x, x_stack, ym, W1, net)

    # ------------------------------------------------------------------ bottom channel
    ctrl_bot = ocy + cp["DIN[2]"][1][3]              # top of the bottom pins
    mac_bot_top = omy + (-292 + 3) * um              # top of the macro's bottom pins
    s_in = [(pk, ctrl_name(pads[pads_key(pads, pk)]["pin"])) for pk in ("S1", "S2", "S3", "S4", "S5")]
    for k, (pk, cname) in enumerate(s_in):
        x1, y1, x2, y2, xp, _ = port(pads_key(pads, pk))
        _, xc, _ = cpin(cname)
        y = 450.0 + 4.0 * k
        core.vline("MET2", xp, y1, y + 1.0, W2, cname)
        core.via("VIA2", xp, y, cname)
        core.hline("MET3", xp, xc, y, 1.2, cname, ext=1.0)        # minimum width: these runs are long
        core.via("VIA2", xc, y, cname)
        core.vline("MET2", xc, y, ctrl_bot, W2, cname)
        labels.append((pads[pads_key(pads, pk)]["pin"], xp, y1 + 0.7))
    col = [("PRE_N", "PRE_N", omx - 12.0)]
    for c in range(8):
        col.append((f"SENSE[{c}]", f"SENSE{c}", omx + (60 * c + 15) * um))
        col.append((f"WD[{c}]", f"WD{c}", omx + (60 * c + 29) * um))
    col.sort(key=lambda t: cpin(t[0])[1])
    for k, (cname, mname, xm) in enumerate(col):
        _, xc, _ = cpin(cname)
        y = 474.0 + 4.0 * k
        core.vline("MET2", xc, y, ctrl_bot, W2, mname, ext=0)
        core.box("MET2", xc - W2 / 2, y - 1.0, xc + W2 / 2, y, mname)
        core.via("VIA2", xc, y, mname)
        core.hline("MET3", xc, xm, y, W3, mname, ext=1.0)
        core.via("VIA2", xm, y, mname)
        if mname == "PRE_N":
            yp = omy + (-166.5) * um                 # PRE_N rail centre (-170..-163 lambda)
            core.vline("MET2", xm, y, yp, W2, mname, ext=1.0)
            core.via("VIA1", xm, yp, mname)
            core.hline("MET1", xm, omx + (-17) * um, yp, W1, mname, ext=0)
        else:
            core.vline("MET2", xm, y - 1.0, mac_bot_top, W2, mname)

    # ------------------------------------------------------------------ W channel
    w_in = [(f"W{i}", ctrl_name(pads[pads_key(pads, f"W{i}")]["pin"])) for i in range(1, 8)]
    x_pin_l = ocx + cp["CLK"][1][2]                  # right edge of the left pins
    tracks = []
    for k, (pk, cname) in enumerate(w_in):
        x1, y1, x2, y2, _, yp = port(pads_key(pads, pk))
        _, _, yc = cpin(cname)
        tracks.append((pk, cname, yp, yc))
    order = choose_w_order(tracks)
    for k, (pk, cname, yp, yc) in zip(order, tracks):
        x = 446.0 + 3.0 * k
        core.box("MET2", 440.6, yp - 1.0, x + 1.0, yp + 1.0, cname)
        core.via("VIA1", x, yp, cname)
        core.vline("MET1", x, yp, yc, W1, cname, ext=0.6)
        core.via("VIA1", x, yc, cname)
        core.box("MET2", x - 1.0, yc - 1.0, x + 3.8, yc + 1.0, cname)
        core.via("VIA2", x + 2.8, yc, cname)
        core.hline("MET3", x + 2.8, x_pin_l, yc, W3, cname, ext=0)
        labels.append((pads[pads_key(pads, pk)]["pin"], 441.3, yp))

    # ------------------------------------------------------------------ top channel
    ctrl_top = ocy + cp["DOUT[0]"][1][1]             # bottom of the top pins
    outs = [(ctrl_name(pads[pads_key(pads, pk)]["pin"]), pk) for pk in ("N5", "N6", "N7", "E5", "E6", "E7")]
    outs.sort(key=lambda t: cpin(t[0])[1])
    lane = {"E5": 1452.0, "E6": 1448.0, "E7": 1444.0}
    for k, (cname, pk) in enumerate(outs):
        _, xc, _ = cpin(cname)
        x1, y1, x2, y2, xp, yp = port(pads_key(pads, pk))
        y = 1080.0 + 4.0 * k
        core.vline("MET2", xc, ctrl_top, y, W2, cname, ext=0)
        core.box("MET2", xc - W2 / 2, y, xc + W2 / 2, y + 1.0, cname)
        core.via("VIA2", xc, y, cname)
        if pk.startswith("N"):
            core.hline("MET3", xc, xp, y, W3, cname, ext=1.0)
            core.via("VIA2", xp, y, cname)
            core.vline("MET2", xp, y - 1.0, y2, W2, cname)
            labels.append((pads[pads_key(pads, pk)]["pin"], xp, y2 - 0.7))
        else:
            xl = lane[pk]
            core.hline("MET3", xc, xl, y, W3, cname, ext=1.0)
            core.via("VIA2", xl, y, cname)
            core.vline("MET2", xl, y, yp, W2, cname, ext=0.6)
            core.box("MET2", xl - 0.6, yp - W2 / 2, x2, yp + W2 / 2, cname)
            labels.append((pads[pads_key(pads, pk)]["pin"], x1 + 0.7, yp))
    n_in = [(pk, ctrl_name(pads[pads_key(pads, pk)]["pin"])) for pk in ("N1", "N2", "N3")]
    for k, (pk, cname) in enumerate(n_in):
        _, xc, _ = cpin(cname)
        x1, y1, x2, y2, xp, _ = port(pads_key(pads, pk))
        y = 1108.0 + 4.0 * k
        core.vline("MET2", xp, y - 1.0, y2, W2, cname)
        core.via("VIA2", xp, y, cname)
        core.hline("MET3", xp, xc, y, W3, cname, ext=1.0)
        core.via("VIA2", xc, y, cname)
        core.vline("MET2", xc, ctrl_top, y, W2, cname, ext=0)
        core.box("MET2", xc - W2 / 2, y, xc + W2 / 2, y + 1.0, cname)
        labels.append((pads[pads_key(pads, pk)]["pin"], xp, y2 - 0.7))

    # ------------------------------------------------------------------ supplies
    def strap_via(kind, x0, y0, x1, y1, net):
        core.via_array(kind, x0, y0, x1, y1, net)
    # VSS: metal3 strap y 542-556
    gx0, gx1 = ocx + 471.3 + 1.0, ocx + 480.3 - 1.0          # inside the gnd spine (metal1 471.3-480.3)
    core.box("MET3", gx0, 542.0, 1456.0, 556.0, "VSS")
    core.box("MET2", gx0, 542.0, gx1, ocy + 9.0, "VSS")
    strap_via("VIA2", gx0, 542.0, gx1, 556.0, "VSS")
    strap_via("VIA1", gx0, ocy + 1.0, gx1, ocy + 9.0, "VSS")
    vx0, vx1 = omx + 145.8, omx + 149.4                      # macro VSS bus
    s6 = port(pads_key(pads, "S6"))
    core.box("MET2", vx0, s6[1], vx1, mac_bot_top, "VSS")
    strap_via("VIA2", vx0, 542.0, vx1, 556.0, "VSS")
    labels.append(("VSS", (vx0 + vx1) / 2, s6[1] + 0.7))
    dx0 = DECAP_LL["decap_vddw"][0]                          # decap VSS buses (left, metal2 3.6 wide)
    core.box("MET2", dx0, DECAP_LL["decap_vddw"][1] + 280.0, dx0 + 3.6, DECAP_LL["decap_vdda"][1] + 5.0, "VSS")
    strap_via("VIA2", dx0, 542.0, dx0 + 3.6, 552.0, "VSS")    # below the decap's own rail via at 553.4
    e1 = port(pads_key(pads, "E1"))
    core.box("MET2", 1448.0, 542.0, e1[2], 556.0, "VSS")
    strap_via("VIA2", 1448.0, 542.0, 1456.0, 556.0, "VSS")
    labels.append(("VSS", e1[0] + 0.7, 549.0))
    # VDD: N4 -> metal3 y 1438-1450 -> control vdd spine; S7 -> macro VDD bus
    n4 = port(pads_key(pads, "N4"))
    core.box("MET2", 930.0, 1438.0, 970.0, n4[3], "VDD")
    strap_via("VIA2", 930.0, 1438.0, 970.0, 1450.0, "VDD")
    sx0, sx1 = ocx - 9.3 + 1.0, ocx - 0.3 - 1.0              # inside the vdd spine (metal1 -9.3..-0.3)
    core.box("MET3", sx0, 1438.0, 970.0, 1450.0, "VDD")
    strap_via("VIA2", sx0, 1438.0, sx1, 1450.0, "VDD")
    core.box("MET2", sx0, ocy + 461.0, sx1, 1450.0, "VDD")
    strap_via("VIA1", sx0, ocy + 461.0, sx1, ocy + 469.7, "VDD")
    labels.append(("VDD", 950.0, n4[3] - 0.7))
    s7 = port(pads_key(pads, "S7"))
    px0, px1 = omx + 156.6, omx + 160.2                      # macro VDD bus
    core.box("MET2", s7[0], s7[1], s7[2], 456.0, "VDD")
    strap_via("VIA2", s7[0], 446.0, s7[2], 456.0, "VDD")
    core.box("MET3", px0 - 0.6, 446.0, s7[2], 456.0, "VDD")
    strap_via("VIA2", px0, 446.0, px1, 456.0, "VDD")
    core.box("MET2", px0, 446.0, px1, mac_bot_top, "VDD")
    labels.append(("VDD", s7[4], s7[1] + 0.7))
    # VDDW: E2 -> decap bus (metal2) ; decap -> macro VDDW bus (metal3 y 576-590)
    e2 = port(pads_key(pads, "E2"))
    bx0 = DECAP_LL["decap_vddw"][0] + 148.8                   # decap supply bus (right, 3.6 wide)
    core.box("MET2", bx0, e2[1] + 1.35, e2[2], e2[3] - 1.35, "VDDW")
    wx0, wx1 = omx + 162.0, omx + 165.6
    core.box("MET3", wx0, 576.0, bx0 + 3.6, 590.0, "VDDW")
    strap_via("VIA2", wx0, 576.0, wx1, 590.0, "VDDW")
    strap_via("VIA2", bx0, 576.0, bx0 + 3.6, 590.0, "VDDW")
    labels.append(("VDDW", e2[0] + 0.7, e2[5]))
    # VDDA: E3 -> decap bus ; decap -> macro VDDA bus between two of the array's bus vias
    e3 = port(pads_key(pads, "E3"))
    core.box("MET2", bx0, e3[1] + 1.35, e3[2], e3[3] - 1.35, "VDDA")
    # keep the strap's VIA2s away from the VIA1s already on both buses (no VIA2 on VIA1, 0.6 um apart):
    # the array's VDDA rail vias on the macro bus and the decap's supply rail vias on the decap bus
    taken = [omy + s8.local_y(rr, 56.5) * um for rr in range(15)]
    oy_d = DECAP_LL["decap_vdda"][1] + 1.8
    taken += [oy_d + (k * 68 + 60) * um for k in range(7)]
    cands = [840.0 + 0.5 * i for i in range(130)]
    ym = max(cands, key=lambda y: min(abs(y - t) for t in taken))
    if min(abs(ym - t) for t in taken) < 5.0 + 1.05 + 0.6:
        raise SystemExit("no room for the VDDA strap between the bus vias")
    ax0, ax1 = omx + 151.2, omx + 154.8
    core.box("MET3", ax0, ym - 5.0, bx0 + 3.6, ym + 5.0, "VDDA")
    strap_via("VIA2", ax0, ym - 5.0, ax1, ym + 5.0, "VDDA")
    strap_via("VIA2", bx0, ym - 5.0, bx0 + 3.6, ym + 5.0, "VDDA")
    labels.append(("VDDA", e3[0] + 0.7, e3[5]))

    # ------------------------------------------------------------------ write
    opt = kdb.SaveLayoutOptions()
    core.ly.write(str(BUILD / "ecc_sram_core.gds"), opt)
    ring = kdb.Layout()
    ring.read(str(BUILD / "ecc_sram_Pad.gds"))
    chip = kdb.Layout()
    chip.read(str(BUILD / "ecc_sram_core.gds"))
    chip.read(str(BUILD / "ecc_sram_Pad.gds"))                # merges cells; two top cells now
    top = chip.create_cell("ecc_sram_Top")
    for c in [c for c in chip.top_cells() if c.name != "ecc_sram_Top"]:
        top.insert(kdb.CellInstArray(c.cell_index(), kdb.Trans()))
    chip.write(str(BUILD / "ecc_sram_Top.gds"), opt)
    json.dump(dict(unit="um", labels=[dict(name=n, x=round(x, 2), y=round(y, 2)) for n, x, y in labels],
                   blocks=dict(ctrl=[ocx, ocy], macro=[omx, omy], **{k: [v[0], v[1]] for k, v in dec.items()})),
              open(BUILD / "ecc_sram_nets.json", "w"), indent=1)
    bb = top.dbbox()
    print(f"wrote {BUILD / 'ecc_sram_Top.gds'} ({bb.width():.1f} x {bb.height():.1f} um), core shapes {len(core.wires)},"
          f" pin labels {len(labels)}; control at ({ocx}, {ocy}), macro at ({omx}, {omy})")
    return 0


def ctrl_name(pin):
    """Pad pin name (pins.csv) -> control block pin name: DIN2 -> DIN[2], SEC -> SEC_FLAG."""
    import re
    if pin in ("SEC", "DED"):
        return pin + "_FLAG"
    m = re.fullmatch(r"([A-Z_]+?)(\d+)", pin)
    return f"{m[1]}[{m[2]}]" if m else pin


def pads_key(pads, pk):
    for k, p in pads.items():
        if p["pad"] == pk:
            return k
    raise KeyError(pk)


def choose_w_order(tracks):
    """Track index per W net so that no pad-side metal2 run (y of the pad, from the ring to its track) comes
    within 3 um of another net's metal2 bridge (y of the control pin, at that net's track)."""
    import itertools
    n = len(tracks)
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            xi = 446.0 + 3.0 * perm[i]
            for j in range(n):
                if i == j:
                    continue
                xj = 446.0 + 3.0 * perm[j]
                if xj - 1.0 < xi + 1.0 and abs(tracks[i][2] - tracks[j][3]) < 3.2:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return list(perm)
    raise SystemExit("no W track order without metal2 conflicts")


if __name__ == "__main__":
    sys.exit(main())
