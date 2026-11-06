#!/usr/bin/env python3
"""Explanatory figures for docs/operation.md, drawn with matplotlib: the chip's block diagram, the data path of
the control block, the 8T cell with its column circuits, one column writing and reading (ngspice, official PDK
models), the canary latch, the canaries' retention voltages per corner and the ring-oscillator bank with its
divider.

  python3 scripts/doc_diagrams.py                 # all -> docs/img/op_*.png
  python3 scripts/doc_diagrams.py wave canary     # only these (block ctrl column wave canary ladder ro)

The waveform needs ngspice and the PDK models (bash scripts/get-models.sh); it reuses the cell and column
netlists of designs/etri050/sim/cell/cell8t.py. Korean labels need a CJK font (Noto Sans CJK or Nanum).
Sizes and values written in the figures come from the generators (designs/etri050/gen), the RTL
(designs/etri050/ctrl) and docs/verification.md.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib
import matplotlib.font_manager

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs/img"
_HAVE = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
plt.rcParams.update({"font.family": [f for f in ("Noto Sans CJK KR", "Noto Sans CJK JP", "NanumGothic") if f in _HAVE]
                     + ["DejaVu Sans"], "font.size": 10, "axes.unicode_minus": False})

INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
DOM = {"VDD": ("#e6f0fc", "#2a78d6"), "VDDA": ("#dff4eb", "#1baf7a"), "VDDW": ("#fde9df", "#eb6834")}
PANEL = "#f6f6f4"


# ------------------------------------------------------------------ drawing helpers (data units)
def canvas(w, h, scale=0.58):
    fig = plt.figure(figsize=(w * scale, h * scale))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, name, dpi=170):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=dpi, facecolor="white")
    plt.close(fig)
    print(f"docs/img/{name}")


def box(ax, x, y, w, h, text="", dom=None, fc="white", ec=INK2, lw=1.0, fs=9.5, weight="normal", r=0.08,
        tx=None, ty=None, ha="center", va="center", color=INK, z=2, ls="-"):
    if dom:
        fc, ec = DOM[dom]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw,
                                zorder=z, ls=ls))
    if text:
        ax.text(x + w / 2 if tx is None else tx, y + h / 2 if ty is None else ty, text, ha=ha, va=va,
                fontsize=fs, fontweight=weight, color=color, zorder=z + 1, linespacing=1.35)


def text(ax, x, y, s, fs=8.5, color=INK2, ha="left", va="center", weight="normal", bg=False, z=6, **kw):
    bbox = dict(fc="white", ec="none", pad=0.6) if bg else None
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va, fontweight=weight, zorder=z, bbox=bbox,
            linespacing=1.3, **kw)


def wire(ax, pts, color=INK2, lw=1.1, arrow=True, ms=9, z=3, ls="-"):
    """Polyline through pts, arrow head at the last point."""
    xs, ys = zip(*pts)
    if arrow:
        if len(pts) > 2:
            ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, zorder=z, ls=ls, solid_capstyle="butt")
        ax.annotate("", xy=pts[-1], xytext=pts[-2], zorder=z,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms,
                                    linestyle=ls))
    else:
        ax.plot(xs, ys, color=color, lw=lw, zorder=z, ls=ls, solid_capstyle="butt")


def dot(ax, x, y, color=INK2, r=0.045):
    ax.add_patch(Circle((x, y), r, fc=color, ec=color, zorder=5))


def vline(ax, x, y1, y2, hops=(), r=0.14, color=INK, lw=1.2):
    """Vertical line from y1 down to y2 (y1 > y2) with a half-circle hop to the right at each y in hops."""
    pts, y = [(x, y1)], y1
    for h in sorted(hops, reverse=True):
        pts.append((x, h + r))
        pts += [(x + r * math.sin(a), h + r * math.cos(a)) for a in (i * math.pi / 12 for i in range(13))]
    pts.append((x, y2))
    ax.plot(*zip(*pts), color=color, lw=lw, zorder=3)


def hline(ax, x1, x2, y, hops=(), r=0.14, color=INK, lw=1.2):
    """Horizontal line from x1 to x2 (x1 < x2) with a half-circle hop upwards at each x in hops."""
    pts = [(x1, y)]
    for h in sorted(hops):
        pts.append((h - r, y))
        pts += [(h - r * math.cos(a), y + r * math.sin(a)) for a in (i * math.pi / 12 for i in range(13))]
    pts.append((x2, y))
    ax.plot(*zip(*pts), color=color, lw=lw, zorder=3)


def bezier(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


# logic gates: (x, y) = middle of the back edge, s = scale; return the pin coordinates
def _bubble(ax, x, y, s, color):
    ax.add_patch(Circle((x + 0.07 * s, y), 0.07 * s, fc="white", ec=color, lw=1.1, zorder=4))
    return (x + 0.14 * s, y)


def gate_inv(ax, x, y, s=0.6, color=INK, label=None, fs=7.5, left=False):
    """Inverter with its input at (x, y), pointing right (left=True: pointing left)."""
    d = -1 if left else 1
    ax.add_patch(Polygon([(x, y - 0.38 * s), (x, y + 0.38 * s), (x + d * 0.75 * s, y)], closed=True, fc="white",
                         ec=color, lw=1.1, zorder=4))
    bx = x + d * 0.82 * s
    ax.add_patch(Circle((bx, y), 0.07 * s, fc="white", ec=color, lw=1.1, zorder=4))
    out = (x + d * 0.89 * s, y)
    if label:
        text(ax, x + d * 0.35 * s, y - 0.5 * s, label, fs=fs, ha="center", va="top", color=INK2)
    return dict(i=(x, y), o=out)


def gate_and(ax, x, y, s=0.6, n=2, bubble=False, color=INK, label=None, fs=7.5):
    h = 0.4 * s
    pts = [(x, y - h), (x + 0.45 * s, y - h)]
    pts += [(x + 0.45 * s + h * math.sin(a), y - h * math.cos(a)) for a in (i * math.pi / 24 for i in range(25))]
    pts += [(x, y + h)]
    ax.add_patch(Polygon(pts, closed=True, fc="white", ec=color, lw=1.1, zorder=4))
    tip = (x + 0.45 * s + h, y)
    out = _bubble(ax, *tip, s, color) if bubble else tip
    ys = [y + h * (1 - 2 * (k + 0.5) / n) * 0.9 for k in range(n)]
    if label:
        text(ax, x + 0.4 * s, y - h - 0.12 * s, label, fs=fs, ha="center", va="top", color=INK2)
    return dict(i=[(x, yy) for yy in ys], o=out)


def gate_or(ax, x, y, s=0.6, n=2, bubble=False, color=INK, label=None, fs=7.5):
    h = 0.4 * s
    back = bezier((x, y - h), (x + 0.28 * s, y), (x, y + h))
    top = bezier((x, y + h), (x + 0.62 * s, y + h), (x + 0.95 * s, y))
    bot = bezier((x + 0.95 * s, y), (x + 0.62 * s, y - h), (x, y - h))
    ax.add_patch(Polygon(back + top[1:] + bot[1:], closed=True, fc="white", ec=color, lw=1.1, zorder=4))
    tip = (x + 0.95 * s, y)
    out = _bubble(ax, *tip, s, color) if bubble else tip
    ins = []
    for k in range(n):
        yy = y + h * (1 - 2 * (k + 0.5) / n) * 0.9
        t = (yy - (y - h)) / (2 * h)
        xb = x + 2 * (1 - t) * t * 0.28 * s
        ax.plot([x - 0.02 * s, xb], [yy, yy], color=color, lw=1.1, zorder=4)
        ins.append((x - 0.02 * s, yy))
    if label:
        text(ax, x + 0.45 * s, y - h - 0.12 * s, label, fs=fs, ha="center", va="top", color=INK2)
    return dict(i=ins, o=out)


def mos(ax, x, y, kind="n", s=1.0, rot=0, mirror=False, color=INK, label=None, lpos=(0.45, 0.0), fs=7.5,
        lha="left"):
    """MOSFET symbol, channel vertical at (x, y) before rotation: gate on the left (right if mirror), drain up,
    source down. kind 'p' adds the gate bubble. Returns the gate, drain and source pins."""
    sx = -1 if mirror else 1
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def T(px, py):
        px *= sx * s
        py *= s
        return (x + c * px - si * py, y + si * px + c * py)

    def seg(*pts):
        ax.plot(*zip(*[T(*p) for p in pts]), color=color, lw=1.2, zorder=4, solid_capstyle="round")

    seg((0, -0.32), (0, 0.32))
    seg((-0.13, -0.24), (-0.13, 0.24))
    if kind == "p":
        ax.add_patch(Circle(T(-0.2, 0), 0.07 * s, fc="white", ec=color, lw=1.1, zorder=4))
        seg((-0.27, 0), (-0.55, 0))
    else:
        seg((-0.13, 0), (-0.55, 0))
    seg((0, 0.24), (0.3, 0.24), (0.3, 0.6))
    seg((0, -0.24), (0.3, -0.24), (0.3, -0.6))
    if label:
        lx, ly = T(*lpos) if not mirror else T(lpos[0], lpos[1])
        text(ax, lx, ly, label, fs=fs, ha=lha if not mirror else ("right" if lha == "left" else "left"),
             va="center", color=INK2)
    return dict(g=T(-0.55, 0), d=T(0.3, 0.6), s=T(0.3, -0.6))


def rail(ax, x1, x2, y, name, color=INK2, fs=8, side="left"):
    ax.plot([x1, x2], [y, y], color=color, lw=1.6, zorder=3)
    if name:
        if side == "left":
            text(ax, x1 - 0.1, y, name, fs=fs, ha="right", color=color, weight="bold")
        else:
            text(ax, x2 + 0.1, y, name, fs=fs, ha="left", color=color, weight="bold")


def gnd(ax, x, y, s=0.18, color=INK2):
    ax.plot([x, x], [y, y - s * 0.6], color=color, lw=1.1, zorder=4)
    for k, w in enumerate((1.0, 0.6, 0.25)):
        ax.plot([x - w * s, x + w * s], [y - s * 0.6 - k * s * 0.35] * 2, color=color, lw=1.1, zorder=4)


def xor(ax, x, y, r=0.24, color=INK):
    ax.add_patch(Circle((x, y), r, fc="white", ec=color, lw=1.1, zorder=4))
    ax.plot([x - r, x + r], [y, y], color=color, lw=1.0, zorder=5)
    ax.plot([x, x], [y - r, y + r], color=color, lw=1.0, zorder=5)


def tag(ax, x, y, w, h, s, fs=8.4):
    box(ax, x, y, w, h, s, fc=PANEL, ec=BASE, fs=fs, r=0.06)


# ------------------------------------------------------------------ 1. block diagram
def fig_block():
    W, H = 19.4, 11.4
    fig, ax = canvas(W, H)
    MX, DX, PX = 10.7, 14.6, 17.4            # macro, decoupling and supply pins (left edges)
    # pins
    box(ax, 0.2, 0.6, 2.0, 4.6, "", fc=PANEL, ec=BASE)
    text(ax, 1.2, 4.85, "입력 핀 15 (PIC)", fs=9, ha="center", color=INK, weight="bold")
    for i, s in enumerate(["CLK", "WE", "ADDR[3:0]", "DIN[3:0]", "FI_MODE[1:0]", "FI_POS[2:0]"]):
        text(ax, 0.45, 4.3 - i * 0.6, s, fs=8.6, color=INK)
    box(ax, 0.2, 5.75, 2.0, 1.75, "", fc=PANEL, ec=BASE)
    text(ax, 1.2, 7.2, "출력 핀 6 (POB8)", fs=9, ha="center", color=INK, weight="bold")
    text(ax, 0.45, 6.65, "DOUT[3:0]", fs=8.6, color=INK)
    text(ax, 0.45, 6.12, "SEC · DED", fs=8.6, color=INK)

    # control block
    box(ax, 2.9, 0.35, 6.25, 7.7, "", dom="VDD", lw=1.4, r=0.12)
    text(ax, 4.15, 7.78, "제어 블록 ecc_fi_ctrl", fs=9.5, color=INK, weight="bold")
    text(ax, 4.15, 7.43, "합성 364셀 · VDD", fs=7.8, color=INK2)
    box(ax, 3.2, 5.75, 5.65, 1.45, "보기 해독 · 출력 선택\nDOUT = 정정 데이터 | 원시 | 카나리 | RO_DIV\n"
        "CSET · CRD_N · RO_EN 만듦", fs=8.6)
    box(ax, 3.2, 2.45, 2.6, 2.6, "읽기 결함 마스크\n\n신드롬 · 전체 패리티\n\n정정 · SEC/DED", fs=8.6)
    box(ax, 3.2, 0.6, 2.6, 1.3, "기준 워드 (주소 15)\n플립플롭 8개", fs=8.6)
    box(ax, 6.25, 4.2, 2.6, 1.2, "행 해독\nWWL = 해독 · CLK · WE\nRWL = 해독 · CLK · ~WE", fs=7.9)
    box(ax, 6.25, 0.6, 2.6, 1.3, "부호기\n쓰기 결함 마스크", fs=8.6)

    # SRAM macro
    text(ax, MX, 7.95, "SRAM 매크로 sram_macro", fs=9.5, color=INK, weight="bold")
    box(ax, MX, 4.05, 3.1, 3.55, "8T 셀 어레이\n15행 × 8열\n\nVDDA", dom="VDDA", fs=9)
    box(ax, MX, 2.3, 3.1, 1.5, "읽기 회로 8열\n프리차지 · keeper · 센스\nVDD", dom="VDD", fs=8.6)
    box(ax, MX, 0.6, 3.1, 1.45, "쓰기 드라이버 8열\nBL = WD,  BLB = not WD\nVDDW", dom="VDDW", fs=8.6)

    # monitor
    text(ax, 3.0, 11.05, "신뢰성 모니터 (2026-11-06)", fs=9.5, color=INK, weight="bold")
    box(ax, 3.0, 9.55, 2.9, 1.15, "카나리 래치 8개\nVDDA", dom="VDDA", fs=8.6)
    box(ax, 3.0, 9.05, 2.9, 0.5, "읽기 게이트 · VDD", dom="VDD", fs=8.2)
    box(ax, 6.7, 9.05, 3.6, 1.65, "RO 뱅크\nINV · NAND · NOR 31단 링\nVDD", dom="VDD", fs=8.6)
    box(ax, 11.6, 9.05, 2.2, 1.65, "분주기\n÷256\nVDD", dom="VDD", fs=8.6)

    # decoupling and supply pins
    box(ax, DX, 5.15, 2.1, 1.25, "디커플링\n28.5 pF", dom="VDDA", fs=8.6)
    box(ax, DX, 0.7, 2.1, 1.25, "디커플링\n57 pF", dom="VDDW", fs=8.6)
    box(ax, PX, 5.2, 1.8, 1.15, "VDDA 핀 17\nPANA", fc=PANEL, ec=BASE, fs=8.4)
    box(ax, PX, 0.75, 1.8, 1.15, "VDDW 핀 16\nPANA", fc=PANEL, ec=BASE, fs=8.4)
    for y, d in ((5.78, "VDDA"), (1.33, "VDDW")):
        wire(ax, [(PX, y), (DX + 2.1, y)], color=DOM[d][1], lw=1.6)
        wire(ax, [(DX, y), (MX + 3.1, y)], color=DOM[d][1], lw=1.6)
        text(ax, (DX + MX + 3.1) / 2, y + 0.12, d, fs=7.8, ha="center", va="bottom")
        text(ax, (PX + DX + 2.1) / 2, y + 0.12, "PADR", fs=7.2, ha="center", va="bottom", color=MUTED)

    # legend (supply domains)
    lx, ly = DX, 4.45
    text(ax, lx, ly, "전원", fs=8.6, color=INK, weight="bold")
    for i, (d, s) in enumerate([("VDD", "VDD 5 V 고정: 논리, 읽기 회로, 모니터"), ("VDDA", "VDDA: 셀, 카나리 래치"),
                                ("VDDW", "VDDW: 쓰기 드라이버")]):
        box(ax, lx, ly - 0.55 - i * 0.48, 0.38, 0.3, dom=d, r=0.04)
        text(ax, lx + 0.5, ly - 0.4 - i * 0.48, s, fs=7.8)
    text(ax, lx, ly - 2.0, "VDD 핀 14 · 25,  VSS 핀 13 · 15 · 18\nPADR: PANA 패드의 직렬 저항 약 0.7 kΩ", fs=7.6,
         color=MUTED, va="top")

    # pins <-> control block
    wire(ax, [(2.2, 2.9), (2.9, 2.9)], lw=1.6)
    text(ax, 2.55, 3.05, "15", fs=7.5, ha="center", va="bottom", color=MUTED)
    wire(ax, [(3.2, 6.4), (2.2, 6.4)], lw=1.6)
    text(ax, 2.7, 6.55, "6", fs=7.5, ha="center", va="bottom", color=MUTED)

    # control block <-> macro
    gx = (9.15 + MX) / 2
    wire(ax, [(8.85, 5.0), (MX, 5.0)], lw=1.6)
    text(ax, gx, 5.12, "WWL[14:0]\nRWL[14:0]", fs=7.6, ha="center", va="bottom")
    wire(ax, [(8.85, 4.5), (gx, 4.5), (gx, 3.35), (MX, 3.35)])
    text(ax, gx + 0.08, 3.92, "PRE_N", fs=7.6, ha="left", va="center", bg=True)
    wire(ax, [(MX, 2.7), (5.8, 2.7)], lw=1.6)
    text(ax, 7.6, 2.82, "SENSE[7:0]", fs=7.6, ha="center", va="bottom")
    wire(ax, [(8.85, 1.25), (MX, 1.25)], lw=1.6)
    text(ax, gx, 1.37, "WD[7:0]", fs=7.6, ha="center", va="bottom")
    wire(ax, [(6.25, 1.25), (5.8, 1.25)])
    wire(ax, [(4.5, 1.9), (4.5, 2.45)])
    text(ax, 4.6, 2.17, "주소 15", fs=7.4, ha="left")
    wire(ax, [(4.5, 5.05), (4.5, 5.75)], lw=1.6)
    text(ax, 4.6, 5.4, "정정 데이터\nr · SEC/DED", fs=7.2, ha="left")

    # control block <-> monitor
    wire(ax, [(3.4, 9.05), (3.4, 7.2)])
    text(ax, 3.3, 8.55, "CAN[7:0]", fs=7.6, ha="right")
    wire(ax, [(4.0, 7.2), (4.0, 9.05)])
    text(ax, 4.1, 8.55, "CSET · CRD_N", fs=7.6, ha="left")
    wire(ax, [(7.95, 7.2), (7.95, 9.05)])
    text(ax, 7.85, 8.55, "RO_EN[2:0]", fs=7.6, ha="right")
    wire(ax, [(8.45, 7.2), (8.45, 8.65), (12.1, 8.65), (12.1, 9.05)])
    text(ax, 10.3, 8.72, "RO_EN (0이면 리셋)", fs=7.4, ha="center", va="bottom")
    wire(ax, [(13.2, 9.05), (13.2, 8.3), (8.7, 8.3), (8.7, 7.2)])
    text(ax, 13.3, 8.65, "RO_DIV", fs=7.6, ha="left")
    wire(ax, [(10.3, 9.85), (11.6, 9.85)], lw=1.6)
    text(ax, 10.95, 9.97, "TAP[2:0]", fs=7.4, ha="center", va="bottom")
    save(fig, "op_block.png")


# ------------------------------------------------------------------ 2. control block data path
def fig_ctrl():
    W, H = 18.0, 11.0
    fig, ax = canvas(W, H)
    # pins (left), macro (right), monitor (bottom)
    tag(ax, 0.2, 9.6, 1.7, 0.8, "ADDR[3:0]\nCLK · WE")
    tag(ax, 0.2, 7.85, 1.7, 0.7, "DIN[3:0]")
    tag(ax, 0.2, 5.8, 1.7, 0.8, "FI_MODE[1:0]\nFI_POS[2:0]")
    tag(ax, 0.2, 4.25, 1.7, 0.7, "SEC · DED")
    tag(ax, 0.2, 2.55, 1.7, 0.7, "DOUT[3:0]")
    tag(ax, 16.1, 9.6, 1.7, 0.8, "WWL · RWL\nPRE_N")
    tag(ax, 16.1, 7.85, 1.7, 0.7, "WD[7:0]")
    tag(ax, 16.1, 2.2, 1.7, 0.7, "SENSE[7:0]")
    tag(ax, 7.6, 0.25, 2.8, 0.8, "CSET · CRD_N · RO_EN[2:0]\n→ 모니터")
    tag(ax, 10.9, 0.25, 2.3, 0.8, "CAN[7:0] · RO_DIV\n← 모니터")
    text(ax, 0.2, 10.75, "입력 핀 · 출력 핀", fs=8, color=MUTED)
    text(ax, 17.8, 10.75, "SRAM 매크로", fs=8, color=MUTED, ha="right")

    # lane A: row decoding
    box(ax, 2.6, 9.4, 7.6, 1.2, "행 해독:  dec = 1 << ADDR   (ADDR = 15는 워드라인 없음 → 기준 워드)\n"
        "WWL[i] = dec[i] · CLK · WE     RWL[i] = dec[i] · CLK · ~WE     PRE_N = CLK", fs=8.6)
    wire(ax, [(1.9, 10.0), (2.6, 10.0)])
    wire(ax, [(10.2, 10.0), (16.1, 10.0)], lw=1.6)
    text(ax, 13.1, 10.12, "CLK = 1인 동안 선택된 행 하나 (쓰기 WWL, 읽기 RWL)", fs=7.8, ha="center", va="bottom")

    # lane B: encoder and write mask
    box(ax, 2.6, 7.6, 4.4, 1.2, "부호기\nP0 = D0^D1^D3   P1 = D0^D2^D3\nP2 = D1^D2^D3   PALL = D0^D1^D2", fs=8.4)
    wire(ax, [(1.9, 8.2), (2.6, 8.2)])
    wire(ax, [(7.0, 8.2), (7.56, 8.2)])
    text(ax, 7.28, 8.32, "enc", fs=7.6, ha="center", va="bottom")
    xor(ax, 7.8, 8.2)
    wire(ax, [(8.04, 8.2), (16.1, 8.2)], lw=1.6)
    text(ax, 9.4, 8.32, "WD = enc ⊕ wmask", fs=7.8, ha="left", va="bottom")
    text(ax, 13.6, 8.32, "C = {D3, D2, D1, P2, D0, P1, P0, PALL}", fs=7.6, ha="center", va="bottom", color=MUTED)

    # lane C: fault masks and reference word
    box(ax, 2.6, 5.3, 4.4, 1.8, "결함 마스크 (k = FI_POS)\nh1 = {k},  h2 = {k, k^1},  h3 = {k, k^1, k^2}\n"
        "쓰기 wmask: 01 h1 · 10 h2 · 11 h3\n읽기 rmask: 01 h1 · 10 h2 · 11 없음", fs=8.2)
    wire(ax, [(1.9, 6.2), (2.6, 6.2)])
    wire(ax, [(7.0, 6.9), (7.8, 6.9), (7.8, 7.96)])
    text(ax, 7.9, 7.3, "wmask", fs=7.6)
    box(ax, 9.3, 5.9, 3.8, 1.2, "기준 워드 refw[7:0]\nCLK↑에서 WE = 1, ADDR = 15면 WD 저장", fs=8.0)
    dot(ax, 11.2, 8.2)
    wire(ax, [(11.2, 8.2), (11.2, 7.1)])
    wire(ax, [(7.0, 5.45), (13.9, 5.45), (13.9, 2.79)])
    text(ax, 8.4, 5.57, "rmask", fs=7.6, va="bottom")
    wire(ax, [(13.1, 6.5), (15.2, 6.5), (15.2, 3.2)])
    text(ax, 13.25, 6.62, "refw", fs=7.6, va="bottom")

    # lane D: read path
    box(ax, 14.45, 1.9, 1.5, 1.3, "stored =\nADDR = 15 ?\nrefw : SENSE", fs=7.4)
    wire(ax, [(16.1, 2.55), (15.95, 2.55)], lw=1.6)
    wire(ax, [(14.45, 2.55), (14.14, 2.55)])
    xor(ax, 13.9, 2.55)
    wire(ax, [(13.66, 2.55), (3.3, 2.55)], lw=1.6)
    text(ax, 12.6, 2.4, "r = stored ⊕ rmask", fs=7.8, ha="center", va="top")
    box(ax, 10.2, 3.0, 2.8, 1.1, "신드롬 s = 1인 비트 위치의 XOR\n전체 패리티 q = r 8비트 XOR", fs=8.0)
    dot(ax, 11.6, 2.55)
    wire(ax, [(11.6, 2.55), (11.6, 3.0)])
    box(ax, 5.4, 3.0, 4.0, 1.1, "정정: 데이터 비트 {R7, R6, R5, R3}\nq = 1이고 s가 그 위치면 그 비트를 뒤집음", fs=8.0)
    dot(ax, 7.4, 2.55)
    wire(ax, [(7.4, 2.55), (7.4, 3.0)])
    wire(ax, [(10.2, 3.55), (9.4, 3.55)])
    text(ax, 9.8, 3.67, "s, q", fs=7.4, ha="center", va="bottom")
    wire(ax, [(11.6, 4.1), (11.6, 4.6), (1.9, 4.6)])
    text(ax, 6.2, 4.72, "SEC = q,   DED = (s ≠ 0) · ~q", fs=7.8, ha="center", va="bottom")
    # DOUT multiplexer
    ax.add_patch(Polygon([(3.3, 1.5), (3.3, 4.3), (2.6, 3.9), (2.6, 1.9)], closed=True, fc="white", ec=INK, lw=1.1,
                         zorder=4))
    text(ax, 2.92, 2.9, "DOUT 선택", fs=7.8, ha="center", va="center", color=INK, rotation=90)
    wire(ax, [(5.4, 3.75), (3.3, 3.75)])
    text(ax, 3.45, 3.87, "정정 데이터", fs=7.4, va="bottom")
    text(ax, 3.45, 2.67, "원시: r 반쪽 (FI_POS0)", fs=7.4, va="bottom")
    wire(ax, [(11.8, 1.05), (11.8, 2.15), (3.3, 2.15)])
    text(ax, 3.45, 2.2, "카나리: CAN 반쪽 (FI_POS0)", fs=7.4, va="bottom")
    wire(ax, [(11.2, 1.05), (11.2, 1.75), (3.3, 1.75)])
    text(ax, 3.45, 1.62, "RO: {0, 0, 0, RO_DIV}", fs=7.4, va="top")
    wire(ax, [(2.6, 2.9), (1.9, 2.9)], lw=1.6)

    # lane E: view decoding
    box(ax, 2.2, 0.2, 4.95, 1.15, "보기 해독: 읽기(WE = 0)이고 FI_MODE = 11일 때 FI_POS[2:1]\n"
        "00 원시 · 01 카나리 · 10 카나리 세트(CSET = CLK) · 11 RO\nRO_EN: DIN[1:0] = 00 INV · 01 NAND · 10 NOR", fs=7.6)
    wire(ax, [(2.95, 1.35), (2.95, 1.7)])
    wire(ax, [(7.15, 0.65), (7.6, 0.65)])
    save(fig, "op_ctrl.png")


# ------------------------------------------------------------------ 3. 8T cell and column circuits
def fig_column():
    W, H = 18.0, 12.1
    fig, ax = canvas(W, H)
    BL, BLB, RBL = 2.8, 11.0, 14.6
    # supply regions
    box(ax, 1.9, 7.6, 14.1, 4.2, "", dom="VDDA", r=0.1, lw=1.0)
    text(ax, 2.1, 11.5, "8T 셀 (한 열의 한 행)  ·  저장부 VDDA", fs=9, color=INK, weight="bold")
    box(ax, 1.6, 0.3, 10.1, 3.75, "", dom="VDDW", r=0.1, lw=1.0)
    text(ax, 3.1, 3.75, "쓰기 드라이버  ·  VDDW  (늘 켜져 있고, 쓰기는 WWL만 정한다)", fs=9, color=INK, weight="bold")
    box(ax, 12.2, 0.3, 5.6, 6.9, "", dom="VDD", r=0.1, lw=1.0)
    text(ax, 12.4, 6.9, "읽기 회로  ·  VDD", fs=9, color=INK, weight="bold")

    # bit lines
    ax.plot([BL, BL], [2.85, 10.6], color=INK, lw=1.6, zorder=3)
    vline(ax, BLB, 10.6, 1.45, lw=1.6)
    text(ax, BL, 10.75, "BL", fs=9, ha="center", va="bottom", color=INK, weight="bold")
    text(ax, BLB, 10.75, "BLB", fs=9, ha="center", va="bottom", color=INK, weight="bold")

    # storage: two cross-coupled inverters, Q on the left, QB on the right
    QX, QBX = 5.2, 8.8
    top = gate_inv(ax, 7.6, 10.3, s=0.9, left=True)
    bot = gate_inv(ax, 6.4, 9.05, s=0.9)
    wire(ax, [top["o"], (QX, 10.3), (QX, 9.05), bot["i"]], arrow=False, color=INK, lw=1.2)
    wire(ax, [bot["o"], (QBX, 9.05), (QBX, 10.3), top["i"]], arrow=False, color=INK, lw=1.2)
    text(ax, QX + 0.1, 9.72, "Q", fs=9, color=INK, weight="bold")
    text(ax, QBX - 0.1, 9.72, "QB", fs=9, color=INK, weight="bold", ha="right")
    text(ax, 7.0, 9.68, "PU 1.8/0.6\nPD 3.0/0.6", fs=7.4, ha="center", color=INK2)
    # pass gates (WWL)
    pgl = mos(ax, 3.9, 9.75, rot=-90)
    pgr = mos(ax, 10.1, 9.75, rot=-90)
    for pin, x in ((pgl["s"], BL), (pgl["d"], QX), (pgr["s"], QBX), (pgr["d"], BLB)):
        ax.plot([pin[0], x], [pin[1], pin[1]], color=INK, lw=1.2, zorder=3)
        dot(ax, x, pin[1], color=INK)
    ax.plot([pgl["g"][0], pgl["g"][0], pgr["g"][0], pgr["g"][0]], [pgl["g"][1], 11.05, 11.05, pgr["g"][1]],
            color=INK, lw=1.2, zorder=3)
    text(ax, 7.0, 11.15, "WWL (쓰기 워드라인)", fs=8.2, ha="center", va="bottom", color=INK)
    text(ax, 3.9, 9.02, "PG\n1.8/0.6", fs=7.4, ha="center", va="top")
    text(ax, 10.1, 9.02, "PG\n1.8/0.6", fs=7.4, ha="center", va="top")
    # read port: RD2 (RWL) over RD1 (QB), RBL to the read circuits
    rd2 = mos(ax, 13.3, 9.6)
    rd1 = mos(ax, 13.3, 8.4)
    gnd(ax, *rd1["s"], color=INK)
    ax.plot([12.1, rd2["g"][0]], [9.6, 9.6], color=INK, lw=1.2, zorder=3)
    text(ax, 12.05, 9.6, "RWL", fs=8.2, ha="right", color=INK)
    ax.plot([QBX, QBX], [9.05, 8.4], color=INK, lw=1.2, zorder=3)
    dot(ax, QBX, 9.05, color=INK)
    hline(ax, QBX, rd1["g"][0], 8.4, hops=(BLB,))
    ax.plot([rd2["d"][0], rd2["d"][0], RBL], [rd2["d"][1], 10.55, 10.55], color=INK, lw=1.2, zorder=3)
    text(ax, RBL + 0.1, 10.7, "RBL", fs=9, color=INK, weight="bold")
    text(ax, 13.75, 9.6, "RD2", fs=7.4)
    text(ax, 13.75, 8.4, "RD1", fs=7.4)
    text(ax, 14.75, 9.0, "읽기 포트\nRD1 · RD2\n3.0/0.6", fs=7.4, va="center")

    # operation notes
    box(ax, 3.3, 4.55, 7.4, 2.6, "", fc="white", ec=BASE, r=0.08)
    text(ax, 3.5, 5.85, "쓰기: CLK = 1, WE = 1 → WWL = 1. PG가 켜지고 BL · BLB(= WD, not WD) 중\n"
         "         0인 비트라인이 1인 저장 노드를 끌어내려 셀이 뒤집힌다\n"
         "읽기: CLK = 0 동안 PRE_N = 0 → RBL = VDD.\n"
         "         CLK = 1, WE = 0 → RWL = 1. Q = 0이면 QB = 1이라 RD1 · RD2가\n"
         "         RBL을 내리고 SB = 1, SENSE = 0. Q = 1이면 keeper가 RBL을 붙잡는다\n"
         "읽기 전류가 Q · QB를 지나지 않아 읽어도 셀 값이 바뀌지 않는다", fs=8.6, color=INK, va="center")

    # write drivers: BLB = not WD, BL = not BLB
    tag(ax, 5.0, 1.1, 1.9, 0.7, "WD (제어 블록)", fs=8)
    inv1 = gate_inv(ax, 8.4, 1.45, s=0.9)
    ax.plot([6.9, inv1["i"][0]], [1.45, 1.45], color=INK, lw=1.2, zorder=3)
    ax.plot([inv1["o"][0], BLB], [1.45, 1.45], color=INK, lw=1.2, zorder=3)
    inv2 = gate_inv(ax, 9.4, 2.85, s=0.9, left=True)
    ax.plot([BLB, inv2["i"][0]], [2.85, 2.85], color=INK, lw=1.2, zorder=3)
    dot(ax, BLB, 2.85, color=INK)
    ax.plot([inv2["o"][0], BL], [2.85, 2.85], color=INK, lw=1.2, zorder=3)
    text(ax, 8.75, 0.82, "BLB = not WD", fs=7.8, ha="center", va="top")
    text(ax, 9.05, 3.25, "BL = not BLB = WD", fs=7.8, ha="center", va="bottom")
    text(ax, 3.1, 2.1, "인버터마다 P 12.0/0.6, N 6.0/0.6\n(손가락 2개)", fs=7.4, va="center")

    # read circuits: precharge, keeper, sense and output inverters
    ax.plot([13.4, 16.6], [6.3, 6.3], color=INK, lw=1.6, zorder=3)
    text(ax, 16.7, 6.3, "VDD", fs=8, color=INK, weight="bold")
    vline(ax, RBL, 10.55, 3.6, hops=(6.3,))
    pre = mos(ax, 13.7, 5.7, kind="p")
    kp = mos(ax, 15.45, 5.7, kind="p", mirror=True)
    for t in (pre, kp):
        ax.plot([t["d"][0], t["d"][0]], [t["d"][1], 6.3], color=INK, lw=1.2, zorder=3)
        ax.plot([t["s"][0], RBL], [t["s"][1], t["s"][1]], color=INK, lw=1.2, zorder=3)
    dot(ax, RBL, pre["s"][1], color=INK)
    text(ax, pre["g"][0] - 0.05, pre["g"][1], "PRE_N", fs=8, ha="right", color=INK)
    text(ax, 12.45, 4.55, "프리차지\nP 6.0/0.6", fs=7.4, va="center")
    sa = gate_inv(ax, 14.9, 3.6, s=0.8)
    ax.plot([RBL, sa["i"][0]], [3.6, 3.6], color=INK, lw=1.2, zorder=3)
    sbx = 16.25
    ax.plot([sa["o"][0], sbx, sbx, kp["g"][0]], [3.6, 3.6, kp["g"][1], kp["g"][1]], color=INK, lw=1.2, zorder=3)
    text(ax, 16.4, 4.75, "keeper\nP 1.8/1.8", fs=7.4, va="center")
    text(ax, sbx + 0.1, 3.75, "SB", fs=8.5, color=INK, weight="bold")
    dot(ax, sbx, 3.6, color=INK)
    oi = gate_inv(ax, sbx, 1.6, s=0.8, left=True)
    ax.plot([sbx, sbx], [3.6, 1.6], color=INK, lw=1.2, zorder=3)
    tag(ax, 12.6, 1.25, 2.0, 0.7, "SENSE (= Q)", fs=8)
    ax.plot([oi["o"][0], 14.6], [1.6, 1.6], color=INK, lw=1.2, zorder=3)
    text(ax, 15.3, 3.05, "센스 P 9.0 · N 3.6", fs=7.2, ha="center", va="top")
    text(ax, 15.6, 1.05, "출력 P 9.0 · N 3.6", fs=7.2, ha="center", va="top")
    save(fig, "op_column.png")


# ------------------------------------------------------------------ 4. one column writing and reading
def _pwl(steps, tr=0.5e-9):
    """steps: [(t, v), ...] starting at t = 0; each change takes tr."""
    pts = [f"0 {steps[0][1]}"]
    for (t, v), (_, v0) in zip(steps[1:], steps):
        if v != v0:
            pts += [f"{t:.4g} {v0}", f"{t + tr:.4g} {v}"]
    return "PWL(" + " ".join(pts) + ")"


def wave_deck(vdd=5.0, corner="TT", temp=27):
    """Write 0, read, write 1, read on one column: the selected cell, a cell of another row holding 0 on the same
    bit lines and 13 more unselected read ports at their leakiest (QB = 1), with the drawn column circuits.
    Cycle 40 ns: CLK = 0 for 20 ns (inputs change 2 ns in), then CLK = 1. WWL = CLK and WE, RWL = CLK and not
    WE, PRE_N = CLK, as the control block makes them."""
    sys.path.insert(0, str(REPO / "designs/etri050/sim/cell"))
    import cell8t as c  # noqa: E402
    ns = 1e-9
    clk = [(0, 0)] + [(t * ns, v * vdd) for k in range(4) for t, v in ((40 * k + 20, 1), (40 * k + 40, 0))]
    we = [(0, vdd), (42 * ns, 0), (82 * ns, vdd), (122 * ns, 0)]
    wd = [(0, vdd), (2 * ns, 0), (82 * ns, vdd)]
    wwl = [(0, 0), (20 * ns, vdd), (40 * ns, 0), (100 * ns, vdd), (120 * ns, 0)]
    rwl = [(0, 0), (60 * ns, vdd), (80 * ns, 0), (140 * ns, vdd), (160 * ns, 0)]
    sz = c.SZ
    deck = c.header(corner, temp) + f"""
