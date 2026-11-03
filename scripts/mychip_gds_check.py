#!/usr/bin/env python3
"""MyChip (ETRI 0.5 um, 내 칩 제작서비스) 제출 GDS 검사와 제출 zip 만들기.

DRC 덱이 보지 않는 제출 파일 자체를 검사한다. 어떤 칩이든(표준칩 배치 MPW_PAD_28pin, GPIO 사용 여부와
상관없이) 최상위 GDS 하나만 주면 된다. 기준은 2026년 4차 안내 사항과 PDK 260820이다.

  파일       최상위 셀 하나(--top으로 이름 확인), dbu 1 nm, CHIPBOUNDARY(층 0)가 없으면 범위가 스크라이브
             레인 안쪽(60-1840 um) 안, 있으면 상자 하나 0-1900 um = 범위
  스크라이브 레인  칩 1.9 x 1.9 mm에 레인 120 um 포함 -> 변마다 바깥 60 um에 층 0 말고는 도형·글자 없음
             (실링을 레인에 그리면 여기서 걸린다). 예외: PDK MPW_PAD_28pin.gds 원본에 있는 TEXT(48/0)
             칩 외곽 상자(0-1900 um) 하나는 템플릿 그대로이므로 정보로만 적는다. 층 0·48/0 상자는 넣지 않아도
             된다(모아팹 마이칩 QnA #1226 답변, 2026-09-01)
  본딩 패드  PAD(37) 개구가 PDK MPW_PAD_28pin.gds와 같음(28개, XOR 0). 28-pin SOP 패키지는 이 배치만 한다.
             --frame custom이면 비교하지 않는다(그 칩은 bare die만 받는다)
  설계 면적  (정보) GPIO 패드 셀의 안쪽 끝이 둘러싼 상자. 안내: GPIO를 쓰면 약 1.0 x 1.0 mm
  층         모든 층/데이터형이 PDK 층 지도(datatype 0)에 있고, 설계자 층이 아닌 KEY(1)·NODRC(58)·
             DUMMY0-9(100-109)가 없음
  격자       모든 꼭짓점·배치·글자 위치가 0.01 um 격자 위(안내의 최소 grid, Calibre 덱 OFFGRID)
  도형       모든 변이 직교 또는 45도, 경로 폭은 격자 두 칸의 배수이고 끝이 둥글지 않음
  배치       배율 1, 90도 회전만, 배열 간격이 격자 위, 퇴화한 배열(1 x 1, 간격 0) 없음
  GPIO 셀    ETRI GPIO 라이브러리(ETRI_NSPL_GPIO_250610) 이름의 패드 셀이 라이브러리와 층마다 같은지.
             다르면 경고: 킷의 Magic 사본(pads_ETRI/GDS_Magic)으로 만든 링이다. 그 PANA는 ESD 다이오드의
             N-well이 빠져 패드가 기판에 붙는다(아래 기판 검사가 실패로 잡음)
  라벨       최상위 셀의 LVS 라벨 층(41 42 44 46 47) 글자는 ETRI LVS 덱이 넷 이름으로 읽는다:
             경고로 목록만(--strict-labels면 실패)
  우물·기판  게이트(ACT∧POLY1)마다 주입 하나, p형은 N-well 안·n형은 밖. 기판의 p+(N-well 밖 ACT∧PSD)에
             금속으로 이어진 본딩 패드는 PVSS 패드뿐이어야 함(GPIO가 없는 칩은 목록만)

통과하면 --zip으로 제출 파일(<top>.gds 하나를 담은 zip)을 만들고 sha256을 적는다. 실패하면 만들지 않는다.

필요: KLayout 파이썬 모듈 0.28 이상(pip install klayout), ETRI 0.5 um 오픈소스 디자인 킷
(GoodKook/ETRI-0.5um-CMOS-MPW-Std-Cell-DK)의 pads_ETRI/GDS/ETRI_NSPL_GPIO_250610.gds와
pads_ETRI/GDS/MPW_PAD_28pin.gds(모아팹 PDK 260820의 같은 파일).

사용: python3 mychip_gds_check.py <chip.gds> [--top NAME] [--kit DIR] [--frame std|custom]
                                  [--zip OUT.zip] [--report OUT.txt] [--prefix PFX] [--strict-labels]
      종료 코드 0 = 통과(경고는 있을 수 있음), 1 = 실패, 2 = 입력 오류
"""
import argparse
import collections
import hashlib
import os
import sys
import zipfile
from pathlib import Path

