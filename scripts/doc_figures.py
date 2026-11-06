#!/usr/bin/env python3
"""Figures for docs/guide.md, drawn from the GDS files with KLayout (scripts/render_gds.py) and labelled with
Pillow: the final chip with its pins, the core, the reliability monitor over the top channel, the SRAM macro,
the column circuits, the 8T cell and the control block.

  python3 scripts/doc_figures.py              # -> docs/img/*.png

Inputs: designs/etri050/chip/final/ecc_sram_Top.gds.gz, designs/etri050/ctrl/macro/ecc_fi_ctrl.gds.gz and the
SRAM blocks that check_all.sh (or gen/sram8t.py, gen/colper.py, gen/decap.py) writes to
designs/etri050/sram/build. Korean labels need a CJK font (Noto Sans CJK or Nanum).
Coordinates below are in um, the same as in the GDS files.
"""
from __future__ import annotations

import csv
import gzip
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs/img"
KIT = Path(os.environ.get("ETRI050_DK", REPO / ".pdk/ETRI050_DesignKit"))
LYP = KIT / "tech/ETRI050_CMOS.lyp"
SRAM = REPO / "designs/etri050/sram/build"
CHIP = REPO / "designs/etri050/chip"
FONTS = [("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 1),
         ("/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc", 1),
         ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", 0)]
WHITE, GREY, YELLOW, CYAN = (255, 255, 255), (200, 200, 200), (255, 220, 90), (90, 220, 255)
PIN_COLOUR = dict(PIC=(120, 190, 255), POB8=(255, 170, 60), PVDD=(255, 100, 100), PVSS=(200, 200, 200),
                  PANA=(120, 235, 120))
# block outlines (die um), as chip/assemble.py places them (build/ecc_sram_nets.json, block bounding boxes)
CTRL = (470, 560, 965.9, 1080.05)
MON = {"canary": (554, 1158.2, 824.6, 1235.0), "robank": (829, 1158.2, 1174.1, 1357.1),
       "ro_div": (1184, 1158.2, 1403.6, 1309.1)}


def font(size):
    for path, index in FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size, index=index)
    return ImageFont.load_default(size)


class Fig:
    """A KLayout render of a window (x1, y1, x2, y2) and drawing helpers in layout coordinates."""

    def __init__(self, gds, box, width, margin=(0, 0, 0, 0)):
        """margin: empty space (px) left, top, right and bottom of the render, for labels."""
        self.box, self.w, self.m = box, width, margin
        x1, y1, x2, y2 = box
        self.h = max(1, round(width * (y2 - y1) / (x2 - x1)))
        tmp = Path(tempfile.mkdtemp())
        cmd = ["klayout", "-b", "-r", str(REPO / "scripts/render_gds.py"), "-rd", f"gds={gds}",
               "-rd", f"png={tmp / 'r.png'}", "-rd", f"width={width}",
               "-rd", "box=" + ",".join(f"{v:g}" for v in box)]
        if LYP.exists():
            cmd += ["-rd", f"lyp={LYP}"]
        subprocess.run(cmd, check=True, capture_output=True)
        render = Image.open(tmp / "r.png").convert("RGBA")
        shutil.rmtree(tmp)
        ml, mt, mr, mb = margin
        self.im = Image.new("RGBA", (ml + render.size[0] + mr, mt + render.size[1] + mb), (0, 0, 0, 255))
        self.im.paste(render, (ml, mt))
        self.top = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.top)

    def px(self, x, y):
        x1, y1, x2, y2 = self.box
        return self.m[0] + (x - x1) * self.w / (x2 - x1), self.m[1] + (y2 - y) * self.h / (y2 - y1)

    def rect(self, x1, y1, x2, y2, colour=YELLOW, width=3):
        (a, b), (c, d) = self.px(x1, y2), self.px(x2, y1)
        self.d.rectangle([a, b, c, d], outline=colour + (255,), width=width)

    def line(self, x1, y1, x2, y2, colour=GREY, width=2):
        self.d.line([self.px(x1, y1), self.px(x2, y2)], fill=colour + (255,), width=width)

    def text(self, x, y, s, size=20, colour=WHITE, anchor="mm", angle=0):
        """Text on a dark box; anchor as in Pillow ('lm' = left end at x, y); angle 90 reads upwards."""
        f, pad = font(size), max(3, size // 5)
        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        l, t, r, b = probe.multiline_textbbox((0, 0), s, font=f, spacing=4)
        tile = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 185))
        ImageDraw.Draw(tile).multiline_text((pad - l, pad - t), s, font=f, fill=colour + (255,), spacing=4)
        if angle:
            tile = tile.rotate(angle, expand=True)
        w, h = tile.size
        cx, cy = self.px(x, y)
        ox = {"l": cx, "m": cx - w / 2, "r": cx - w}[anchor[0]]
        oy = {"t": cy, "m": cy - h / 2, "b": cy - h}[anchor[1]]
        self.top.alpha_composite(tile, (int(round(ox)), int(round(oy))))

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        im = Image.alpha_composite(self.im, self.top).convert("RGB")
        im = im.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
        im.save(OUT / name, optimize=True)
        print(f"wrote docs/img/{name} ({im.size[0]} x {im.size[1]} px)")


