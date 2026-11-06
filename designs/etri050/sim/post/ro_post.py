#!/usr/bin/env python3
"""Post-layout check of the ring-oscillator monitor: the drawn RO bank (gen/robank.py, robank_flat.gds) and the
frozen divider (ctrl/macro/ro_div.gds.gz), both extracted by Magic with capacitance (x CAP_SCALE, as
array_post.py: Magic's coefficients in this kit are AMI 0.5 um ones), official PDK models (nmos4 / pmos4).
The ring's tap drives the divider's TAP input as on the chip (plus 15 fF for the channel wiring), DIV drives
100 fF (the channel to the control block). One ring at a time: its enable goes to 5 V at 20 ns, the other two
stay at 0 (their rings stand still, taps at 1).

  frequency   every ring at 5 corners (27 C) and TT at 125 C: ring frequency from the tap (rise 6 to 16), VDD
              current while it runs
  divider     the fastest ring (FF, INV: the divider's hardest input) and TT INV for 300 ring periods: DIV, held
              at 1 until the enable, must fall after 128 periods and rise 128 periods later (a period of 256)

  python3 designs/etri050/sim/post/ro_post.py            both
  python3 designs/etri050/sim/post/ro_post.py --quick    frequency at TT 27 C only
Results: designs/etri050/sim/post/build/ro_post.json
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import klayout.db as kdb

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
D = REPO / "designs/etri050"
BUILD = HERE / "build" / "ro"
MODELS = D / "sim/models"
CAP_SCALE = float(os.environ.get("CAP_SCALE", "1.5"))
VDD = 5.0
RINGS = {0: "inv", 1: "nand", 2: "nor"}
CORNERS = [("TT", 27), ("SS", 27), ("FF", 27), ("SF", 27), ("FS", 27), ("TT", 125)]
DIV_RUNS = [("FF", 27, 0), ("TT", 27, 0)]


def magicrc():
    dk = os.environ.get("ETRI050_DK", str(REPO / ".pdk/ETRI050_DesignKit"))
    return os.path.join(dk, "tech/etri050.magicrc")


def labelled(src: Path, out: Path, pins):
    """Copy of a flat GDS with only the block's port labels: pins = [(name, layer (gds, dt), x, y)]."""
    ly = kdb.Layout()
    ly.read(str(src))
    top = ly.top_cell()
    for li in ly.layer_indexes():
        for s in [s for s in top.shapes(li).each() if s.is_text()]:
            top.shapes(li).erase(s)
    for name, (l, d), x, y in pins:
        top.shapes(ly.layer(l, d)).insert(kdb.Text(name, kdb.Trans(kdb.Vector(round(x / ly.dbu), round(y / ly.dbu)))))
    ly.write(str(out))
    return top.name


def extract(gds: Path, cell: str) -> tuple[Path, list[str]]:
    script = f"""cif istyle lambda=0.30(ETRI)
gds read {gds.name}
load {cell}
select top cell
port makeall
extract do capacitance
extract do coupling
extract all
ext2spice cthresh 0
ext2spice format ngspice
ext2spice scale off
ext2spice subcircuit top on
ext2spice -o {cell}_pex.spice
quit -noprompt
"""
    p = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", magicrc()], input=script, text=True,
                       cwd=BUILD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (BUILD / f"{cell}_ext.log").write_text(p.stdout)
    raw = (BUILD / f"{cell}_pex.spice").read_text()
    lines = []
    for line in raw.splitlines():
        if line.startswith("+") and lines:
            lines[-1] += " " + line[1:].strip()
        else:
            lines.append(line)
    out, ports = [], []
    for line in lines:
        if line.lower().startswith(".subckt"):
            ports = line.split()[2:]
        m = re.match(r"^(C\d+)\s+(\S+)\s+(\S+)\s+([\d.eE+-]+)fF\s*$", line)
        if m:
            line = f"{m[1]} {m[2]} {m[3]} {float(m[4]) * CAP_SCALE:.4g}f"
        out.append(re.sub(r"\bnfet\b", "nmos4", re.sub(r"\bpfet\b", "pmos4", line)))
    net = BUILD / f"{cell}_pex_x{CAP_SCALE:g}.spice"
    net.write_text("\n".join(out) + "\n")
    return net, ports


def prepare():
    """Labelled flat GDS of both blocks, extracted netlists: {block: (netlist, ports, subckt name)}."""
    BUILD.mkdir(parents=True, exist_ok=True)
    for lib in ("05cmos_mosfet_corner.lib",):
        shutil.copy(MODELS / lib, BUILD / lib)
    rp = json.loads((D / "monitor/build/robank_pins.json").read_text())["pins"]
    lay = {"metal1": (32, 0), "metal2": (34, 0)}
    pins = [(n, lay[v["layer"]], (v["box"][0] + v["box"][2]) / 2, (v["box"][1] + v["box"][3]) / 2) for n, v in rp.items()]
    rb = labelled(D / "monitor/build/robank_flat.gds", BUILD / "robank_lab.gds", pins)
    src = BUILD / "ro_div_frozen.gds"
    with gzip.open(D / "ctrl/macro/ro_div.gds.gz") as f, open(src, "wb") as o:
        shutil.copyfileobj(f, o)
    pins = []
    for line in (D / "ctrl/macro/ro_div_pins.txt").read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        name, layer, *v = line.split()
        x1, y1, x2, y2 = (float(t) for t in v)
        name = name.replace("[", "").replace("]", "")
        if name in ("vdd", "gnd"):                  # spine: label 10 um above its bottom end
            pins.append((name, lay[layer], (x1 + x2) / 2, y1 + 10.0))
        else:
            pins.append((name, lay[layer], (x1 + x2) / 2, (y1 + y2) / 2))
    dv = labelled(src, BUILD / "ro_div_lab.gds", pins)
    out = {}
    for key, gds, cell in (("robank", BUILD / "robank_lab.gds", rb), ("ro_div", BUILD / "ro_div_lab.gds", dv)):
        net, ports = extract(gds, cell)
        out[key] = (str(net), ports, cell)
    return out