try:
    import klayout.db as kdb
except ImportError:                                   # inside klayout -b
    import pya as kdb

LAYERMAP = {0: "CHIPBOUNDARY", 1: "KEY", 2: "NWELL", 3: "PWELL", 4: "HNWELL", 5: "HPWELL", 6: "DWELL",
            7: "DNWELL", 8: "DPWELL", 11: "ACT", 12: "POLY1", 13: "POLY2", 14: "NSD", 15: "PSD", 16: "FVTN",
            17: "FVTP", 18: "VTN", 19: "VTP", 20: "NHRI", 21: "PHRI", 22: "NPI", 23: "PPI", 24: "NDRIFT",
            25: "PDRIFT", 26: "ESDI", 27: "TGOX", 28: "JISO", 29: "TISO", 31: "CONT", 32: "MET1", 33: "VIA1",
            34: "MET2", 35: "VIA2", 36: "MET3", 37: "PAD", 41: "POLY1TXT", 42: "MET1TXT", 44: "MET2TXT",
            46: "MET3TXT", 47: "PADTXT", 48: "TEXT", 51: "RES", 52: "ESD", 53: "CAP", 54: "HVMS", 55: "HVMA",
            56: "BJT", 57: "DIODE", 58: "NODRC", 59: "ESDD", 60: "LVSD"}
LAYERMAP.update({100 + k: f"DUMMY{k}" for k in range(10)})   # PDK NSPL_..._V1p1.layermap, all datatype 0
LABEL_LAYERS = (41, 42, 44, 46, 47)
RESERVED = {1, 58} | set(range(100, 110))
GRID_NM = 10
PAD_LAYER = 37
FRAME_MARK = (48, 0)          # MPW_PAD_28pin.gds 원본: TEXT 층에 칩 외곽 상자 (0,0;1900,1900)
GPIO_PADS = ("PANA", "PIC", "POB4", "POB8", "POB24", "PBCT4", "PBCT8", "PVDD", "PVSS")
GPIO_OTHER = ("PCORNER", "IOFILLER1", "IOFILLER10", "IOFILLER50")
GPIO_IN_KIT = "pads_ETRI/GDS/ETRI_NSPL_GPIO_250610.gds"
PADS_IN_KIT = "pads_ETRI/GDS/MPW_PAD_28pin.gds"


def base(name):
    """Cell name without the '$N' suffix that tools add when merging layouts with the same cell names."""
    return name.split("$")[0]


def find_kit(arg):
    here = Path(__file__).resolve().parent
    for k in (arg, os.environ.get("ETRI050_DK"), Path.home() / "ETRI050_DesignKit",
              Path.cwd() / ".pdk/ETRI050_DesignKit", here.parent / ".pdk/ETRI050_DesignKit"):
        if k and (Path(k) / PADS_IN_KIT).exists():
            return Path(k)
    return None


def rec(cell, li, texts=False):
    it = cell.begin_shapes_rec(li)
    it.shape_flags = kdb.Shapes.STexts if texts else kdb.Shapes.SRegions
    return it


def layer_region(cell, li, skip=None):
    """Shapes of one layer (top coordinates); boxes equal to `skip` (the frame mark) are left out.
    Returns (region, number of skipped boxes)."""
    if skip is None:
        return kdb.Region(rec(cell, li)), 0
    reg, n = kdb.Region(), 0
    it = rec(cell, li)
    while not it.at_end():
        p = it.shape().polygon.transformed(it.trans())
        if p.is_box() and p.bbox() == skip:
            n += 1
        else:
            reg.insert(p)
        it.next()
    return reg, n


def same_cell(la, ca, lb, cb):
    """Same shapes on every layer, hierarchy flattened (XOR empty)."""
    for li in la.layer_indexes():
        lj = lb.find_layer(la.get_info(li))
        ra = kdb.Region(ca.begin_shapes_rec(li))
        rb = kdb.Region(cb.begin_shapes_rec(lj)) if lj is not None else kdb.Region()
        if not (ra ^ rb).is_empty():
            return False
    for lj in lb.layer_indexes():
        if la.find_layer(lb.get_info(lj)) is None and not kdb.Region(cb.begin_shapes_rec(lj)).is_empty():
            return False
    return True


