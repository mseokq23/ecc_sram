#!/usr/bin/env python3
"""Top-level assembly of the ECC 8T SRAM chip (KLayout): ETRI GPIO pad ring, control block and decoder block
(qflow macros), SRAM macro (array + column circuits), decoupling for VDDA and VDDW, and the wiring between them.

  python3 designs/etri050/chip/assemble.py        (after run_pad_ring.sh, colper.py, decap.py, freeze_macro.sh
                                                   for ecc_fi_ctrl and ecc_dec)

Writes build/ecc_sram_Top.gds (the chip), build/ecc_sram_core.gds (the same without the pad ring, for LVS)
and build/ecc_sram_nets.json (where each pad port meets the core wiring: the LVS pin labels).

Floorplan (die um, core window 442-1458):
  control block   lower-left (470, 560); inputs from W pads on its left side, from S pads on its bottom
                  left, from N pads on its top left; the read word R and VIEW, V_DIR, HALF for the decoder on
                  its top; word lines on its right; PRE_N, WD and SENSE on its bottom right
  SRAM macro      lower-left (1065, 567.4), word line pins (left) facing the control block
  decoupling      VDDW 57 pF at (1290, 470), VDDA 28.5 pF at (1290, 770), supply buses toward the E pads
  decoder block   over the top channel, left edge x 560, bottom (Y_BLK) set by the channel height; its pins
                  are all on its bottom side: the 11 inputs from the control block, the 6 outputs to the pads
Wiring (three layers, each net on its own track, so no two nets share a layer where they cross):
  word lines      control pin -> metal3 -> metal2 track (x 968 + 3 i) -> metal1 into the macro's word line
                  contact stack
  bottom channel  S pad inputs on metal3 tracks y 450-466 (below), PRE_N/WD/SENSE on tracks y 474-538,
                  metal2 up and down at the pins
  W channel       pad port -> metal2 -> metal1 track (x 446 + 3 i) -> metal2/metal3 into the control pin
  top channel     metal3 tracks from y 1086 (4 um pitch, track order from channel_tracks()): the control
                  block's top pins below, the decoder's pins above; the decoder's N pad outputs go east to
                  metal2 lines at x 1435-1441, up to metal3 y 1440-1448 and west to their pads; its E pad
                  outputs go down or up metal2 lanes at x 1444-1452
  FI_POS          N pad inputs: metal2 straight up from the control pins (west of the decoder block) to
                  metal3 y 1418-1426, east to their pads
  supplies        VSS: metal3 strap y 542-556 from the control block's gnd spine to the macro VSS bus,
                  the decap VSS buses and pads S6, E1; VDD: N4 -> metal3 y 1438-1450 -> control block vdd
                  spine, S7 -> macro VDD bus; VDDW: E2 -> decap -> macro (metal3 y 576-590); VDDA: E3 ->
                  decap -> macro (metal3 between two of the array's VDDA bus vias)
                  decoder block (straps between the top channel and the block): VDD metal1 from the control
                  block's vdd spine to the decoder's vdd spine; VSS metal3 from the control block's gnd spine
                  (metal2 riser through the channel) to the decoder's gnd spine
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
# decoder block: x of its bounding box's left edge; y (bottom) follows the top channel's height. Its left edge
# stays east of the FI_POS lines (x 484-497), its right edge west of the N pad output lines (x 1435), and no pin
# of it within 2 um of the control block's gnd riser (x 945.6-952.6)
DEC_X = 560.0
CH_Y0, CH_PITCH = 1086.0, 4.0                       # top channel: first metal3 track, pitch
WL_X0 = 968.0                                        # word line metal2 tracks x WL_X0 + 3 i (clear of the gnd spine)
N_OUT = {"N5": (1435.0, 1440.0), "N6": (1438.0, 1444.0), "N7": (1441.0, 1448.0)}   # metal2 line x, metal3 y
E_LANE = {"E5": 1452.0, "E6": 1448.0, "E7": 1444.0}
FI_BAND = {"N1": 1418.0, "N2": 1422.0, "N3": 1426.0}                               # metal3 y per N input
LINK = [f"R[{i}]" for i in range(8)] + ["VIEW", "V_DIR", "HALF"]                   # control block -> decoder


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
    for name in ("ecc_fi_ctrl", "ecc_dec"):
        gds[name] = BUILD / f"{name}.gds"
        with gzip.open(D / f"ctrl/macro/{name}.gds.gz") as f, open(gds[name], "wb") as o:
            shutil.copyfileobj(f, o)

    core = Top("ecc_sram_core")
    ocx, ocy, _ = core.place(gds["ecc_fi_ctrl"], CTRL_LL)
    omx, omy, _ = core.place(D / "sram/build/sram_macro.gds", MACRO_LL)
    dec = {n: core.place(D / f"sram/build/{n}.gds", ll) for n, ll in DECAP_LL.items()}
    cp = ctrl_pins()
    cbb = cell_bbox(gds["ecc_fi_ctrl"])              # control block bounding box (block coordinates)
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
    # the pins' column: metal3 of the block east of it belongs to routes that go round a pin; a word line that
    # would cross one leaves its pin on metal2 instead (via2 on the pin)
    col_x2 = max(cp[f"{k}[{i}]"][1][2] for k in ("WWL", "RWL") for i in range(15))
    cb = (cbb.left, cbb.bottom, col_x2 + 0.05, cbb.top)
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
        if hits(stray3, (px1, yl - W3 / 2, WL_X0 - 1.0 - ocx, yl + W3 / 2), (px1, py1, px2, py2), 1.0):
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
    stray2 = stray_metal(gds["ecc_fi_ctrl"], "MET2", (cbb.left, cbb.bottom - 0.05, cbb.right, cbb.top))

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

    # ------------------------------------------------------------------ top channel and decoder block
    ctrl_top = ocy + cp["R[0]"][1][1]                # bottom of the top pins
    vdd_x = spine("ecc_fi_ctrl", "vdd")
    gnd_x = spine("ecc_fi_ctrl", "gnd")
    dbb = cell_bbox(gds["ecc_dec"])
    ddx = round(DEC_X - dbb.left, 2)                 # decoder block origin x (die)
    dp = ctrl_pins("ecc_dec")

    def dx(pin):                                     # die x of a decoder pin's centre
        _, (x1, _, x2, _) = dp[pin]
        return round(ddx + (x1 + x2) / 2, 2)

    def cx(name):
        return round(cpin(name)[1], 2)

    outs = {"N5": "DED_FLAG", "N6": "SEC_FLAG", "N7": "DOUT[3]", "E5": "DOUT[0]", "E6": "DOUT[1]",
            "E7": "DOUT[2]"}
    for pk, cname in outs.items():
        if ctrl_name(pads[pads_key(pads, pk)]["pin"]) != cname:
            raise SystemExit(f"{pk} is not {cname} in pins.csv")
    for p in LINK:
        if p not in cp or p not in dp:
            raise SystemExit(f"{p}: missing on the control block or the decoder block")
    # control block -> decoder: up from the control pin to the track, up again into the decoder pin
    nets = {link_net(p): dict(bot=[cx(p)], top=[dx(p)]) for p in LINK}
    # decoder -> pads: up from the track into the decoder pin; N outputs and E6, E7 go up their lines, E5 down
    for pk, cname in outs.items():
        n = nets_name(pads, pk)
        if pk in N_OUT:
            nets[n] = dict(bot=[], top=[dx(cname), N_OUT[pk][0]])
        elif pk == "E5":                                                 # DOUT0: its lane goes down
            nets[n] = dict(bot=[E_LANE[pk]], top=[dx(cname)])
        else:
            nets[n] = dict(bot=[], top=[dx(cname), E_LANE[pk]])
    fi = {pk: ctrl_name(pads[pads_key(pads, pk)]["pin"]) for pk in FI_BAND}
    # metal2 that crosses the whole channel: FI_POS lines, the vdd and gnd spine risers of the control block
    g_riser = (ocx + gnd_x[0] + 1.0, ocx + gnd_x[1] - 1.0)
    v_riser = (ocx + vdd_x[0] + 1.0, ocx + vdd_x[1] - 1.0)
    through = [(cx(c) - W2 / 2, cx(c) + W2 / 2) for c in fi.values()] + [g_riser, v_riser]
    rows, span = channel_tracks(nets, through)
    n_tr = len(rows)
    y_tr = {n: CH_Y0 + CH_PITCH * (n_tr - 1 - i) for i, row in enumerate(rows) for n in row}
    y_last = CH_Y0 + CH_PITCH * (n_tr - 1)
    if CH_Y0 - 2.0 - 1.0 < ctrl_top + (cbb.top - cp["R[0]"][1][1]):
        raise SystemExit(f"top channel starts at {CH_Y0}, too close to the control block top")
    ys = (y_last + 9.2, y_last + 17.2)               # VSS strap (metal3) and VDD strap (metal1)
    y_blk = round(ys[1] + 7.0, 2)                    # decoder block's bottom edge
    ddx_p, ddy, _ = core.place(gds["ecc_dec"], (DEC_X, y_blk))
    if abs(ddx_p - ddx) > 0.005:
        raise SystemExit(f"ecc_dec: placed at x offset {ddx_p}, expected {ddx}")
    dec_top = ddy + dbb.top
    if dec_top > FI_BAND["N1"] - W3 / 2 - 1.0 and DEC_X + dbb.width() > min(cx(c) for c in fi.values()):
        raise SystemExit(f"ecc_dec top {dec_top:.2f} reaches the FI_POS band")
    if dec_top > min(y for _, y in N_OUT.values()) - W3 / 2 - 1.0:
        raise SystemExit(f"ecc_dec top {dec_top:.2f} reaches the N pad output wiring")
    if DEC_X + dbb.width() > min(x for x, _ in N_OUT.values()) - W2 / 2 - 1.0:
        raise SystemExit("ecc_dec reaches the N pad output lines")

    def dtop(pin):                                   # die y of a decoder pin's top edge
        _, (_, _, _, y2) = dp[pin]
        return round(ddy + y2, 2)

    # the decoder's pins are on its bottom edge, but the router also runs some routes under the pin row (the
    # block's bounding box reaches below the pins): a metal2 line coming up into a pin would cross them
    dstray2 = stray_metal(gds["ecc_dec"], "MET2", (dbb.left, -3.7, dbb.right, dbb.top))
    dpin_of = {(link_net(p), dx(p)): p for p in LINK}
    dpin_of.update({(nets_name(pads, pk), dx(cname)): cname for pk, cname in outs.items()})

    def into_dec_pin(pin, x, y_low, net):
        """Metal2 from y_low up into a decoder pin; where a route of the block runs under the pin row, the
        metal2 stops below it and a via2, metal3 up past the route and a via2 on the pin finish the line."""
        _, (px1, py1, px2, py2) = dp[pin]
        xl = x - ddx
        under = hits(dstray2, (xl - W2 / 2, -12.0, xl + W2 / 2, py2), (px1, py1, px2, py2), 1.0)
        if not under:
            core.vline("MET2", x, y_low, ddy + py2, W2, net)
            return
        yj = ddy + min(b.bottom for b in under) - 2.4      # via2 pad 1.4 um below the route
        yp = ddy + (py1 + py2) / 2
        core.via("VIA2", x, yp, net)
        core.vline("MET3", x, yj, yp, W3, net)
        core.via("VIA2", x, yj, net)
        core.vline("MET2", x, y_low, yj, W2, net)
        jumped.append(net)

    # metal2 line ends: control pins from their bottom edge, decoder pins up to their top edge
    ends = {}
    for p in LINK:
        ends[(link_net(p), dx(p))] = dtop(p)
    for pk, cname in outs.items():
        ends[(nets_name(pads, pk), dx(cname))] = dtop(cname)
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
            if (n, x) in dpin_of:
                into_dec_pin(dpin_of[(n, x)], x, y, n)
            else:
                core.vline("MET2", x, y, ends[(n, x)], W2, n)
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
    m_vss, m_vdda = (omx + 145.8, omx + 149.4), (omx + 151.2, omx + 154.8)   # macro VSS and VDDA buses
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


    # ------------------------------------------------------------------ decoder block supplies
    dvdd, dgnd = spine("ecc_dec", "vdd"), spine("ecc_dec", "gnd")
    # VDD, metal1 strap ys: control block vdd spine (drawn up from its top end) to the decoder's vdd spine
    # (drawn down from its bottom end)
    top_m1 = ocy + spine_top(gds["ecc_fi_ctrl"], vdd_x) - 1.7               # inside the spines' top ends
    if abs(spine_top(gds["ecc_fi_ctrl"], gnd_x) - spine_top(gds["ecc_fi_ctrl"], vdd_x)) > 0.005:
        raise SystemExit("control block: vdd and gnd spines end at different heights")
    if top_m1 + 1.7 > v1y[0]:
        raise SystemExit("control block spines reach the via1 rows above the block")
    core.box("MET1", ocx + vdd_x[0], top_m1, ocx + vdd_x[1], ys[1], "VDD")
    core.box("MET1", ocx + vdd_x[0], ys[0], ddx + dvdd[1], ys[1], "VDD")
    sp_bot = ddy + 0.3 + 2.0                                                 # 2 um into the spines (they start at 0.3)
    core.box("MET1", ddx + dvdd[0], ys[0], ddx + dvdd[1], sp_bot, "VDD")
    # VSS, metal3 strap ys: control block gnd spine (metal1 up, via1, metal2 riser) to the decoder's gnd spine
    # (metal1 down, via1, metal2)
    rx0, rx1 = ddx + dgnd[0] + 1.0, ddx + dgnd[1] - 1.0
    core.box("MET3", gx0, ys[0], rx1, ys[1], "VSS")
    core.box("MET1", ocx + gnd_x[0], top_m1, ocx + gnd_x[1], v1y[1], "VSS")
    strap_via("VIA1", gx0, v1y[0], gx1, v1y[1], "VSS")
    core.box("MET2", gx0, v1y[0], gx1, ys[1], "VSS")
    strap_via("VIA2", gx0, ys[0], gx1, ys[1], "VSS")
    yv = (ys[1] + 1.0, ys[1] + 6.0)                                          # via1 row under the decoder gnd spine
    core.box("MET1", ddx + dgnd[0], yv[0], ddx + dgnd[1], sp_bot, "VSS")
    strap_via("VIA1", rx0, yv[0], rx1, yv[1], "VSS")
    core.box("MET2", rx0, ys[0], rx1, yv[1], "VSS")
    strap_via("VIA2", rx0, ys[0], rx1, ys[1], "VSS")

    # ------------------------------------------------------------------ write
    opt = kdb.SaveLayoutOptions()
    core.ly.write(str(BUILD / "ecc_sram_core.gds"), opt)
    chip = kdb.Layout()
    chip.read(str(BUILD / "ecc_sram_core.gds"))
    chip.read(str(BUILD / "ecc_sram_Pad.gds"))                # merges cells; two top cells now
    top = chip.create_cell("ecc_sram_Top")
    for c in [c for c in chip.top_cells() if c.name != "ecc_sram_Top"]:
        top.insert(kdb.CellInstArray(c.cell_index(), kdb.Trans()))
    chip.write(str(BUILD / "ecc_sram_Top.gds"), opt)
    json.dump(dict(unit="um", labels=[dict(name=n, x=round(x, 2), y=round(y, 2)) for n, x, y in labels],
                   blocks=dict(ctrl=[ocx, ocy], macro=[omx, omy], **{k: [v[0], v[1]] for k, v in dec.items()},
                               ecc_dec=[ddx, ddy]),
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
          f" (y {CH_Y0}-{y_last}), decoder block at ({DEC_X}, {y_blk}) to y {dec_top:.2f};"
          f" past stray block routes: {', '.join(jumped) or '-'}")
    return 0


def cell_bbox(path):
    """Bounding box of a GDS file's top cell (um)."""
    lay = kdb.Layout()
    lay.read(str(path))
    return lay.top_cell().dbbox()


def spine_top(path, xr):
    """Top end (um, block coordinates) of a qflow block's power comb whose spine is the metal1 at x range xr."""
    lay = kdb.Layout()
    lay.read(str(path))
    c = lay.top_cell()
    reg = kdb.Region(c.begin_shapes_rec(lay.layer(*LY["MET1"]))).merged()
    probe = kdb.Region(kdb.DBox(xr[0] + 0.1, 0.3, xr[1] - 0.1, 1.3).to_itype(lay.dbu))
    hit = reg.interacting(probe)
    if hit.is_empty():
        raise SystemExit(f"{path.name}: no spine metal1 at x {xr}")
    return round(max(p.bbox().to_dtype(lay.dbu).top for p in hit.each()), 3)


def link_net(pin):
    """Chip net of a control-to-decoder pin: R[3] -> R3."""
    return pin.replace("[", "").replace("]", "")


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
