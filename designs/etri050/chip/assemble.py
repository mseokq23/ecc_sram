#!/usr/bin/env python3
"""Top-level assembly of the ECC 8T SRAM chip (KLayout): ETRI GPIO pad ring, control block (qflow macro),
SRAM macro (array + column circuits), decoupling for VDDA and VDDW, the reliability monitor (canary latches,
ring oscillator bank, divider) and the wiring between them.

  python3 designs/etri050/chip/assemble.py        (after run_pad_ring.sh, colper.py, decap.py, freeze_macro.sh
                                                   for ecc_fi_ctrl and ro_div, canary.py, robank.py)

Writes build/ecc_sram_Top.gds (the chip), build/ecc_sram_core.gds (the same without the pad ring, for LVS)
and build/ecc_sram_nets.json (where each pad port meets the core wiring: the LVS pin labels).

Floorplan (die um, core window 442-1458):
  control block   lower-left (470, 560); inputs from W pads on its left side, from S pads on its bottom
                  left, from N pads on its top left; outputs and the monitor pins on its top; word lines on
                  its right; PRE_N, WD and SENSE on its bottom right
  SRAM macro      lower-left (1065, 567.4), word line pins (left) facing the control block
  decoupling      VDDW 57 pF at (1290, 470), VDDA 28.5 pF at (1290, 770), supply buses toward the E pads
  monitor         over the top channel, bottoms in line (Y_BLK, set by the channel height): canary latches
                  (x 554), RO bank (x 829), divider ro_div (x 1184)
Wiring (three layers, each net on its own track, so no two nets share a layer where they cross):
  word lines      control pin -> metal3 -> metal2 track (x 968 + 3 i) -> metal1 into the macro's word line
                  contact stack
  bottom channel  S pad inputs on metal3 tracks y 450-466 (below), PRE_N/WD/SENSE on tracks y 474-538,
                  metal2 up and down at the pins
  W channel       pad port -> metal2 -> metal1 track (x 446 + 3 i) -> metal2/metal3 into the control pin
  top channel     metal3 tracks from y 1086 (4 um pitch, track order from channel_tracks()): the control
                  block's outputs and monitor pins below, the monitor ports above; N pad outputs go east to
                  metal2 lines at x 1435-1441, up to metal3 y 1440-1448 and west to their pads; E pad
                  outputs go down or up metal2 lanes at x 1444-1452
  FI_POS          N pad inputs: metal2 straight up from the control pins (west of the canary block) to
                  metal3 y 1418-1426, east to their pads
  supplies        VSS: metal3 strap y 542-556 from the control block's gnd spine to the macro VSS bus,
                  the decap VSS buses and pads S6, E1; VDD: N4 -> metal3 y 1438-1450 -> control block vdd
                  spine, S7 -> macro VDD bus; VDDW: E2 -> decap -> macro (metal3 y 576-590); VDDA: E3 ->
                  decap -> macro (metal3 between two of the array's VDDA bus vias)
                  monitor (straps between the top channel and the blocks): VDD metal1 from the control
                  block's vdd spine; VSS metal3 from the control block's gnd spine and the macro VSS bus;
                  VDDA metal3 from the macro VDDA bus (the canary latches sit on the array supply)
Rules used (rule document v1.1): metal1 >= 0.8, metal2 >= 1.0, metal3 >= 1.2 wide; cuts 0.8 with 0.6
enclosure, cut spacing 0.8, no VIA2 on VIA1; drawn here: metal1 1.2, metal2 1.2, metal3 1.6, via pads 2.0.
Every coordinate is rounded to 0.01 um. Straps stay narrower than 10 um (no wide-metal spacing).
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
# monitor blocks: x of the bounding box's left edge; y (bottom) follows the top channel's height
#   canary  CAN[7] port right over the control block's CAN[7] pin (a straight line); the others take tracks
#   ro_div  the macro's VSS and VDDA buses come up through the channel at x 1226-1235: its TAP pins stay
#           west of them, its EN and DIV pins east
MON_X = {"canary": 554.0, "robank": 829.0, "ro_div": 1184.0}
CH_Y0, CH_PITCH = 1086.0, 4.0                       # top channel: first metal3 track, pitch
WL_X0 = 968.0                                        # word line metal2 tracks x WL_X0 + 3 i (clear of the gnd spine)
N_OUT = {"N5": (1435.0, 1440.0), "N6": (1438.0, 1444.0), "N7": (1441.0, 1448.0)}   # metal2 line x, metal3 y
E_LANE = {"E5": 1452.0, "E6": 1448.0, "E7": 1444.0}
FI_BAND = {"N1": 1418.0, "N2": 1422.0, "N3": 1426.0}                               # metal3 y per N input


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


def ctrl_pins(name="ecc_fi_ctrl"):
    pins = {}
    for line in (D / f"ctrl/macro/{name}_pins.txt").read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        pname, layer, *v = line.split()
        pins[pname] = (layer, tuple(float(t) for t in v))
    return pins


def stray_metal(path, layer, keep):
    """Merged shapes of one metal of a qflow macro that reach outside the box keep (block coordinates): the
    router sometimes takes a net around a pin through the strip between the pins and the block edge, where
    the chip wiring leaves the pin. Returns [(polygon region, bbox)]."""
    lay = kdb.Layout()
    lay.read(str(path))
    c = lay.top_cell()
    reg = kdb.Region(c.begin_shapes_rec(lay.layer(*LY[layer]))).merged()
    k = kdb.Region(kdb.DBox(*keep).to_itype(lay.dbu))
    out = []
    for p in reg.each():
        r = kdb.Region(p)
        if not (r - k).is_empty():
            out.append((r, p.bbox().to_dtype(lay.dbu), lay.dbu))
    return out


def hits(stray, box, pin, gap):
    """Stray shapes (not the pin's own: those touch the pin) closer than gap to box (block coordinates)."""
    out = []
    for r, bb_, dbu in stray:
        if r.interacting(kdb.Region(kdb.DBox(*pin).to_itype(dbu))).count():
            continue
        b = kdb.DBox(box[0] - gap, box[1] - gap, box[2] + gap, box[3] + gap)
        if not (r & kdb.Region(b.to_itype(dbu))).is_empty():
            out.append(bb_)
    return out


def block_pins(name):
    """Ports of a monitor block from its pins JSON (block coordinates): name -> (layer, box)."""
    j = json.loads((D / f"monitor/build/{name}_pins.json").read_text())
    return {k: (v["layer"], tuple(v["box"])) for k, v in j["pins"].items()}


def channel_tracks(nets, through, d_min=3.0, gap=4.0):
    """Track rows (top first) for the top channel: constrained left-edge.

    nets: {name: {"bot": [x], "top": [x]}}: x of the metal2 lines that come up from below (control pins,
    lanes going down) and go up from the track (block ports, lines going up). Each net is one metal3 track
    from its smallest to its largest x with a via2 at every x. A top x closer than d_min to another net's
    bottom x puts that net's track above the other's (vertical constraint); two tops or two bottoms of
    different nets that close cannot be routed and stop the script, as does any x within 2 um of a through
    column (metal2 that crosses the whole channel: x0, x1). Nets share a track when their spans are gap
    apart."""
    cols = [(x, n, s) for n, v in nets.items() for s in ("bot", "top") for x in v[s]]
    for x, n, s in cols:
        for a, b in through:
            if a - 2.0 < x < b + 2.0:
                raise SystemExit(f"top channel: {n} at x {x:.2f} is within 2 um of the line at {a:.2f}-{b:.2f}")
    above = {n: set() for n in nets}
    for i, (x1, n1, s1) in enumerate(cols):
        for x2, n2, s2 in cols[i + 1:]:
            dx = round(abs(x1 - x2), 3)
            if n1 == n2:
                if 0 < dx < 1.6:
                    raise SystemExit(f"top channel: {n1} has two vias {dx:.2f} um apart")
                continue
            if dx >= d_min:
                continue
            if s1 == s2:
                raise SystemExit(f"top channel: {n1} and {n2} at x {x1:.2f}, {x2:.2f} on the same side")
            t, b = (n1, n2) if s1 == "top" else (n2, n1)
            above[b].add(t)
    span = {n: (min(v["bot"] + v["top"]), max(v["bot"] + v["top"])) for n, v in nets.items()}
    rows, left = [], set(nets)
    while left:
        ready = sorted((n for n in left if not (above[n] & left)), key=lambda n: span[n][0])
        if not ready:
            raise SystemExit(f"top channel: vertical constraints form a cycle among {sorted(left)}")
        row, last = [], None
        for n in ready:
            if last is None or span[n][0] - last >= gap:
                row.append(n)
                last = span[n][1]
        rows.append(row)
        left -= set(row)
    return rows, span


def main() -> int:
    BUILD.mkdir(exist_ok=True)
    pads = {p["pin"] if p["cell"] not in ("PVDD", "PVSS") else p["pad"]: p
            for p in json.loads((BUILD / "pad_pins.json").read_text())["pads"]}
    gds = {}
    for name in ("ecc_fi_ctrl", "ro_div"):
        gds[name] = BUILD / f"{name}.gds"
        with gzip.open(D / f"ctrl/macro/{name}.gds.gz") as f, open(gds[name], "wb") as o:
            shutil.copyfileobj(f, o)
    gds["canary"] = D / "monitor/build/canary_flat.gds"
    gds["robank"] = D / "monitor/build/robank_flat.gds"

    core = Top("ecc_sram_core")
    ocx, ocy, _ = core.place(gds["ecc_fi_ctrl"], CTRL_LL)
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

    def spine(name, which):                          # x range of a qflow block's vdd / gnd spine (metal1)
        _, (x1, _, x2, _) = ctrl_pins(name)[which]
        return x1, x2

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
    if WL_X0 - 1.0 - (ocx + spine("ecc_fi_ctrl", "gnd")[1]) < 0.9:
        raise SystemExit("word line via1 pads too close to the control block's gnd spine")
    # the pins' column (block x 482.4-483.6): metal3 of the block east of it belongs to routes that go round
    # a pin; a word line that would cross one leaves its pin on metal2 instead (via2 on the pin)
    cb = (-9.3, -3.65, 483.65, 513.5)
    stray3 = stray_metal(gds["ecc_fi_ctrl"], "MET3", cb)
    wl_x = {net: WL_X0 + 3.0 * k for k, (net, _, _) in enumerate(wl)}
    span_y = {net: (min(yc, ym), max(yc, ym)) for net, yc, ym in wl}
    jumped = []
    for k, (net, yc, ym) in enumerate(wl):
        if abs(yc - ym) < 2.6:
            raise SystemExit(f"{net}: control pin and macro word line {abs(yc - ym):.2f} um apart, move the macro")
        x = wl_x[net]
        name = ("WWL" if net.startswith("WWL") else "RWL") + f"[{net[3:]}]"
        _, (px1, py1, px2, py2) = cp[name]
        yl = yc - ocy
        if hits(stray3, (px1, yl - W3 / 2, 487.0, yl + W3 / 2), (px1, py1, px2, py2), 1.0):
            for other, (a, b) in span_y.items():
                if other != net and wl_x[other] < x and a - 2.2 < yc < b + 2.2:
                    raise SystemExit(f"{net}: metal2 from the pin would cross {other}'s track")
            xp = ocx + (px1 + px2) / 2
            core.via("VIA2", xp, yc, net)
            core.hline("MET2", xp, x, yc, W2, net, ext=0.6)
            jumped.append(net)
        else:
            core.hline("MET3", x_pin_r, x, yc, W3, net, ext=0)
            core.via("VIA2", x, yc, net)
        core.vline("MET2", x, yc, ym, W2, net)
        core.via("VIA1", x, ym, net)
        core.hline("MET1", x, x_stack, ym, W1, net)

    # ------------------------------------------------------------------ bottom channel
    ctrl_bot = ocy + cp["DIN[2]"][1][3]              # top of the bottom pins
    mac_bot_top = omy + (-292 + 3) * um              # top of the macro's bottom pins
    stray2 = stray_metal(gds["ecc_fi_ctrl"], "MET2", (-9.3, -3.7, 486.6, 513.5))

    def from_bottom_pin(cname, xc, y_low, net):
        """Metal2 from y_low up into a bottom pin; where a route of the block runs under the pin row, a via2
        on the pin and metal3 down past it, then a via2 back to metal2."""
        _, (px1, py1, px2, py2) = cp[cname]
        xl = xc - ocx
        under = hits(stray2, (xl - W2 / 2, -12.0, xl + W2 / 2, py2), (px1, py1, px2, py2), 1.0)
        if not under:
            core.vline("MET2", xc, y_low, ctrl_bot, W2, net)
            return
        yj = ocy + min(b.bottom for b in under) - 2.4       # via2 pad 1.4 um below the stray route
        yp = ocy + (py1 + py2) / 2
        core.via("VIA2", xc, yp, net)
        core.vline("MET3", xc, yj, yp, W3, net)
        core.via("VIA2", xc, yj, net)
        core.vline("MET2", xc, y_low, yj, W2, net)
        jumped.append(net)
    s_in = [(pk, ctrl_name(pads[pads_key(pads, pk)]["pin"])) for pk in ("S1", "S2", "S3", "S4", "S5")]
    for k, (pk, cname) in enumerate(s_in):
        x1, y1, x2, y2, xp, _ = port(pads_key(pads, pk))
        _, xc, _ = cpin(cname)
        y = 450.0 + 4.0 * k
        core.vline("MET2", xp, y1, y + 1.0, W2, cname)
        core.via("VIA2", xp, y, cname)
        core.hline("MET3", xp, xc, y, 1.2, cname, ext=1.0)        # minimum width: these runs are long
        core.via("VIA2", xc, y, cname)
        from_bottom_pin(cname, xc, y, cname)
        labels.append((pads[pads_key(pads, pk)]["pin"], xp, y1 + 0.7))
    col = [("PRE_N", "PRE_N", omx - 12.0)]
    for c in range(8):
        col.append((f"SENSE[{c}]", f"SENSE{c}", omx + (60 * c + 15) * um))
        col.append((f"WD[{c}]", f"WD{c}", omx + (60 * c + 29) * um))
    col.sort(key=lambda t: cpin(t[0])[1])
    for k, (cname, mname, xm) in enumerate(col):
        _, xc, _ = cpin(cname)
        y = 474.0 + 4.0 * k
        from_bottom_pin(cname, xc, y, mname)
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

    # ------------------------------------------------------------------ top channel and monitor blocks
    ctrl_top = ocy + cp["DOUT[0]"][1][1]             # bottom of the top pins
    vdd_x = spine("ecc_fi_ctrl", "vdd")
    gnd_x = spine("ecc_fi_ctrl", "gnd")
    bb = {}
    for name in ("canary", "robank", "ro_div"):
        lay = kdb.Layout()
        lay.read(str(gds[name]))
        bb[name] = lay.top_cell().dbbox()
    dxm = {n: round(MON_X[n] - bb[n].left, 2) for n in MON_X}           # block origin x (die)
    canp, robp = block_pins("canary"), block_pins("robank")
    divp = ctrl_pins("ro_div")

    def bx(name, pin):                                # die x of a monitor port's centre
        layer, (x1, _, x2, _) = (canp if name == "canary" else robp if name == "robank" else divp)[pin]
        return round(dxm[name] + (x1 + x2) / 2, 2)

    def cx(name):
        return round(cpin(name)[1], 2)

    outs = {"N5": "DED_FLAG", "N6": "SEC_FLAG", "N7": "DOUT[3]", "E5": "DOUT[0]", "E6": "DOUT[1]",
            "E7": "DOUT[2]"}
    for pk, cname in outs.items():
        if ctrl_name(pads[pads_key(pads, pk)]["pin"]) != cname:
            raise SystemExit(f"{pk} is not {cname} in pins.csv")
    nets = {"CRD_N": dict(bot=[cx("CRD_N")], top=[bx("canary", "CRD_N")]),
            "CSET": dict(bot=[cx("CSET")], top=[bx("canary", "CSET")])}
    for k in range(7):
        nets[f"CAN{k}"] = dict(bot=[cx(f"CAN[{k}]")], top=[bx("canary", f"CAN{k}")])
    if abs(cx("CAN[7]") - bx("canary", "CAN7")) > 0.005:
        raise SystemExit(f"canary CAN7 port {bx('canary', 'CAN7')} is not over the control pin {cx('CAN[7]')}")
    for k in range(3):
        nets[f"RO_EN{k}"] = dict(bot=[cx(f"RO_EN[{k}]")], top=[bx("robank", f"en{k}"), bx("ro_div", f"EN[{k}]")])
        nets[f"TAP{k}"] = dict(bot=[], top=[bx("robank", f"in{k}"), bx("ro_div", f"TAP[{k}]")])
    nets["RO_DIV"] = dict(bot=[cx("RO_DIV")], top=[bx("ro_div", "DIV")])
    for pk, cname in outs.items():
        n = ctrl_name(pads[pads_key(pads, pk)]["pin"]).replace("_FLAG", "").replace("[", "").replace("]", "")
        if pk in N_OUT:
            nets[n] = dict(bot=[cx(cname)], top=[N_OUT[pk][0]])
        elif pk == "E5":                                                 # DOUT0: its lane goes down
            nets[n] = dict(bot=[cx(cname), E_LANE[pk]], top=[])
        else:
            nets[n] = dict(bot=[cx(cname)], top=[E_LANE[pk]])
    fi = {pk: ctrl_name(pads[pads_key(pads, pk)]["pin"]) for pk in FI_BAND}
    # metal2 that crosses the whole channel: FI_POS lines, CAN7, the gnd spine riser, the macro VSS / VDDA buses
    g_riser = (ocx + gnd_x[0] + 1.0, ocx + gnd_x[1] - 1.0)
    m_vss, m_vdda = (omx + 145.8, omx + 149.4), (omx + 151.2, omx + 154.8)
    through = [(cx(c) - W2 / 2, cx(c) + W2 / 2) for c in fi.values()]
    through += [(cx("CAN[7]") - W2 / 2, cx("CAN[7]") + W2 / 2), g_riser, m_vss, m_vdda]
    rows, span = channel_tracks(nets, through)
    n_tr = len(rows)
    y_tr = {n: CH_Y0 + CH_PITCH * (n_tr - 1 - i) for i, row in enumerate(rows) for n in row}
    y_last = CH_Y0 + CH_PITCH * (n_tr - 1)
    ya = y_last + 4.0                                # VDDA strap (metal3) ya .. ya+4
    ys = (ya + 5.2, ya + 13.2)                       # VSS strap (metal3) and VDD strap (metal1)
    y_blk = round(ya + 20.2, 2)                      # monitor blocks' bottom edge
    dym = {}
    for name in ("canary", "robank", "ro_div"):
        dxp, dym[name], _ = core.place(gds[name], (MON_X[name], y_blk))
        if abs(dxp - dxm[name]) > 0.005:
            raise SystemExit(f"{name}: placed at x offset {dxp}, expected {dxm[name]}")

    def by_top(name, pin):                           # die y of a monitor port's top edge
        layer, (_, _, _, y2) = (canp if name == "canary" else robp if name == "robank" else divp)[pin]
        return round(dym[name] + y2, 2)

    # metal2 line ends: control pins from their bottom edge, block ports up to their top edge
    ends = {}
    for k in range(7):
        ends[(f"CAN{k}", bx("canary", f"CAN{k}"))] = by_top("canary", f"CAN{k}")
    for p in ("CRD_N", "CSET"):
        ends[(p, bx("canary", p))] = by_top("canary", p)
    for k in range(3):
        ends[(f"RO_EN{k}", bx("robank", f"en{k}"))] = by_top("robank", f"en{k}")
        ends[(f"RO_EN{k}", bx("ro_div", f"EN[{k}]"))] = by_top("ro_div", f"EN[{k}]")
        ends[(f"TAP{k}", bx("robank", f"in{k}"))] = by_top("robank", f"in{k}")
        ends[(f"TAP{k}", bx("ro_div", f"TAP[{k}]"))] = by_top("ro_div", f"TAP[{k}]")
    ends[("RO_DIV", bx("ro_div", "DIV"))] = by_top("ro_div", "DIV")
    for pk in N_OUT:
        ends[(nets_name(pads, pk), N_OUT[pk][0])] = N_OUT[pk][1]
    for pk, xl in E_LANE.items():
        yp = port(pads_key(pads, pk))[5]
        ends[(nets_name(pads, pk), xl)] = yp - 0.6 if pk == "E5" else yp + 0.6
    for n, v in nets.items():
        y = y_tr[n]
        x0, x1 = span[n]
        core.hline("MET3", x0, x1, y, W3, n, ext=1.0)
        for x in v["bot"]:
            core.via("VIA2", x, y, n)
            core.vline("MET2", x, ends.get((n, x), ctrl_top), y, W2, n)
        for x in v["top"]:
            core.via("VIA2", x, y, n)
            core.vline("MET2", x, y, ends[(n, x)], W2, n)
    core.vline("MET2", cx("CAN[7]"), ctrl_top, by_top("canary", "CAN7"), W2, "CAN7")
    # N pad outputs: metal3 west at y N_OUT[pk][1] to the pad, metal2 up into its port
    for pk, (xl, yb) in N_OUT.items():
        n = nets_name(pads, pk)
        x1, y1, x2, y2, xp, _ = port(pads_key(pads, pk))
        core.via("VIA2", xl, yb, n)
        core.hline("MET3", xp, xl, yb, W3, n, ext=1.0)
        core.via("VIA2", xp, yb, n)
        core.vline("MET2", xp, yb, y2, W2, n)
        labels.append((pads[pads_key(pads, pk)]["pin"], xp, y2 - 0.7))
    for pk, xl in E_LANE.items():                    # E pad outputs: metal2 east into the port
        x1, y1, x2, y2, xp, yp = port(pads_key(pads, pk))
        core.box("MET2", xl - 0.6, yp - W2 / 2, x2, yp + W2 / 2, nets_name(pads, pk))
        labels.append((pads[pads_key(pads, pk)]["pin"], x1 + 0.7, yp))
    # N pad inputs FI_POS: metal2 up from the control pin to metal3 y FI_BAND, east to the pad, metal2 up
    for pk, cname in fi.items():
        x1, y1, x2, y2, xp, _ = port(pads_key(pads, pk))
        xc, yb = cx(cname), FI_BAND[pk]
        core.vline("MET2", xc, ctrl_top, yb, W2, cname)
        core.via("VIA2", xc, yb, cname)
        core.hline("MET3", xc, xp, yb, W3, cname, ext=1.0)
        core.via("VIA2", xp, yb, cname)
        core.vline("MET2", xp, yb, y2, W2, cname)
        labels.append((pads[pads_key(pads, pk)]["pin"], xp, y2 - 0.7))

    # ------------------------------------------------------------------ supplies
    def strap_via(kind, x0, y0, x1, y1, net):
        core.via_array(kind, x0, y0, x1, y1, net)
    # VSS: metal3 strap y 542-556
    gx0, gx1 = ocx + gnd_x[0] + 1.0, ocx + gnd_x[1] - 1.0     # inside the gnd spine (metal1)
    mac_vss = omx + 145.8
    core.box("MET3", gx0, 542.0, 1456.0, 556.0, "VSS")
    core.box("MET2", gx0, 542.0, gx1, ocy + 9.0, "VSS")
    strap_via("VIA2", gx0, 542.0, gx1, 556.0, "VSS")
    strap_via("VIA1", gx0, ocy + 1.0, gx1, ocy + 9.0, "VSS")
    vx0, vx1 = m_vss                                         # macro VSS bus
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
    # VDD: N4 -> metal3 y 1438-1450 -> metal2 down to the control block's vdd spine (metal1 drawn up from it)
    n4 = port(pads_key(pads, "N4"))
    core.box("MET2", 930.0, 1438.0, 970.0, n4[3], "VDD")
    strap_via("VIA2", 930.0, 1438.0, 970.0, 1450.0, "VDD")
    sx0, sx1 = ocx + vdd_x[0] + 1.0, ocx + vdd_x[1] - 1.0     # inside the vdd spine
    v1y = (ctrl_top + 2.4, ctrl_top + 10.4)                   # via1 rows on the spines' metal1, above the block
    core.box("MET3", sx0, 1438.0, 970.0, 1450.0, "VDD")
    strap_via("VIA2", sx0, 1438.0, sx1, 1450.0, "VDD")
    core.box("MET2", sx0, v1y[0], sx1, 1450.0, "VDD")
    strap_via("VIA1", sx0, v1y[0], sx1, v1y[1], "VDD")
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
    ax0, ax1 = m_vdda
    core.box("MET3", ax0, ym - 5.0, bx0 + 3.6, ym + 5.0, "VDDA")
    strap_via("VIA2", ax0, ym - 5.0, ax1, ym + 5.0, "VDDA")
    strap_via("VIA2", bx0, ym - 5.0, bx0 + 3.6, ym + 5.0, "VDDA")
    labels.append(("VDDA", e3[0] + 0.7, e3[5]))

    # ------------------------------------------------------------------ monitor supplies
    mac_top = omy + bb_top(D / "sram/build/sram_macro.gds") - 3.0       # 2 um into the macro's bus tops
    can_vdd, can_vdda, can_vss = (canp[p][1] for p in ("VDD", "VDDA", "VSS"))
    rob_vdd, rob_vss = robp["VDD"][1], robp["VSS"][1]
    dvdd, dgnd = spine("ro_div", "vdd"), spine("ro_div", "gnd")
    xc0 = dxm["canary"]
    # VDD, metal1 strap ys: control block vdd spine (drawn up from its top end), canary VDD rail, RO bank VDD,
    # ro_div vdd spine (drawn down from its bottom end)
    top_m1 = ocy + 505.0                                       # inside the spines' top ends (506.7)
    core.box("MET1", ocx + vdd_x[0], top_m1, ocx + vdd_x[1], ys[1], "VDD")
    core.box("MET1", ocx + vdd_x[0], ys[0], dxm["ro_div"] + dvdd[1], ys[1], "VDD")
    core.box("MET1", xc0 + can_vdd[0], ys[0], xc0 + can_vdd[2], dym["canary"] + can_vdd[3], "VDD")
    core.box("MET1", dxm["robank"] + rob_vdd[0], ys[0], dxm["robank"] + rob_vdd[2], by_top("robank", "VDD"), "VDD")
    sp_bot = dym["ro_div"] + 0.3 + 2.0                         # 2 um into the spines (they start at 0.3)
    core.box("MET1", dxm["ro_div"] + dvdd[0], ys[0], dxm["ro_div"] + dvdd[1], sp_bot, "VDD")
    # VSS, metal3 strap ys: control block gnd spine (metal1 up, via1, metal2 riser), macro VSS bus (metal2
    # up), canary and RO bank VSS ports (metal2 down), ro_div gnd spine (metal1 down, via1, metal2)
    rx0, rx1 = dxm["ro_div"] + dgnd[0] + 1.0, dxm["ro_div"] + dgnd[1] - 1.0
    core.box("MET3", xc0 + can_vss[0], ys[0], rx1, ys[1], "VSS")
    core.box("MET1", ocx + gnd_x[0], top_m1, ocx + gnd_x[1], v1y[1], "VSS")
    strap_via("VIA1", gx0, v1y[0], gx1, v1y[1], "VSS")
    core.box("MET2", gx0, v1y[0], gx1, ys[1], "VSS")
    strap_via("VIA2", gx0, ys[0], gx1, ys[1], "VSS")
    core.box("MET2", vx0, mac_top, vx1, ys[1], "VSS")
    strap_via("VIA2", vx0, ys[0], vx1, ys[1], "VSS")
    for (bxx, box_, top_) in ((xc0, can_vss, by_top("canary", "VSS")),
                              (dxm["robank"], rob_vss, by_top("robank", "VSS"))):
        core.box("MET2", bxx + box_[0], ys[0], bxx + box_[2], top_, "VSS")
        strap_via("VIA2", bxx + box_[0], ys[0], bxx + box_[2], ys[1], "VSS")
    yv = (ys[1] + 1.0, ys[1] + 6.0)                            # via1 row under the ro_div gnd spine
    core.box("MET1", dxm["ro_div"] + dgnd[0], yv[0], dxm["ro_div"] + dgnd[1], sp_bot, "VSS")
    strap_via("VIA1", rx0, yv[0], rx1, yv[1], "VSS")
    core.box("MET2", rx0, ys[0], rx1, yv[1], "VSS")
    strap_via("VIA2", rx0, ys[0], rx1, ys[1], "VSS")
    # VDDA, metal3 strap ya .. ya+4: macro VDDA bus (metal2 up) to the canary's VDDA port (metal2 down)
    core.box("MET3", xc0 + can_vdda[0], ya, ax1, ya + 4.0, "VDDA")
    core.box("MET2", ax0, mac_top, ax1, ya + 4.0, "VDDA")
    strap_via("VIA2", ax0, ya, ax1, ya + 4.0, "VDDA")
    core.box("MET2", xc0 + can_vdda[0], ya, xc0 + can_vdda[2], by_top("canary", "VDDA"), "VDDA")
    strap_via("VIA2", xc0 + can_vdda[0], ya, xc0 + can_vdda[2], ya + 4.0, "VDDA")
    mon = {n: [round(MON_X[n], 2), y_blk] for n in MON_X}

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
                   blocks=dict(ctrl=[ocx, ocy], macro=[omx, omy], **{k: [v[0], v[1]] for k, v in dec.items()},
                               **mon),
                   top_channel=dict(tracks=n_tr, y=[CH_Y0, y_last], rows=rows)),
              open(BUILD / "ecc_sram_nets.json", "w"), indent=1)
    bad = net_spacing(core.wires)
    if bad:
        for b in bad[:20]:
            print("spacing:", b)
        raise SystemExit(f"{len(bad)} added shapes of different nets too close (see above)")
    bbt = top.dbbox()
    print(f"wrote {BUILD / 'ecc_sram_Top.gds'} ({bbt.width():.1f} x {bbt.height():.1f} um), core shapes {len(core.wires)},"
          f" pin labels {len(labels)}; control at ({ocx}, {ocy}), macro at ({omx}, {omy}); top channel {n_tr} tracks"
          f" (y {CH_Y0}-{y_last}), monitor blocks at y {y_blk}; past stray block routes: {', '.join(jumped) or '-'}")
    return 0