def gpio_boxes(ly, top):
    """{cell name: [DBox in top coordinates]} for every placed GPIO pad/corner/filler cell."""
    names = set(GPIO_PADS + GPIO_OTHER)
    out = collections.defaultdict(list)
    it = kdb.RecursiveInstanceIterator(ly, top)
    while not it.at_end():
        c = it.inst_cell()
        if base(c.name) in names:
            t = it.trans() * it.inst_trans()
            out[base(c.name)].append(c.bbox().transformed(t).to_dtype(ly.dbu))
        it.next()
    return out


class Report:
    def __init__(self):
        self.lines, self.fail, self.warn = [], 0, 0

    def add(self, text, state=None):
        tag = {"ok": " -> ok", "fail": " -> 실패", "warn": " -> 경고", "info": " (정보)", None: ""}[state]
        self.fail += state == "fail"
        self.warn += state == "warn"
        self.lines.append(text + tag)


def check(gds, top_name, gpio, pads, frame, prefix, die_um, lane_um, strict_labels):
    r = Report()
    ly = kdb.Layout()
    ly.read(str(gds))
    tops = ly.top_cells()
    top = tops[0]
    die = kdb.DBox(0, 0, die_um, die_um)
    inner = kdb.DBox(lane_um, lane_um, die_um - lane_um, die_um - lane_um)

    # what the chip draws: every layer but CHIPBOUNDARY (0/0), without the template's 48/0 outline box
    die_i = die.to_itype(ly.dbu)
    regions, content, mark = {}, kdb.Box(), 0
    for li in ly.layer_indexes():
        info = ly.get_info(li)
        if (info.layer, info.datatype) == (0, 0):
            continue
        reg, n = layer_region(top, li, die_i if (info.layer, info.datatype) == FRAME_MARK else None)
        regions[li], mark = reg, mark + n
        content += reg.bbox()
        it = rec(top, li, texts=True)
        while not it.at_end():
            content += it.shape().bbox().transformed(it.trans())
            it.next()
    cbox = content.to_dtype(ly.dbu) if not content.empty() else kdb.DBox()

    # file
    l0 = ly.find_layer(0, 0)
    bnd = kdb.Region(rec(top, l0)).merged() if l0 is not None else kdb.Region()
    if bnd.is_empty():
        form, fits = "CHIPBOUNDARY 없음", cbox.inside(inner)
    else:
        form = f"CHIPBOUNDARY {bnd.count()}개 {bnd.bbox().to_dtype(ly.dbu)}"
        fits = bnd.count() == 1 and bnd.bbox().to_dtype(ly.dbu) == die and top.dbbox() == die
    name_ok = top_name is None or top.name == top_name
    ok = len(tops) == 1 and name_ok and abs(ly.dbu - 0.001) < 1e-12 and fits
    r.add(f"파일: 최상위 셀 {[c.name for c in tops]}" + (f"(기대 {top_name})" if top_name else "")
          + f", dbu {ly.dbu * 1000:g} nm, 범위 {cbox}" + (f"(48/0 외곽 상자 빼고; 전체 {top.dbbox()})" if mark else "")
          + f", {form}", "ok" if ok else "fail")
    if mark:
        r.add(f"TEXT(48/0) 칩 외곽 상자 {mark}개 {die}: PDK MPW_PAD_28pin.gds 원본에 있는 표시라 레인 검사에서 뺌. "
              "넣지 않아도 된다(모아팹 마이칩 QnA #1226)", "info")

    # scribe lane
    keep = kdb.Region(inner.to_itype(ly.dbu))
    lane = []
    for li in ly.layer_indexes():
        info = ly.get_info(li)
        if (info.layer, info.datatype) == (0, 0):
            continue
        reg = regions[li]
        if not reg.is_empty() and not reg.bbox().to_dtype(ly.dbu).inside(inner):
            o = reg - keep
            if not o.is_empty():
                lane.append(f"{LAYERMAP.get(info.layer, info.layer)} {o.count()}개 {o.bbox().to_dtype(ly.dbu)}")
        it, nt = rec(top, li, texts=True), 0
        while not it.at_end():
            t = it.shape().text.transformed(it.trans())
            nt += not inner.contains(kdb.DPoint(t.x * ly.dbu, t.y * ly.dbu))
            it.next()
        if nt:
            lane.append(f"{LAYERMAP.get(info.layer, info.layer)} 글자 {nt}개")
    r.add(f"스크라이브 레인(바깥 {lane_um:g} um): " + ("CHIPBOUNDARY 말고 아무것도 없음" if not lane
          else "들어 있는 것: " + "; ".join(lane)), "fail" if lane else "ok")

    # bond pads
    lp = ly.find_layer(PAD_LAYER, 0)
    mine = kdb.Region(rec(top, lp)).merged() if lp is not None else kdb.Region()
    if frame == "custom":
        r.add(f"본딩 패드: PAD 개구 {mine.count()}개, 표준칩 배치와 비교 안 함(--frame custom: 패키지 없이 bare die만)",
              "info")
    elif pads:
        ref = kdb.Layout()
        ref.read(str(pads))
        rp = ref.find_layer(PAD_LAYER, 0)
        std = kdb.Region(rec(ref.top_cells()[0], rp)).merged() if rp is not None else kdb.Region()
        std.transform(kdb.ICplxTrans(ref.dbu / ly.dbu))
        diff = mine ^ std
        ok = mine.count() == 28 and std.count() == 28 and diff.is_empty()
        r.add(f"본딩 패드: PAD 개구 {mine.count()}개, {Path(pads).name} {std.count()}개, "
              + ("같음(XOR 0)" if diff.is_empty() else f"XOR {diff.count()}개 {diff.bbox().to_dtype(ly.dbu)}"),
              "ok" if ok else "fail")
    else:
        r.add("본딩 패드: MPW_PAD_28pin.gds를 찾지 못해 비교 못 함(--kit 또는 --pads)", "fail")

    # GPIO placements and design area
    boxes = gpio_boxes(ly, top)
    padb = [b for n in GPIO_PADS for b in boxes.get(n, [])]
    if padb:
        ring = kdb.DBox()
        for b in padb:
            ring += b
        tol = 1.0
        edge = kdb.DBox(max((b.right for b in padb if abs(b.left - ring.left) < tol), default=ring.left),
                        max((b.top for b in padb if abs(b.bottom - ring.bottom) < tol), default=ring.bottom),
                        min((b.left for b in padb if abs(b.right - ring.right) < tol), default=ring.right),
                        min((b.bottom for b in padb if abs(b.top - ring.top) < tol), default=ring.top))
        count = ", ".join(f"{n} {len(boxes[n])}" for n in GPIO_PADS + GPIO_OTHER if boxes.get(n))
        r.add(f"GPIO 배치: {count}; 설계 면적(패드 셀 안쪽 끝) {edge} = {edge.width():g} x {edge.height():g} um", "info")
    else:
        r.add("GPIO 배치: ETRI GPIO 패드 셀 없음(맨 패드 칩이면 안내의 설계 면적은 약 1.5 x 1.5 mm)", "info")

    # layers
    used, where, label_shapes = {}, {}, collections.Counter()
    for li in ly.layer_indexes():
        info = ly.get_info(li)
        cells = [c.name for c in ly.each_cell() if not c.shapes(li).is_empty()]
        if cells:
            used[(info.layer, info.datatype)] = len(cells)
            where[(info.layer, info.datatype)] = cells
        if info.layer in LABEL_LAYERS:
            for c in ly.each_cell():
                label_shapes[info.layer] += sum(1 for s in c.shapes(li).each() if not s.is_text())
    foreign = [k for k in used if k[1] != 0 or k[0] not in LAYERMAP]
    reserved = [LAYERMAP[k[0]] for k in used if k[0] in RESERVED and k[1] == 0]
    r.add("층: " + ", ".join(f"{LAYERMAP.get(l, '?')} {l}/{d}" for (l, d) in sorted(used))
          + (" (모두 층 지도 안)" if not foreign else "")
          + (f" -- 설계자 층이 아님: {reserved}" if reserved else ""), "fail" if reserved else "ok")
    if foreign:
        r.add("층 지도에 없는 층: " + "; ".join(f"{l}/{d} (셀 {where[(l, d)][:6]})" for l, d in foreign)
              + " — 의도한 층이 아니면 지우기(선례 pong_pt1은 GPIO 셀 안에 235/0이 있는 채로 제작됨)", "warn")
    if sum(label_shapes.values()):
        r.add("라벨 층의 도형(글자가 아닌 것): " + ", ".join(f"{LAYERMAP[l]} {k}" for l, k in sorted(label_shapes.items()) if k)
              + " — Magic 기본(MOSIS) 층 번호로 쓴 GDS일 수 있음: cif ostyle lambda=0.30(ETRI)로 다시 쓰기", "fail")

    # grid, shapes, placements, arrays
    grid, tgrid, angle, paths, npath = collections.Counter(), collections.Counter(), collections.Counter(), [], 0
    trans, pitch, degenerate, narray = [], [], [], 0
    for c in ly.each_cell():
        for li in ly.layer_indexes():
            lnum = ly.get_info(li).layer
            for s in c.shapes(li).each():
                if s.is_text():
                    d = s.text.trans.disp
                    if d.x % GRID_NM or d.y % GRID_NM:
                        tgrid[(c.name, lnum)] += 1
                    continue
                if s.is_box():
                    pts = [s.box.p1, s.box.p2]
                elif s.is_path():
                    npath += 1
                    pa = s.path
                    pts = list(pa.each_point())
                    if pa.width % (2 * GRID_NM) or pa.bgn_ext % GRID_NM or pa.end_ext % GRID_NM or pa.round:
                        paths.append(f"{c.name} 층 {lnum}")
                else:
                    poly = s.polygon
                    pts = list(poly.each_point_hull()) + [p for h in range(poly.holes()) for p in poly.each_point_hole(h)]
                k = sum(1 for p in pts if p.x % GRID_NM or p.y % GRID_NM)
                if k:
                    grid[(c.name, lnum)] += k
                if not s.is_box():
                    for e in s.polygon.each_edge():
                        if e.dx() and e.dy() and abs(e.dx()) != abs(e.dy()):
                            angle[(c.name, lnum)] += 1
        for i in c.each_inst():
            t = i.cplx_trans
            if t.disp.x % GRID_NM or t.disp.y % GRID_NM:
                grid[(c.name, "배치")] += 1
            if abs(t.mag - 1) > 1e-12 or not t.is_ortho():
                trans.append(f"{c.name}/{i.cell.name}")
            if i.is_regular_array():
                narray += 1
                if any(v % GRID_NM for v in (i.a.x, i.a.y, i.b.x, i.b.y)):
                    pitch.append(f"{c.name}/{i.cell.name}")
                if i.na * i.nb <= 1 or (i.na > 1 and i.a == kdb.Vector()) or (i.nb > 1 and i.b == kdb.Vector()):
                    degenerate.append(f"{c.name}/{i.cell.name}")
    r.add("격자 0.01 um: " + ("모든 꼭짓점·배치가 격자 위" if not grid else "벗어남: " + ", ".join(
          f"{c} 층 {l}: {k}" for (c, l), k in sorted(grid.items(), key=str)[:20]))
          + "; 글자 위치 " + ("모두 격자 위" if not tgrid else "벗어남: " + ", ".join(
          f"{c} 층 {l}: {k}" for (c, l), k in sorted(tgrid.items(), key=str)[:20])),
          "fail" if grid or tgrid else "ok")
    r.add("도형: " + ("모든 변이 직교·45도" if not angle else "다른 각도: " + ", ".join(
          f"{c} 층 {l}: {k}" for (c, l), k in sorted(angle.items(), key=str)[:20]))
          + f"; 경로 {npath}개" + (f", 격자 밖 폭·둥근 끝: {paths[:10]}" if paths else ""),
          "fail" if angle or paths else "ok")
    r.add("배치: " + ("배율 1, 90도 회전만" if not trans else f"그 밖의 변환: {trans[:10]}")
          + f"; 배열 {narray}개" + (f", 간격이 격자 밖: {pitch[:10]}" if pitch else ""),
          "fail" if trans or pitch else "ok")
    if degenerate:
        r.add(f"퇴화한 배열(1 x 1 또는 간격 0) {len(degenerate)}개: {degenerate[:6]} — ETRI GPIO GDS 원본에도 있음"
              "(선례 pong_pt1은 그대로 제작). 읽기를 거부하는 도구가 있어 한 번 놓기(SREF)로 바꾸기 권장", "warn")

    # GPIO cells against the library
    lib = kdb.Layout()
    gpio_used = [c.name for c in ly.each_cell() if base(c.name) in GPIO_PADS + GPIO_OTHER]
    inside = set()
    for n in gpio_used:
        inside |= set(ly.cell(n).called_cells())
    differ = []
    if gpio and gpio_used:
        lib.read(str(gpio))
        differ = [n for n in gpio_used
                  if lib.has_cell(base(n)) and not same_cell(ly, ly.cell(n), lib, lib.cell(base(n)))]
    ours = [c.name for c in ly.each_cell() if c.name not in gpio_used and c.cell_index() not in inside]
    if not gpio_used:
        r.add(f"셀: GPIO 셀 없음; 설계 셀 {len(ours)}개", "info")
    elif not gpio:
        r.add("셀: GPIO 라이브러리 GDS를 찾지 못해 비교 못 함(--kit 또는 --gpio)", "warn")
    else:
        r.add(f"셀: GPIO {len(gpio_used)}종({', '.join(gpio_used)})"
              + (f" 중 라이브러리(250610)와 다른 것 {differ}: 킷 Magic 사본이나 다른 버전으로 만든 링 "
                 "(ETRI 원본 250610으로 바꾸기 권장, PANA면 아래 기판 검사 확인)" if differ else " 모두 라이브러리 원본과 같음"),
              "warn" if differ else "ok")
    if prefix:
        no_pfx = [n for n in ours if not n.startswith(prefix)]
        r.add(f"설계 셀 {len(ours)}개 중 접두어 '{prefix}' 없는 것 {len(no_pfx)}개: {sorted(no_pfx)[:30]}", "info")

    # labels in the top cell
    labels, other_txt = [], collections.Counter()
    for li in ly.layer_indexes():
        lnum = ly.get_info(li).layer
        for s in top.shapes(li).each():
            if s.is_text():
                if lnum in LABEL_LAYERS:
                    labels.append(f"{s.text.string}@{LAYERMAP[lnum]}")
                else:
                    other_txt[lnum] += 1
    r.add(f"라벨: 최상위 셀의 LVS 라벨 층 글자 {len(labels)}개" + (f" ({', '.join(labels[:30])})" if labels else "")
          + "; 다른 층 " + (", ".join(f"{LAYERMAP.get(l, l)} {k}" for l, k in sorted(other_txt.items())) or "없음"),
          ("fail" if strict_labels else "warn") if labels else "ok")

    # wells and substrate (flat copy)
    wells(gds, boxes, r)
    r.add("제출 GDS 검사: " + ("통과" if not r.fail else "실패") + f" (실패 {r.fail}, 경고 {r.warn})")
    return r, top.name


