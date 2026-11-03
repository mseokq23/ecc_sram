#!/usr/bin/env python3
"""mychip_gds_check.py 자체 시험: 통과하는 GDS 하나에 일부러 오류를 넣어 검사기가 잡는지 확인한다.

쓰는 법(기준 GDS는 제작된 선례 칩이 좋다 — 킷 sparse-checkout으로 받음):
  git -C .pdk/ETRI050_DesignKit sparse-checkout add Projects/RTL/pong_pt1
  python3 scripts/mychip_gds_check_selftest.py \\
      .pdk/ETRI050_DesignKit/Projects/RTL/pong_pt1/ETRI050_MyChip_MPW/pong_pt1_MPW2025_STD-II/chip_top/pong_pt1_Top.gds.gz \\
      --top pong_pt1_Top
  (자기 칩: python3 scripts/mychip_gds_check_selftest.py build/<Top>.gds --top <Top>)

기준 GDS는 표준칩 배치(MPW_PAD_28pin)여야 하고 그대로 통과해야 한다. 오류는 칩 가운데(--at)와 서쪽
스크라이브 레인에 넣는다. 종료 코드 0 = 모든 경우가 기대대로.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import klayout.db as kdb
except ImportError:
    import pya as kdb

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("gds", type=Path, help="그대로 통과하는 GDS(.gds 또는 .gds.gz)")
    ap.add_argument("--top", required=True, help="최상위 셀 이름")
    ap.add_argument("--kit", help="ETRI 0.5 um 오픈소스 디자인 킷 폴더(검사기에 그대로 넘김)")
    ap.add_argument("--checker", type=Path, default=HERE / "mychip_gds_check.py")
    ap.add_argument("--at", type=float, default=950.0, help="칩 안 오류 자리(um, x = y, 기본 950)")
    a = ap.parse_args()
    c = a.at

    def box(l, d, x1, y1, x2, y2):
        return lambda ly, t: t.shapes(ly.layer(l, d)).insert(kdb.DBox(x1, y1, x2, y2).to_itype(ly.dbu))

    def text(l, d, s):
        return lambda ly, t: t.shapes(ly.layer(l, d)).insert(
            kdb.Text(s, kdb.Trans(kdb.Vector(int(round(c / ly.dbu)), int(round(c / ly.dbu))))))

    def tri(l, d):
        pts = [(c, c), (c + 10, c), (c, c + 5.77)]               # 30도 변
        return lambda ly, t: t.shapes(ly.layer(l, d)).insert(
            kdb.DPolygon([kdb.DPoint(*p) for p in pts]).to_itype(ly.dbu))

    # (이름, 넣을 오류, 기대 종료 코드, 리포트에 있어야 할 말)
    cases = [
        ("기준 그대로", None, 0, "통과"),
        ("레인에 금속1", box(32, 0, 20, c, 40, c + 20), 1, "스크라이브 레인"),
        ("꼭짓점 5 nm 벗어남", box(32, 0, c + 0.005, c, c + 1, c + 1), 1, "격자"),
        ("라벨 층(MET1TXT)에 도형", box(42, 0, c, c, c + 1, c + 1), 1, "라벨 층의 도형"),
        ("NODRC 층", box(58, 0, c, c, c + 1, c + 1), 1, "설계자 층이 아님"),
        ("30도 변", tri(32, 0), 1, "다른 각도"),
        ("본딩 패드 개구 하나 더", box(37, 0, c, c, c + 60, c + 60), 1, "본딩 패드"),
        ("최상위 라벨(경고만)", text(46, 0, "VDD"), 0, "라벨: 최상위"),
        ("CHIPBOUNDARY 0/0 상자(허용)", box(0, 0, 0, 0, 1900, 1900), 0, "CHIPBOUNDARY 1개"),
        ("48/0 칩 외곽 상자(템플릿과 같음, 허용)", box(48, 0, 0, 0, 1900, 1900), 0, "칩 외곽 상자 1개"),
        ("48/0 작은 상자가 레인에", box(48, 0, 10, 10, 50, 50), 1, "스크라이브 레인"),
    ]
    extra = ["--kit", a.kit] if a.kit else []
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, fn, want, key) in enumerate(cases):
            g = a.gds
            if fn is not None:
                ly = kdb.Layout()
                ly.read(str(a.gds))
                fn(ly, ly.top_cells()[0])
                g = Path(tmp) / f"case{i}.gds"
                ly.write(str(g))
            r = subprocess.run([sys.executable, str(a.checker), str(g), "--top", a.top] + extra,
                               capture_output=True, text=True)
            ok = r.returncode == want and key in r.stdout
            bad += not ok
            summary = next((l for l in r.stdout.splitlines() if l.startswith("제출 GDS 검사")), r.stdout[-200:])
            print(f"{'맞음' if ok else '틀림'}  {name}: 종료 {r.returncode}(기대 {want}) | {summary}")
            if not ok:
                print(r.stdout[-2000:], r.stderr[-1000:])
    print(f"자체 시험: {len(cases)}가지 중 {len(cases) - bad}가지 기대대로")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