def bb_top(path):
    lay = kdb.Layout()
    lay.read(str(path))
    return lay.top_cell().dbbox().top


def nets_name(pads, pk):
    """Chip net of an output pad (top channel net name): DED, SEC, DOUT0 .. DOUT3."""
    return pads[pads_key(pads, pk)]["pin"]


def net_spacing(wires):
    """Added rectangles of different nets on the same metal (via pads included) closer than the rule
    document's spacing (metal1 0.8, metal2 and metal3 1.0) or touching: the drawing's own short check."""
    sp = {"MET1": 0.8, "MET2": 1.0, "MET3": 1.0, "VIA1": 0.8, "VIA2": 0.8}
    bad = []
    for layer, s in sp.items():
        rs = sorted(((b, n) for n, ly_, b in wires if ly_ == layer and n), key=lambda t: t[0][0])
        for i, (a, na) in enumerate(rs):
            for b, nb in rs[i + 1:]:
                if b[0] >= a[2] + s:
                    break
                if na == nb:
                    continue
                dx = max(b[0] - a[2], a[0] - b[2], 0.0)
                dy = max(b[1] - a[3], a[1] - b[3], 0.0)
                if (dx * dx + dy * dy) ** 0.5 < s - 1e-6:
                    bad.append((layer, na, a, nb, b))
    return bad


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