VDD vdd 0 {vdd}
VDDA vdda 0 {vdd}
VDDW vddw 0 {vdd}
VCLK clk 0 {_pwl(clk)}
VPRE preb 0 {_pwl(clk)}
VWE we 0 {_pwl(we)}
VWD wd 0 {_pwl(wd)}
VWWL wwl 0 {_pwl(wwl)}
VRWL rwl 0 {_pwl(rwl)}
* write drivers (VDDW): BLB = not WD, BL = not BLB
{c.mos('wcp', 'blb', 'wd', 'vddw', 'vddw', 'pmos4', *sz['WDP'])}
{c.mos('wcn', 'blb', 'wd', 0, 0, 'nmos4', *sz['WDN'])}
{c.mos('wbp', 'bl', 'blb', 'vddw', 'vddw', 'pmos4', *sz['WDP'])}
{c.mos('wbn', 'bl', 'blb', 0, 0, 'nmos4', *sz['WDN'])}
CBL bl 0 25f
CBLB blb 0 25f
* read circuits (VDD): precharge, keeper, sense and output inverters
{c.mos('pre', 'rbl', 'preb', 'vdd', 'vdd', 'pmos4', *sz['PRE'])}
{c.mos('keep', 'rbl', 'sb', 'vdd', 'vdd', 'pmos4', *sz['KEEP'])}
{c.mos('sap', 'sb', 'rbl', 'vdd', 'vdd', 'pmos4', *sz['SAP'])}
{c.mos('san', 'sb', 'rbl', 0, 0, 'nmos4', *sz['SAN'])}
{c.mos('o2p', 'sense', 'sb', 'vdd', 'vdd', 'pmos4', *sz['OP'])}
{c.mos('o2n', 'sense', 'sb', 0, 0, 'nmos4', *sz['ON'])}
CRBL rbl 0 20f
COUT sense 0 30f
{c.cell('c0', 'q', 'qb', 'bl', 'blb', 'wwl', 'rwl', 'rbl', 'vdda', sz)}
{c.cell('c1', 'q1', 'qb1', 'bl', 'blb', '0', '0', 'rbl', 'vdda', sz)}
{c.mos('lk2', 'rbl', 0, 'nmx', 0, 'nmos4', *sz['RD2'], m=13)}
{c.mos('lk1', 'nmx', 'vdda', 0, 0, 'nmos4', *sz['RD1'], m=13)}
.ic v(q)={vdd} v(qb)=0 v(q1)=0 v(qb1)={vdd} v(rbl)={vdd} v(sb)=0 v(sense)={vdd} v(bl)={vdd} v(blb)=0
.tran 0.05n 172n uic
.control
run
wrdata op_wave.txt v(clk) v(we) v(wwl) v(rwl) v(bl) v(blb) v(q) v(qb) v(q1) v(rbl) v(sense)
.endc
.end
"""
    c.run("op_wave", deck)
    rows = [[float(x) for x in line.split()] for line in (Path(c.BUILD) / "op_wave.txt").read_text().splitlines()
            if line.strip()]
    names = ["clk", "we", "wwl", "rwl", "bl", "blb", "q", "qb", "q1", "rbl", "sense"]
    t = [r[0] * 1e9 for r in rows]
    return t, {n: [r[1 + 2 * i] for r in rows] for i, n in enumerate(names)}


def fig_wave():
    t, v = wave_deck()
    k0 = next(i for i, x in enumerate(t) if x >= 1.0)          # skip the start-up step of the initial conditions
    t, v = t[k0:], {n: w[k0:] for n, w in v.items()}
    panels = [("CLK\n(= PRE_N)", [("clk", BLUE, None)]), ("WE", [("we", BLUE, None)]),
              ("WWL · RWL", [("wwl", BLUE, None), ("rwl", ORANGE, None)]),
              ("BL · BLB", [("bl", BLUE, "BL"), ("blb", ORANGE, "BLB")]),
              ("Q · QB", [("q", BLUE, "Q"), ("qb", ORANGE, "QB"), ("q1", MUTED, None)]),
              ("RBL", [("rbl", BLUE, None)]), ("SENSE", [("sense", BLUE, None)])]
    fig, axes = plt.subplots(len(panels), 1, figsize=(10.5, 8.6), sharex=True,
                             gridspec_kw=dict(hspace=0.18, left=0.12, right=0.88, top=0.9, bottom=0.1))
    for ax, (name, traces) in zip(axes, panels):
        for k in range(4):
            ax.axvspan(40 * k + 20, 40 * k + 40, color="#f1f0ec", zorder=0, lw=0)
        for k in range(1, 5):
            ax.axvline(40 * k, color=BASE, lw=0.8, ls=":", zorder=1)
        for key, col, lab in traces:
            ls = (0, (4, 2)) if key == "q1" else "-"
            ax.plot(t, v[key], color=col, lw=1.7, ls=ls, zorder=3)
            if lab:
                ax.text(173, v[key][-1], lab, color=INK2, fontsize=8.5, va="center", ha="left",
                        fontweight="bold" if key != "q1" else "normal")
        ax.set_ylim(-0.6, 5.8)
        ax.set_yticks([0, 5])
        ax.set_yticklabels(["0", "5 V"], fontsize=8, color=MUTED)
        ax.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=9.5, color=INK, labelpad=8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(BASE)
        ax.tick_params(axis="both", colors=MUTED, length=3)
    axes[-1].set_xlim(0, 172)
    axes[-1].set_xticks(range(0, 172, 20))
    axes[-1].set_xlabel("시간 (ns)", fontsize=9, color=INK2)
    for k, s in enumerate(["쓰기 0 (WD = 0)", "읽기 → SENSE = 0", "쓰기 1 (WD = 1)", "읽기 → SENSE = 1"]):
        axes[0].text(40 * k + 20, 7.0, s, ha="center", va="bottom", fontsize=9, color=INK, fontweight="bold")
    axes[0].text(0, 9.4, "한 열의 쓰기 · 읽기  —  TT 27 °C, VDD = VDDA = VDDW = 5 V, 공식 PDK 모델 (ngspice)",
                 fontsize=9.5, color=INK, va="bottom")
    axes[5].annotate("Q = 0: RD1 · RD2가 방전", xy=(63, 1.0), xytext=(84, 2.2), fontsize=8, color=INK2,
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    axes[5].annotate("Q = 1: keeper가 붙잡음", xy=(150, 5.0), xytext=(124, 2.2), fontsize=8, color=INK2,
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    axes[6].annotate("CLK = 0: 프리차지 값 1", xy=(90, 5.0), xytext=(88, 1.6), fontsize=8, color=INK2,
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    for x0, lab in ((30, "WWL"), (70, "RWL"), (110, "WWL"), (150, "RWL")):
        axes[2].text(x0, 2.5, lab, ha="center", va="center", fontsize=8.5, color=INK, fontweight="bold")
    axes[4].text(122, 1.25, "점선: 같은 열 다른 행의 Q (0 유지)", fontsize=8, color=INK2)
    axes[4].annotate("WWL = 1에서 뒤집힘", xy=(21.5, 2.5), xytext=(26, 1.0), fontsize=8, color=INK2,
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    fig.text(0.1, 0.012, "회색 띠: CLK = 1 (접근).  쓰기 드라이버는 늘 켜져 있어 BL · BLB는 WD를 따르고, "
             "WWL이 열린 행만 바뀐다.  부하: BL · BLB 25 fF, RBL 20 fF, 같은 열의 읽기 포트 14개 누설",
             fontsize=8, color=MUTED)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "op_wave.png", dpi=170, facecolor="white")
    plt.close(fig)
    print("docs/img/op_wave.png")


# ------------------------------------------------------------------ 5. canary latch
def supply(ax, x, y, name, color=INK):
    ax.plot([x - 0.22, x + 0.22], [y, y], color=color, lw=1.6, zorder=4)
    text(ax, x, y + 0.1, name, fs=7.8, ha="center", va="bottom", color=color, weight="bold")


def fig_canary():
    W, H = 15.6, 12.4
    fig, ax = canvas(W, H)
    # (a) circuit
    text(ax, 0.4, 12.05, "카나리 k (8개, k = 0 … 7)", fs=9.5, color=INK, weight="bold")
    box(ax, 0.4, 7.25, 9.0, 4.45, "", dom="VDDA", r=0.1)
    text(ax, 0.6, 11.4, "래치  ·  VDDA (셀과 같은 전원)", fs=8.6, color=INK, weight="bold")
    box(ax, 0.4, 4.15, 9.0, 2.85, "", dom="VDD", r=0.1)
    text(ax, 0.6, 6.7, "읽기 게이트  ·  VDD", fs=8.6, color=INK, weight="bold")
    # CINV: P1 over N1, gates = B, output = A
    p1 = mos(ax, 2.6, 9.95, kind="p")
    n1 = mos(ax, 2.6, 8.55)
    supply(ax, p1["d"][0], p1["d"][1], "VDDA")
    gnd(ax, *n1["s"], color=INK)
    ax.plot([p1["s"][0], n1["d"][0]], [p1["s"][1], n1["d"][1]], color=INK, lw=1.2, zorder=3)
    ax.plot([p1["g"][0], n1["g"][0]], [p1["g"][1], n1["g"][1]], color=INK, lw=1.2, zorder=3)
    ay = (p1["s"][1] + n1["d"][1]) / 2
    text(ax, 3.1, 10.25, "P1  W 1.8 µm\nL 2.4 – 30 µm (약함)", fs=7.6, va="center")
    text(ax, 3.1, 8.3, "N1  W 3.6–18 µm\nL 0.6 µm (넓음)", fs=7.6, va="center")
    # latch NOR (A, CSET) -> B
    xl = gate_or(ax, 6.1, ay, s=1.0, bubble=True)
    ax.plot([p1["s"][0], 4.6, 4.6, xl["i"][0][0]], [ay, ay, xl["i"][0][1], xl["i"][0][1]], color=INK, lw=1.2,
            zorder=3)
    dot(ax, p1["s"][0], ay, color=INK)
    text(ax, p1["s"][0] + 0.12, ay + 0.17, "A", fs=9, color=INK, weight="bold")
    ax.plot([5.3, xl["i"][1][0]], [xl["i"][1][1]] * 2, color=INK, lw=1.2, zorder=3)
    text(ax, 5.25, xl["i"][1][1], "CSET", fs=8, ha="right", color=INK)
    text(ax, 6.55, ay - 0.62, "NOR2X1", fs=7.2, ha="center", va="top")
    ax.plot([xl["o"][0], 7.9, 7.9, 1.5, 1.5, p1["g"][0]], [ay, ay, 11.05, 11.05, ay, ay], color=INK, lw=1.2,
            zorder=3)
    dot(ax, p1["g"][0], ay, color=INK)
    text(ax, 8.0, ay + 0.17, "B", fs=9, color=INK, weight="bold")
    # read-out NOR (A, CRD_N) -> CAN, VDD
    xr = gate_or(ax, 6.1, 5.3, s=1.0, bubble=True)
    ax.plot([4.6, 4.6, xr["i"][0][0]], [ay, xr["i"][0][1], xr["i"][0][1]], color=INK, lw=1.2, zorder=3)
    dot(ax, 4.6, ay, color=INK)
    ax.plot([5.3, xr["i"][1][0]], [xr["i"][1][1]] * 2, color=INK, lw=1.2, zorder=3)
    text(ax, 5.25, xr["i"][1][1], "CRD_N", fs=8, ha="right", color=INK)
    text(ax, 6.55, 5.3 - 0.62, "NOR2X1", fs=7.2, ha="center", va="top")
    tag(ax, 7.75, 4.95, 1.5, 0.7, "CAN[k]", fs=8)
    ax.plot([xr["o"][0], 7.75], [5.3, 5.3], color=INK, lw=1.2, zorder=3)
    text(ax, 0.6, 4.55, "CRD_N = 1이면 직렬 PMOS가 꺼져 CAN = 0, VDD 전류 5 fA", fs=7.6)

    # state table and operation
    tx = 10.0
    text(ax, tx, 11.55, "상태", fs=9, color=INK, weight="bold")
    rows = [("", "A", "B", "CAN (CRD_N = 0)"), ("세트", "1", "0", "0"), ("잃음", "0", "1", "1")]
    for i, r in enumerate(rows):
        y = 11.05 - i * 0.45
        for x, c in zip((tx, tx + 1.4, tx + 2.1, tx + 2.8), r):
            text(ax, x, y, c, fs=8.4, color=INK if i else INK2, weight="bold" if i == 0 else "normal")
    ax.plot([tx, tx + 5.2], [10.83, 10.83], color=BASE, lw=0.8)
    steps = ["세트: CSET = 1 → B = 0 → P1 켜짐, N1 꺼짐 → A = VDDA",
             "유지: A = 1은 P1의 전류가 N1의 꺼진 누설을 이겨야 남는다",
             "VDDA를 보존 전압 아래로: P1이 지고 A가 내려가면 NOR가\nB를 올려 N1을 켠다 → 잃음 (A = 0, B = 1)",
             "VDDA를 5 V로 되돌려도 잃은 상태가 남는다",
             "사다리: k가 클수록 P1이 길고(약함) N1이 넓어(누설 큼)\n더 높은 VDDA에서 잃는다: C7 0.575 → C0 0.428 V (TT)",
             "읽기: CRD_N = 0이면 CAN = not A. VDDA = VDD에서만 읽는다"]
    y = 9.75
    for st in steps:
        text(ax, tx, y, st, fs=7.9, color=INK, va="top")
        y -= 0.5 + 0.38 * st.count("\n")

    # (b) one experiment step
    text(ax, 0.4, 3.55, "실험 한 단계 (spec.md 측정 계획 6)", fs=9.5, color=INK, weight="bold")
    hi, lo = 2.75, 1.25
    xs = [0.6, 6.2, 7.0, 10.0, 10.8, 15.2]
    ax.plot([xs[0], xs[1], xs[2], xs[3], xs[4], xs[5]], [hi, hi, lo, lo, hi, hi], color=AQUA, lw=2.0, zorder=3)
    text(ax, 0.6, hi + 0.18, "VDDA (와 VDDW) 5 V", fs=7.8, va="bottom", color=INK2)
    text(ax, 7.1, lo - 0.15, "V_hold (0.75 V부터 10 mV씩 낮춤), 30 s 이상", fs=7.8, va="top", color=INK2)
    marks = [(1.6, "세트 보기 FI_POS 100 · 101\n(CLK = 1을 100 ns 이상)"), (4.2, "카나리 보기\n010 · 011 → 0000"),
             (12.0, "카나리 보기 010 · 011\n잃은 카나리 = 1"), (14.3, "원시 보기\n실패 지도")]
    for x, lab in marks:
        ax.plot([x, x], [hi - 0.12, hi + 0.12], color=INK, lw=1.4, zorder=4)
        text(ax, x, hi - 0.3, lab, fs=7.6, ha="center", va="top", color=INK)
    text(ax, 8.5, hi + 0.18, "읽기는 모두 VDDA = 5 V에서", fs=7.6, ha="center", va="bottom", color=MUTED)
    save(fig, "op_canary.png")


# ------------------------------------------------------------------ 6. retention ladder per corner
# docs/verification.md section 12 (sim/cell/canary_sim.py ladder): retention voltage (V) at 27 C
LADDER_V = {"SF": [0.303, 0.320, 0.341, 0.361, 0.380, 0.392, 0.414, 0.447],
            "FF": [0.374, 0.390, 0.412, 0.433, 0.450, 0.463, 0.485, 0.518],
            "TT": [0.428, 0.443, 0.465, 0.487, 0.506, 0.520, 0.541, 0.575],
            "SS": [0.477, 0.493, 0.520, 0.540, 0.558, 0.573, 0.596, 0.633],
            "FS": [0.553, 0.571, 0.595, 0.616, 0.635, 0.649, 0.672, 0.707]}
CELL_V = {"SF": 0.273, "FF": 0.342, "TT": 0.387, "SS": 0.432, "FS": 0.507}
RAMP = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95"]


def fig_ladder():
    corners = list(LADDER_V)
    xs = range(len(corners))
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    fig.subplots_adjust(left=0.1, right=0.83, top=0.86, bottom=0.12)
    ends = []
    for k in range(8):
        ys = [LADDER_V[c][k] for c in corners]
        ax.plot(xs, ys, color=RAMP[k], lw=2.0, marker="o", ms=5.5, mec="white", mew=1.0, zorder=3,
                label="카나리 C0 (가장 낮음)" if k == 0 else ("카나리 C7 (가장 높음)" if k == 7 else None))
        ends.append((ys[-1], f"C{k}"))
    ys = [CELL_V[c] for c in corners]
    ax.plot(xs, ys, color=ORANGE, lw=2.0, marker="o", ms=5.5, mec="white", mew=1.0, zorder=3,
            label="셀 (가장 나쁜 쪽)")
    ends.append((ys[-1], "셀"))
    placed, gap = [], 0.0175                   # end labels at least gap apart, leader lines where moved
    for y, lab in sorted(ends):
        yl = max(y, placed[-1] + gap) if placed else y
        placed.append(yl)
        xe = len(corners) - 1
        if abs(yl - y) > 1e-4:
            ax.plot([xe + 0.03, xe + 0.1], [y, yl], color=BASE, lw=0.8)
        ax.text(xe + 0.12, yl, lab, fontsize=8.5, color=INK2, va="center")
    for x, c in zip(xs, corners):
        ax.text(x, CELL_V[c] - 0.025, f"{CELL_V[c]:.3f}", fontsize=7.8, color=INK2, ha="center", va="top")
        ax.text(x, LADDER_V[c][7] + 0.02, f"{LADDER_V[c][7]:.3f}", fontsize=7.8, color=INK2, ha="center",
                va="bottom")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"{c} 27 °C" for c in corners], fontsize=9, color=INK2)
    ax.set_xlim(-0.35, len(corners) - 1 + 0.45)
    ax.set_ylim(0.22, 0.76)
    ax.set_ylabel("보존 전압 (V)", fontsize=9.5, color=INK2)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.grid(axis="y", color=GRID, lw=0.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(BASE)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False, labelcolor=INK2)
    fig.text(0.1, 0.94, "보존 전압 사다리: 카나리 8개와 셀, 공정 코너 5개 (27 °C)", fontsize=10.5,
             color=INK, fontweight="bold")
    fig.text(0.1, 0.9, "VDDA를 내리면 위에서부터(C7) 차례로 값을 잃고, 셀은 사다리 아래에서 실패한다. "
             "코너가 바뀌면 사다리와 셀이 함께 움직인다", fontsize=8.5, color=INK2)
    fig.text(0.1, 0.02, "출처: sim/cell/canary_sim.py ladder (verification.md 12절). 셀: 쓰기 드라이버가 Q = 1 옆 BL을 "
             "0으로 붙잡는 가장 나쁜 쪽", fontsize=7.8, color=MUTED)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "op_ladder.png", dpi=170, facecolor="white")
    plt.close(fig)
    print("docs/img/op_ladder.png")


# ------------------------------------------------------------------ 7. ring-oscillator bank and divider
def fig_ro():
    W, H = 16.4, 11.6
    fig, ax = canvas(W, H)
    # (a) one ring
    text(ax, 0.3, 11.3, "(a) 링 하나: 31단 (RO 뱅크에 INV · NAND · NOR 세 개, VDD)", fs=9.5, color=INK, weight="bold")
    tag(ax, 0.3, 8.25, 1.35, 0.6, "RO_EN[i]", fs=8)
    y0 = 9.3
    st0 = gate_and(ax, 2.5, y0, s=0.9, bubble=True)
    ax.plot([1.65, 2.1, 2.1, st0["i"][1][0]], [8.55, 8.55, st0["i"][1][1], st0["i"][1][1]], color=INK, lw=1.2)
    text(ax, 2.9, y0 - 0.55, "0단 NAND2X1", fs=7.4, ha="center", va="top")
    xs, prev = [4.3, 5.6, 6.9, 9.0], st0["o"]
    for k, x in enumerate(xs):
        if k == 3:
            text(ax, 8.15, y0, "…", fs=12, ha="center", color=INK)
            ax.plot([prev[0], 7.75], [y0, y0], color=INK, lw=1.2)
            ax.plot([8.55, x], [y0, y0], color=INK, lw=1.2)
        else:
            ax.plot([prev[0], x], [y0, y0], color=INK, lw=1.2)
        g = gate_inv(ax, x, y0, s=0.7)
        text(ax, x + 0.3, y0 - 0.45, ["1", "2", "3", "30"][k], fs=7.6, ha="center", va="top")
        prev = g["o"]
    ax.plot([prev[0], 10.0, 10.0, 2.2, 2.2, st0["i"][0][0]], [y0, y0, 10.4, 10.4, st0["i"][0][1], st0["i"][0][1]],
            color=INK, lw=1.2)
    text(ax, 6.1, 10.5, "30단 출력 → 0단 A (되먹임)", fs=7.6, ha="center", va="bottom")
    tx = 3.75
    dot(ax, tx, y0, color=INK)
    ax.plot([tx, tx], [y0, 8.0], color=INK, lw=1.2)
    t1 = gate_inv(ax, tx, 8.0, s=0.55)
    ax.plot([t1["o"][0], 4.85], [8.0, 8.0], color=INK, lw=1.2)
    t2 = gate_inv(ax, 4.85, 8.0, s=0.75)
    tag(ax, 6.2, 7.68, 1.45, 0.64, "TAP[i]", fs=8)
    ax.plot([t2["o"][0], 6.2], [8.0, 8.0], color=INK, lw=1.2)
    text(ax, 5.3, 8.45, "탭 INVX1 → INVX4", fs=7.4, ha="center", va="center")
    notes = ["단 1–30", "  INV 링: INVX1", "  NAND 링: NAND2X1, B = en1 (NMOS 직렬)", "  NOR 링: NOR2X1, B = not en2 (PMOS 직렬)",
             "RO_EN = 0: 0단 출력이 1로 고정 → 링 정지, TAP = 1", "RO_EN = 1: 31번 반전 → 진동",
             "f = 1 / (2 × 31 × 단 지연)"]
    for i, n in enumerate(notes):
        text(ax, 10.6, 10.55 - i * 0.43, n, fs=7.9, color=INK)

    # (b) divider
    text(ax, 0.3, 6.95, "(b) 분주기 ro_div: 도는 링 ÷ 256 (VDD)", fs=9.5, color=INK, weight="bold")
    for i, y in enumerate((6.1, 5.55, 5.0)):
        tag(ax, 0.3, y - 0.24, 1.25, 0.48, f"TAP{i}", fs=7.8)
    a3 = gate_and(ax, 2.2, 5.55, s=1.0, n=3)
    for (x, y), y_in in zip(a3["i"], (6.1, 5.55, 5.0)):
        ax.plot([1.55, 1.9, 1.9, x], [y_in, y_in, y, y], color=INK, lw=1.1)
    text(ax, 2.6, 4.98, "AND", fs=7.2, ha="center", va="top")
    bx = [3.8, 5.3, 6.8, 9.0]
    prev = a3["o"]
    for k, x in enumerate(bx):
        if k == 3:
            text(ax, 8.4, 5.55, "…", fs=12, ha="center", color=INK)
            wire(ax, [(prev[0], 5.55), (7.95, 5.55)], arrow=False, color=INK)
            wire(ax, [(8.75, 5.55), (x, 5.55)], color=INK)
        else:
            wire(ax, [(prev[0], 5.55), (x, 5.55)], color=INK)
        box(ax, x, 5.15, 1.0, 0.8, f"T{[0, 1, 2, 7][k]}", fs=8.6, ec=INK)
        prev = (x + 1.0, 5.55)
    text(ax, 3.4, 5.72, "dclk0", fs=7.2, ha="center", va="bottom")
    text(ax, 6.05, 6.15, "앞 단의 not q가 다음 단의 클록: 단마다 ÷2, 8단 ÷256", fs=7.6, ha="center", va="bottom")
    ax.plot([10.0, 10.5], [5.55, 5.55], color=INK, lw=1.2)
    text(ax, 10.25, 5.68, "q7", fs=7.2, ha="center", va="bottom")
    di = gate_inv(ax, 10.5, 5.55, s=0.6)
    tag(ax, 11.65, 5.2, 4.4, 0.7, "RO_DIV → 제어 블록 → DOUT0 (RO 보기)", fs=8)
    ax.plot([di["o"][0], 11.65], [5.55, 5.55], color=INK, lw=1.2)
    tag(ax, 0.3, 3.86, 1.5, 0.58, "RO_EN[2:0]", fs=7.8)
    o3 = gate_or(ax, 2.2, 4.15, s=0.8, n=3)
    for (x, y) in o3["i"]:
        ax.plot([1.8, x], [y, y], color=INK, lw=1.0)
    ax.plot([o3["o"][0], 9.5], [4.15, 4.15], color=INK, lw=1.2)
    for x in bx:
        ax.plot([x + 0.5, x + 0.5], [4.15, 5.15], color=INK, lw=1.0)
        dot(ax, x + 0.5, 4.15, color=INK)
    text(ax, 3.3, 3.95, "rst_n: 0이면 모든 단 q = 0 → RO_DIV = 1", fs=7.6, va="top")

    # (c) waveform sketch, time in ring periods
    text(ax, 0.3, 3.05, "(c) 동작 (가로: 링 주기, 그림은 개념도)", fs=9.5, color=INK, weight="bold")
    x0, x1, T0, T1 = 2.2, 15.9, 0.0, 620.0
    X = lambda t: x0 + (t - T0) / (T1 - T0) * (x1 - x0)  # noqa: E731
    ten = 40.0
    rows = {"RO_EN[i]": 2.4, "TAP[i]": 1.55, "RO_DIV": 0.7}
    for name, y in rows.items():
        text(ax, 1.9, y + 0.2, name, fs=8.2, ha="right", color=INK)
    hgt = 0.42
    y = rows["RO_EN[i]"]
    ax.plot([X(0), X(ten), X(ten), X(T1)], [y, y, y + hgt, y + hgt], color=BLUE, lw=1.8)
    y = rows["TAP[i]"]
    ax.plot([X(0), X(ten)], [y + hgt, y + hgt], color=BLUE, lw=1.8)
    ax.add_patch(Rectangle((X(ten), y), X(T1) - X(ten), hgt, fc="#cfe1f8", ec=BLUE, lw=1.0, hatch="||||"))
    text(ax, X(330), y + hgt + 0.05, "링 주파수 44–92 MHz (그리기엔 너무 빠름)", fs=7.4, ha="center", va="bottom")
    y = rows["RO_DIV"]
    edges = [ten + 128.6, ten + 128.6 + 128, ten + 128.6 + 256, ten + 128.6 + 384]
    pts, lv = [(X(0), y + hgt)], 1
    for e in edges:
        pts += [(X(e), y + hgt * lv), (X(e), y + hgt * (1 - lv))]
        lv = 1 - lv
    pts.append((X(T1), y + hgt * lv))
    ax.plot(*zip(*pts), color=BLUE, lw=1.8)
    for a, b, lab, yy in ((ten, edges[0], "128.6 주기", y - 0.12), (edges[0], edges[1], "128 주기", y - 0.12),
                          (edges[0], edges[2], "주기 256 → DOUT0 174–358 kHz", y + hgt + 0.1)):
        ax.annotate("", xy=(X(b), yy), xytext=(X(a), yy),
                    arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8, shrinkA=0, shrinkB=0))
        text(ax, (X(a) + X(b)) / 2, yy - 0.05 if yy < y else yy + 0.05, lab, fs=7.4, ha="center",
             va="top" if yy < y else "bottom")
    save(fig, "op_ro.png")


FIGS = {"block": fig_block, "ctrl": fig_ctrl, "column": fig_column, "wave": fig_wave, "canary": fig_canary, "ladder": fig_ladder, "ro": fig_ro}


def main(argv):
    names = argv or list(FIGS)
    for n in names:
        FIGS[n]()


if __name__ == "__main__":
    main(sys.argv[1:])