def pad_centre(pad):
    """Pad openings of the 28-pin frame: 7 per side, 135 um apart from 545 um, 140 um in from the die origin."""
    side, k = pad[0], int(pad[1:]) - 1
    p = 545 + 135 * k
    return {"W": (140, p), "E": (1760, p), "S": (p, 140), "N": (p, 1760)}[side]


def package_pin(pad):
    side, k = pad[0], int(pad[1:])
    return {"W": 8 - k, "S": 7 + k, "E": 14 + k, "N": 29 - k}[side]


def chip(gds):
    f = Fig(gds, (-95, -95, 1995, 1995), 1600)
    die0, die1 = 97.5, 1802.5
    with open(CHIP / "pins.csv", newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pad, cell = row["pad"], row["cell"]
            name = {"PVDD": "VDD", "PVSS": "VSS"}.get(row["pin"], row["pin"])
            label = f"{package_pin(pad)} {name}"
            x, y = pad_centre(pad)
            colour = PIN_COLOUR[cell]
            f.rect(x - 40, y - 40, x + 40, y + 40, colour, 2)
            side = pad[0]
            if side == "W":
                f.text(die0 - 8, y, label, 19, colour, "rm")
            elif side == "E":
                f.text(die1 + 8, y, label, 19, colour, "lm")
            elif side == "N":
                f.text(x, die1 + 8, label, 19, colour, "mb", angle=90)
            else:
                f.text(x, die0 - 8, label, 19, colour, "mt", angle=90)
    blocks = [(CTRL, "제어 블록\necc_fi_ctrl"),
              ((1065, 567.4, 1246.5, 1066.3), "SRAM\n매크로"),
              ((1290, 470, 1442.4, 756.5), "디커플링\nVDDW"),
              ((1290, 770, 1442.4, 913.7), "디커플링\nVDDA"),
              (MON["canary"], "카나리"), (MON["robank"], "RO 뱅크"), (MON["ro_div"], "분주기")]
    for (x1, y1, x2, y2), s in blocks:
        f.rect(x1, y1, x2, y2, YELLOW, 3)
        f.text((x1 + x2) / 2, (y1 + y2) / 2, s, 22, YELLOW)
    f.rect(442, 442, 1458, 1458, CYAN, 1)
    f.text(640, 1320, "코어 영역 1016 × 1016 µm", 20, CYAN)
    f.save("chip.png")


def core(gds):
    f = Fig(gds, (440, 440, 1460, 1460), 1600)
    f.rect(*CTRL, YELLOW, 3)
    f.text(715, 820, "제어 블록 ecc_fi_ctrl\n표준셀 375개 (qflow 배치·배선)\n부호기 · 결함 마스크 · 행 해독\n"
           "기준 워드(주소 15) · 신드롬 · SEC/DED\n보기: 원시 · 카나리 · RO", 22, YELLOW)
    f.rect(1065, 567.4, 1246.5, 1066.3, YELLOW, 3)
    f.text(1155.75, 860, "SRAM 매크로\n8T 셀 15 × 8\n+ 컬럼 회로", 22, YELLOW)
    f.rect(1290, 470, 1442.4, 756.5, YELLOW, 3)
    f.text(1366.2, 613, "VDDW\n디커플링\n57 pF", 21, YELLOW)
    f.rect(1290, 770, 1442.4, 913.7, YELLOW, 3)
    f.text(1366.2, 842, "VDDA\n디커플링\n28.5 pF", 21, YELLOW)
    f.text(1015, 905, "워드라인\n30개\nWWL·RWL", 17, CYAN)
    f.text(760, 500, "아래 채널: S 패드 입력, PRE_N · WD · SENSE", 18, CYAN)
    for name, s in (("canary", "카나리 래치 8"), ("robank", "RO 뱅크 INV·NAND·NOR"), ("ro_div", "분주기 ÷256")):
        x1, y1, x2, y2 = MON[name]
        f.rect(x1, y1, x2, y2, YELLOW, 3)
        f.text((x1 + x2) / 2, (y1 + y2) / 2, s, 20, YELLOW)
    f.text(1300, 1110, "위 채널 13트랙", 17, CYAN)
    f.text(690, 1380, "FI_POS 띠 · VDD 띠 (N4 패드 → 제어 블록)", 17, CYAN)
    f.line(690, 1392, 690, 1437, CYAN)
    for y, s in ((549, "VSS"), (583, "VDDW"), (902, "VDDA")):    # metal3 straps between macro and decaps
        f.text(1268, y, s, 15, CYAN)
    f.save("core.png")


def macro():
    f = Fig(SRAM / "sram_macro.gds", (-17, -90, 168, 413), 420, (300, 10, 400, 10))
    f.rect(0, 0, 144, 409.5, YELLOW, 2)
    f.text(176, 300, "8T 셀 어레이 15행 × 8열\n셀 전원 VDDA\n행 27.3 µm · 열 18.0 µm", 20, YELLOW, "lm")
    f.line(176, 300, 140, 300, YELLOW)
    f.text(176, 180, "전원 버스 (metal2)\nVSS · VDDA · VDD · VDDW", 18, CYAN, "lm")
    f.line(176, 180, 160, 180, CYAN)
    f.rect(0, -51, 144, -4.5, (255, 140, 140), 2)
    f.text(176, -24, "읽기 회로 (VDD)\n프리차지 · keeper\n센스 · 출력 인버터", 18, (255, 140, 140), "lm")
    f.line(176, -24, 144, -24, (255, 140, 140))
    f.rect(0, -84.3, 144, -55.2, (140, 255, 140), 2)
    f.text(176, -72, "쓰기 드라이버 (VDDW)\nBLB = not WD\nBL = not BLB", 18, (140, 255, 140), "lm")
    f.line(176, -72, 144, -72, (140, 255, 140))
    f.text(-25, 300, "워드라인 접점\nWWL · RWL 15쌍\n(제어 블록에서)", 18, CYAN, "rm")
    f.line(-25, 300, -13, 300, CYAN)
    f.text(-25, -60, "아래 핀\nSENSE 8 · WD 8\nPRE_N · 전원", 18, WHITE, "rm")
    f.line(-25, -60, -8, -86, WHITE)
    f.save("macro.png")


def column():
    f = Fig(SRAM / "sram_macro.gds", (-2, -90, 38, 8), 480, (0, 0, 520, 0))
    labels = [(3, "어레이 맨 아래 행 (셀)", YELLOW),
              (-7.3, "RBL 꺾임 · VSS 레일", GREY),
              (-11.1, "센스 · 출력 인버터 N (손가락 2개씩)", CYAN),
              (-25.7, "센스 · 출력 인버터 P (VDD)", CYAN),
              (-30.8, "VDD 레일", (255, 120, 120)),
              (-36.6, "keeper P 1.8/1.8 · 프리차지 P 6.0/0.6", CYAN),
              (-49.9, "PRE_N (프리차지 게이트)", CYAN),
              (-57.2, "VDDW 레일", (140, 255, 140)),
              (-63.0, "비트라인 드라이버 P 6.0/0.6 (VDDW)", (140, 255, 140)),
              (-78.9, "비트라인 드라이버 N 3.0/0.6", (140, 255, 140)),
              (-83.3, "VSS 레일", GREY),
              (-87.6, "핀: SENSE · WD (열마다 metal2)", WHITE)]
    for y, s, c in labels:
        f.text(39.5, y, s, 17, c, "lm")
        f.line(39.5, y, 38, y, c, 1)
    f.text(9, 6.2, "열 0", 16)
    f.text(27, 6.2, "열 1", 16)
    f.save("column.png")


def cell():
    f = Fig(SRAM / "sram8t.gds", (-1.5, -3.5, 19.5, 31), 630, (0, 0, 520, 0))
    f.rect(0, 0, 18, 27.3, YELLOW, 2)
    labels = [(0.0, "VSS 레일 (아래 행과 공유)", GREY),
              (1.8, "WWL 쓰기 워드라인 (poly)", CYAN),
              (5.1, "NMOS: PG_L · PD_L · PD_R · PG_R", CYAN),
              (9.9, "Q · QB 교차 연결", CYAN),
              (14.1, "PMOS: PU_L · PU_R", CYAN),
              (17.0, "VDDA 레일 (셀 전원)", (140, 255, 140)),
              (22.2, "읽기 포트 RD1 (게이트 QB)\n· RD2 (게이트 RWL)", CYAN),
              (25.5, "RWL 읽기 워드라인 (poly)", CYAN),
              (27.3, "VSS 레일 (위 행과 공유)", GREY)]
    for y, s, c in labels:
        f.text(20.2, y, s, 18, c, "lm")
        f.line(20.2, y, 18.2, y, c, 1)
    for x, s in ((0.9, "BL"), (12.0, "RBL"), (15.3, "BLB")):
        f.text(x, 30.2, s, 18, (255, 170, 60))
        f.line(x, 29.4, x, 27.6, (255, 170, 60), 1)
    f.save("cell.png")


def ctrl(gds):
    f = Fig(gds, (-15, -10, 492, 520), 760, (190, 90, 190, 70))
    f.text(-20, 255, "왼쪽\nW 패드 입력 7\n(CLK, WE,\nADDR, DIN3)", 18, CYAN, "rm")
    f.text(497, 255, "오른쪽\n워드라인 30\n(WWL·RWL\n→ SRAM 매크로)", 18, CYAN, "lm")
    f.text(238, 526, "위: N 패드 입력 3 (FI_POS) · 출력 6 (DOUT, SEC, DED)\n"
           "모니터 14 (CAN 8, CSET, CRD_N, RO_EN 3, RO_DIV)", 18, CYAN, "mb")
    f.text(238, -16, "아래: S 패드 입력 5 (FI_MODE, DIN2–0) · PRE_N · WD 8 · SENSE 8", 18, CYAN, "mt")
    f.save("ctrl.png")


def monitor(gds):
    f = Fig(gds, (440, 1060, 1460, 1460), 1600)
    x1, y1, x2, y2 = MON["canary"]
    f.rect(x1, y1, x2, y2, YELLOW, 3)
    f.text((x1 + x2) / 2, y2 + 24, "카나리 래치 8개 (VDDA)\n위 행: 래치 · 아래 행: 읽기 게이트 (VDD)", 18, YELLOW, "mb")
    x1, y1, x2, y2 = MON["robank"]
    f.rect(x1, y1, x2, y2, YELLOW, 3)
    f.text((x1 + x2) / 2, y2 + 10, "RO 뱅크: INV · NAND · NOR 31단 링 (VDD)", 18, YELLOW, "mb")
    x1, y1, x2, y2 = MON["ro_div"]
    f.rect(x1, y1, x2, y2, YELLOW, 3)
    f.text((x1 + x2) / 2, y2 + 10, "분주기 ro_div ÷256\n(qflow)", 18, YELLOW, "mb")
    f.text(455, 1110, "위 채널 13트랙\n제어 블록 핀 ↔ 블록 포트", 16, CYAN, "lm")
    f.text(455, 1145, "VDDA · VSS · VDD 띠", 16, CYAN, "lm")
    f.text(900, 1422, "FI_POS 띠 → N1–N3 패드", 16, CYAN, "lm")
    f.text(1040, 1444, "DED · SEC · DOUT3 → N5–N7 패드", 16, CYAN, "lm")
    f.save("monitor.png")


def main():
    tmp = Path(tempfile.mkdtemp())
    try:
        top = tmp / "ecc_sram_Top.gds"
        top.write_bytes(gzip.decompress((CHIP / "final/ecc_sram_Top.gds.gz").read_bytes()))
        ctl = tmp / "ecc_fi_ctrl.gds"
        ctl.write_bytes(gzip.decompress((REPO / "designs/etri050/ctrl/macro/ecc_fi_ctrl.gds.gz").read_bytes()))
        chip(top)
        core(top)
        monitor(top)
        macro()
        column()
        cell()
        ctrl(ctl)
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