def wells(gds, boxes, r):
    ly = kdb.Layout()
    ly.read(str(gds))
    top = ly.top_cells()[0]
    ly.flatten(top.cell_index(), -1, True)
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
    lay = {}
    for name, n in (("nwell", 2), ("act", 11), ("poly1", 12), ("nsd", 14), ("psd", 15), ("cont", 31),
                    ("m1", 32), ("v1", 33), ("m2", 34), ("v2", 35), ("m3", 36)):
        li = ly.find_layer(n, 0)
        lay[name] = l2n.make_layer(li if li is not None else ly.layer(n, 0), name)
    gate = lay["act"] & lay["poly1"]
    bad = {"N-well 밖 p형": (gate & lay["psd"]) - lay["nwell"], "N-well 안 n형": (gate & lay["nsd"]) & lay["nwell"],
           "주입 없음": (gate - lay["nsd"]) - lay["psd"], "주입 둘": gate & lay["nsd"] & lay["psd"]}
    ptap = ((lay["act"] & lay["psd"]) - lay["nwell"]) - lay["poly1"]
    l2n.register(ptap, "ptap")
    chain = (ptap, lay["cont"], lay["m1"], lay["v1"], lay["m2"], lay["v2"], lay["m3"])
    for x in chain:
        l2n.connect(x)
    for a, b in zip(chain, chain[1:]):
        l2n.connect(a, b)
    l2n.extract_netlist()
    pli = ly.find_layer(PAD_LAYER, 0)
    pads = kdb.Region(top.begin_shapes_rec(pli)) if pli is not None else kdb.Region()
    vss = [b.to_itype(ly.dbu) for b in boxes.get("PVSS", [])]
    circuit = next(l2n.netlist().each_circuit_top_down())
    tied, ground, sub_nets = [], 0, 0
    for n in circuit.each_net():
        if l2n.shapes_of_net(n, ptap, True).is_empty():
            continue
        sub_nets += 1
        on_pad = (l2n.shapes_of_net(n, lay["m3"], True) & pads).merged()
        for p in on_pad.each():
            if any(b.contains(p.bbox().center()) for b in vss):
                ground += 1
            else:
                tied.append(p.bbox().to_dtype(ly.dbu))
    nbad = sum(x.count() for x in bad.values())
    r.add(f"우물: 게이트 {gate.count()}개, " + ", ".join(f"{k} {x.count()}" for k, x in bad.items()),
          "fail" if nbad else "ok")
    if vss:
        r.add(f"기판: p+ 기판 접촉을 가진 넷 {sub_nets}개, 기판에 붙은 본딩 패드 PVSS {ground}개 · 그 밖 {len(tied)}개"
              + (f" {[str(b) for b in tied[:8]]}" if tied else ""), "fail" if tied else "ok")
    else:
        r.add(f"기판: p+ 기판 접촉을 가진 넷 {sub_nets}개, 기판에 붙은 본딩 패드 {len(tied)}개"
              + (f" {[str(b) for b in tied[:8]]}" if tied else "") + " — PVSS 셀이 없어 접지 패드인지 직접 확인",
              "warn" if tied else "ok")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("gds", type=Path)
    ap.add_argument("--top", help="기대하는 최상위 셀 이름(신청서의 Top Cell Name)")
    ap.add_argument("--kit", help="ETRI 0.5 um 오픈소스 디자인 킷 폴더(기본: $ETRI050_DK, ~/ETRI050_DesignKit)")
    ap.add_argument("--gpio", type=Path, help="ETRI_NSPL_GPIO_250610.gds (기본: 킷 안)")
    ap.add_argument("--pads", type=Path, help="MPW_PAD_28pin.gds (기본: 킷 안)")
    ap.add_argument("--frame", choices=("std", "custom"), default="std",
                    help="std = 표준칩 배치 MPW_PAD_28pin(패키지 가능), custom = 자유 배치(bare die만)")
    ap.add_argument("--die", type=float, default=1900.0, help="칩 한 변(um, 기본 1900)")
    ap.add_argument("--lane", type=float, default=60.0, help="변마다 스크라이브 레인 폭(um, 기본 60 = 120/2)")
    ap.add_argument("--prefix", help="설계 셀 이름 접두어(목록만, 예: mychip_)")
    ap.add_argument("--strict-labels", action="store_true", help="최상위 LVS 라벨을 실패로")
    ap.add_argument("--zip", type=Path, help="통과하면 이 이름으로 제출 zip(<top>.gds 하나)을 만듦")
    ap.add_argument("--report", type=Path, help="결과를 이 파일에도 씀")
    a = ap.parse_args(argv)
    if not a.gds.exists():
        print(f"GDS 없음: {a.gds}")
        return 2
    kit = find_kit(a.kit)
    gpio = a.gpio or (kit / GPIO_IN_KIT if kit else None)
    pads = a.pads or (kit / PADS_IN_KIT if kit else None)
    r, top = check(a.gds, a.top, gpio, pads, a.frame, a.prefix, a.die, a.lane, a.strict_labels)
    sha = hashlib.sha256(a.gds.read_bytes()).hexdigest()
    r.add(f"GDS: {a.gds} {a.gds.stat().st_size:,} B, sha256 {sha}")
    if a.zip:
        if r.fail:
            r.add(f"제출 zip: 만들지 않음(실패 {r.fail})")
        elif a.gds.read_bytes()[:2] == b"\x1f\x8b":
            r.add("제출 zip: 만들지 않음(입력이 gzip으로 압축된 GDS — 풀어서 .gds로 다시 실행)", "fail")
        else:
            a.zip.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(a.zip, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(a.gds, f"{top}.gds")
            with zipfile.ZipFile(a.zip) as z:
                bad = z.testzip()
            zsha = hashlib.sha256(a.zip.read_bytes()).hexdigest()
            r.add(f"제출 zip: {a.zip} {a.zip.stat().st_size:,} B (안에 {top}.gds, CRC {'정상' if bad is None else bad}), "
                  f"sha256 {zsha} — 신청서 Top Cell Name: {top}")
    text = "\n".join(r.lines)
    print(text)
    if a.report:
        a.report.write_text(text + "\n", encoding="utf-8")
    return 1 if r.fail else 0


if __name__ == "__main__":
    sys.exit(main())