def deck(ex, corner, temp, k, tstop, divider):
    rb_net, rb_ports, rb_cell = ex["robank"]
    dv_net, dv_ports, dv_cell = ex["ro_div"]
    rbmap = {f"en{i}": f"en{i}" for i in range(3)} | {f"in{i}": f"tap{i}" for i in range(3)} | {"VDD": "vdd", "VSS": "0"}
    dvmap = {f"EN{i}": f"en{i}" for i in range(3)} | {f"TAP{i}": f"tap{i}" for i in range(3)} | \
            {"DIV": "div", "vdd": "vdd", "gnd": "0"}
    for p in rb_ports:
        if p not in rbmap:
            raise SystemExit(f"robank port {p} not expected")
    for p in dv_ports:
        if p not in dvmap:
            raise SystemExit(f"ro_div port {p} not expected")
    L = [f"* RO bank + divider, post-layout, ring {k} ({RINGS[k]}) {corner} {temp}C",
         f".lib '05cmos_mosfet_corner.lib' {corner}",
         f".include '{rb_net}'", f".include '{dv_net}'",
         ".options gmin=1e-15 reltol=1e-3 abstol=1e-12 method=gear",
         f".temp {temp}",
         f"VVDD vdd 0 {VDD}"]
    for i in range(3):
        L.append(f"Ven{i} en{i} 0 PWL(0 0 20n 0 20.5n {VDD})" if i == k else f"Ven{i} en{i} 0 0")
        L.append(f"Ctap{i} tap{i} 0 15f")
    L += ["Cdiv div 0 100f",
          "Xrb " + " ".join(rbmap[p] for p in rb_ports) + f" {rb_cell}",
          "Xdv " + " ".join(dvmap[p] for p in dv_ports) + f" {dv_cell}",
          ".control", "set noaskquit",
          f"tran 0.02n {tstop:.4e} 0 0.05n",
          f"meas tran t1 when v(tap{k})={VDD / 2} rise=6",
          f"meas tran t2 when v(tap{k})={VDD / 2} rise=16",
          "let f = 10 / (t2 - t1)",
          "meas tran iavg avg i(vvdd) from=t1 to=t2",
          f"let p = -iavg * {VDD}",
          'echo "RES f=$&f p=$&p"']
    if divider:
        L += [f"meas tran tf when v(div)={VDD / 2} fall=1",
              f"meas tran tr when v(div)={VDD / 2} rise=1",
              f"meas tran ten when v(tap{k})={VDD / 2} fall=1",
              "let nf = (tf - ten) * f", "let nh = (tr - tf) * f",
              'echo "RES tf=$&tf tr=$&tr nf=$&nf nh=$&nh"']
    L += ["quit", ".endc", ".end"]
    return "\n".join(L) + "\n"


def run(args):
    ex, corner, temp, k, divider, f_guess = args
    tag = f"ro{k}_{corner}_{temp}{'_div' if divider else ''}"
    periods = 300 if divider else 20
    tstop = 30e-9 + periods / f_guess * 1.2
    cir = BUILD / f"{tag}.cir"
    cir.write_text(deck(ex, corner, temp, k, tstop, divider))
    p = subprocess.run(["ngspice", "-b", cir.name], cwd=BUILD, capture_output=True, text=True, timeout=14400)
    (BUILD / f"{tag}.log").write_text(p.stdout + p.stderr)
    res = {}
    for line in p.stdout.splitlines():
        if line.startswith("RES "):
            for kv in line[4:].split():
                key, val = kv.split("=")
                try:
                    res[key] = float(val)
                except ValueError:
                    res[key] = None
    return dict(ring=RINGS[k], corner=corner, temp=temp, divider=divider, **res)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    ex = prepare()
    guess = {0: 100e6, 1: 85e6, 2: 60e6}
    jobs = [] if args.quick else [(ex, c, t, k, True, guess[k] * (1.1 if c == "FF" else 0.8)) for c, t, k in DIV_RUNS]
    jobs += [(ex, c, t, k, False, guess[k] * 0.6) for c, t in (CORNERS[:1] if args.quick else CORNERS) for k in RINGS]
    with ProcessPoolExecutor(max_workers=int(os.environ.get("JOBS", "2"))) as pool:
        res = list(pool.map(run, jobs))
    ok = True
    print(f"{'ring':5} {'corner':7} {'f (MHz)':>8} {'P (mW)':>7}  divider")
    for r in res:
        f = r.get("f")
        line = f"{r['ring']:5} {r['corner']} {r['temp']:>3}C {f / 1e6 if f else float('nan'):8.2f} {r.get('p', 0) * 1e3:7.2f}"
        if r["divider"]:
            nf, nh = r.get("nf"), r.get("nh")
            good = nf is not None and nh is not None and abs(nf - 128) < 1.5 and abs(nh - 128) < 1.5
            ok &= good
            line += f"  DIV falls after {nf:.1f} periods, rises {nh:.1f} later: {'PASS' if good else 'FAIL'}" if nf and nh else "  DIV: no edges FAIL"
        ok &= f is not None
        print(line)
    (HERE / "build").mkdir(exist_ok=True)
    (HERE / "build/ro_post.json").write_text(json.dumps(dict(cap_scale=CAP_SCALE, runs=res), indent=1))
    print(f"ro_post: {'PASS' if ok else 'FAIL'} (build/ro_post.json)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
