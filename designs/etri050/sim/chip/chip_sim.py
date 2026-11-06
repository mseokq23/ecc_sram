#!/usr/bin/env python3
"""Transistor-level simulation of the whole chip core as drawn: the control block, the SRAM macro, the
decoupling and the reliability monitor (canary latches, RO bank, divider), extracted together from
build/lvs/ecc_sram_core_lvs.gds (chip/core_lvs.py) with Magic, devices and parasitic capacitance
(x CAP_SCALE), official PDK models. Inputs are driven at the core side of the pads.

  python3 designs/etri050/sim/chip/chip_sim.py [--corner TT --temp 27 --vdd 5 --vdda 5 --vddw 5]
  python3 designs/etri050/sim/chip/chip_sim.py --no-extract --corner SS --temp 125 --vdd 4.5 --vdda 4.5 --vddw 4.5
      (the second form reuses the last extraction, so several corners can run side by side)

The sequence writes array words, the standard-cell reference word (address 15) and words with stored
faults, then reads them back in every read mode; each read is compared with a model of the ECC
(Hamming(8,4) SEC-DED, fault masks k, k^1, k^2). Then the monitor views (FI_MODE = 11, read): the canary
view before any set (power-up state, shown, not compared), the canary set (CSET pulse while CLK = 1) on both
halves, the canary view (all eight kept: 0000), the ring-oscillator view for each ring and for none (DOUT =
0001: DIV stays 1 for the first 128 ring periods), and a normal read after them. SEC / DED come from the
addressed word in every view. CLK period 200 ns: inputs change 5 ns after CLK falls, CLK = 1 for the second
half, outputs are sampled 5 ns before CLK falls. With VDDA below VDD the canary views are shown, not compared:
the read-out gates are specified at VDDA = VDD only.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BUILD = HERE / "build"
MODELS = REPO / "designs/etri050/sim/models"
LVS_GDS = REPO / "designs/etri050/chip/build/lvs/ecc_sram_core_lvs.gds"
KIT = Path(os.environ.get("ETRI050_DK", REPO / ".pdk/ETRI050_DesignKit"))
CAP_SCALE = float(os.environ.get("CAP_SCALE", "1.5"))
T = 200e-9

INPUTS = ["CLK", "WE"] + [f"ADDR{i}" for i in range(4)] + [f"DIN{i}" for i in range(4)] + \
         [f"FI_MODE{i}" for i in range(2)] + [f"FI_POS{i}" for i in range(3)]
OUTPUTS = [f"DOUT{i}" for i in range(4)] + ["SEC", "DED"]


# ------------------------------------------------------------------ ECC model (same as the RTL)
def encode(d):
    b = [(d >> i) & 1 for i in range(4)]
    p0, p1, p2 = b[0] ^ b[1] ^ b[3], b[0] ^ b[2] ^ b[3], b[1] ^ b[2] ^ b[3]
    pa = b[0] ^ b[1] ^ b[2]
    bits = [pa, p0, p1, b[0], p2, b[1], b[2], b[3]]          # C0..C7
    return sum(v << i for i, v in enumerate(bits))


def mask(mode, k, write):
    h1 = 1 << k
    h2 = h1 | 1 << (k ^ 1)
    h3 = h2 | 1 << (k ^ 2)
    return {1: h1, 2: h2, 3: h3 if write else 0}.get(mode, 0)


def read_model(stored, mode, k, can=None):
    """(DOUT, SEC, DED) of a read; in the monitor views (mode 3, FI_POS[2:1] != 00) DOUT is the canary half
    (can: CAN[7:0], None when not known: not compared) or {000, DIV} with DIV = 1."""
    r = stored ^ mask(mode, k, False)
    bit = lambda i: (r >> i) & 1
    s = 0
    for i in range(1, 8):
        if bit(i):
            s ^= i
    q = bin(r).count("1") & 1
    c = r ^ (1 << s) if q else r
    view = k >> 1 if mode == 3 else 0
    if mode == 3 and view in (1, 2):
        return (None if can is None else (can >> 4 if k & 1 else can) & 0xF), q, int(s != 0 and not q)
    if mode == 3 and view == 3:
        return 0x1, q, int(s != 0 and not q)
    if mode == 3:
        dout = [bit(3), bit(5), bit(6), bit(7)] if k & 1 else [bit(0), bit(1), bit(2), bit(4)]
    else:
        dout = [(c >> 3) & 1, (c >> 5) & 1, (c >> 6) & 1, (c >> 7) & 1]
    return sum(v << i for i, v in enumerate(dout)), q, int(s != 0 and not q)


SEQ = [  # (op, addr, data, fi_mode, fi_pos)
    ("W", 0, 0xA, 0, 0), ("W", 5, 0x3, 0, 0), ("W", 14, 0x9, 0, 0), ("W", 15, 0x6, 0, 0),
    ("W", 9, 0xC, 1, 3), ("W", 12, 0x5, 2, 6), ("W", 7, 0xF, 3, 2),
    ("R", 0, 0, 0, 0), ("R", 5, 0, 0, 0), ("R", 14, 0, 0, 0), ("R", 15, 0, 0, 0),
    ("R", 9, 0, 0, 0), ("R", 9, 0, 3, 1), ("R", 9, 0, 3, 0), ("R", 12, 0, 0, 0), ("R", 7, 0, 0, 0),
    ("R", 0, 0, 1, 5), ("R", 0, 0, 2, 4), ("R", 15, 0, 2, 1), ("W", 0, 0x5, 0, 0), ("R", 0, 0, 0, 0),
    # monitor views (FI_MODE 11): canary view before a set, set (both halves), view; RO view per ring, none
    ("R", 5, 0, 3, 2), ("R", 5, 0, 3, 3), ("R", 5, 0, 3, 4), ("R", 5, 0, 3, 5), ("R", 5, 0, 3, 2), ("R", 5, 0, 3, 3),
    ("R", 5, 0x0, 3, 6), ("R", 5, 0x1, 3, 7), ("R", 5, 0x2, 3, 6), ("R", 5, 0x3, 3, 7), ("R", 5, 0, 0, 0),
]


def extract():
    BUILD.mkdir(parents=True, exist_ok=True)
    if not LVS_GDS.exists():
        sys.exit(f"{LVS_GDS} not found: run python3 designs/etri050/chip/core_lvs.py")
    script = f"""cif istyle lambda=0.30(ETRI)
gds read {LVS_GDS}
load ecc_sram_core
select top cell
port makeall
extract do capacitance
extract do local
extract all
ext2spice cthresh 0.1
ext2spice format ngspice
ext2spice scale off
ext2spice subcircuit top on
ext2spice -o core_pex.spice
quit -noprompt
"""
    subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", str(KIT / "tech/etri050.magicrc")], input=script,
                   text=True, cwd=BUILD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines, ports = [], []
    for line in (BUILD / "core_pex.spice").read_text().splitlines():
        if line.startswith("+") and lines:
            lines[-1] += " " + line[1:].strip()
        else:
            lines.append(line)
    out = []
    for line in lines:
        if line.lower().startswith(".option scale"):
            raise SystemExit("extraction still scaled: expected 'ext2spice scale off'")
        if line.lower().startswith(".subckt"):
            ports = line.split()[2:]
        m = re.match(r"^(C\d+)\s+(\S+)\s+(\S+)\s+([\d.eE+-]+)fF\s*$", line)
        if m:
            line = f"{m[1]} {m[2]} {m[3]} {float(m[4]) * CAP_SCALE:.4g}f"
        out.append(re.sub(r"\bnfet\b", "nmos4", re.sub(r"\bpfet\b", "pmos4", line)))
    net = BUILD / f"core_pex_x{CAP_SCALE:g}.spice"
    net.write_text("\n".join(out) + "\n")
    return net, ports


def pwl(name, points, vhi, edge=1e-9):
    pts, last = [], None
    for t, v in points:
        val = vhi if v else 0.0
        if last is None:
            pts.append((0.0, val))
        elif val != last:
            pts += [(t, last), (t + edge, val)]
        last = val
    return f"V{name} {name} 0 PWL(" + " ".join(f"{t:.4e} {v:g}" for t, v in pts) + ")"


def deck(net, ports, a):
    wave = {n: [] for n in INPUTS}
    samples, model = [], {}
    stored = {}
    can = None                                   # canary state known after the first set of each half
    set_halves = set()
    for i, (op, addr, data, mode, k) in enumerate(SEQ):
        t0 = i * T
        val = dict(WE=int(op == "W"), **{f"ADDR{j}": (addr >> j) & 1 for j in range(4)},
                   **{f"DIN{j}": (data >> j) & 1 for j in range(4)},
                   **{f"FI_MODE{j}": (mode >> j) & 1 for j in range(2)},
                   **{f"FI_POS{j}": (k >> j) & 1 for j in range(3)})
        wave["CLK"] += [(t0, 0), (t0 + T / 2, 1)]
        for n, v in val.items():
            wave[n].append((t0 + 5e-9, v))
        if op == "W":
            stored[addr] = encode(data) ^ mask(mode, k, True)
        else:
            if mode == 3 and k >> 1 == 2:            # set view: this half is set during this read
                set_halves.add(k & 1)
                can = 0 if set_halves == {0, 1} else can
            known = can if can is not None else (0 if (mode == 3 and k >> 1 in (1, 2) and k & 1 in set_halves) else None)
            if a.vdda < a.vdd - 1e-6:                # canaries are read at VDDA = VDD only (spec.md): not compared
                known = None
            samples.append((i, t0 + T - 5e-9, read_model(stored[addr], mode, k, known), (addr, mode, k)))
    t_end = len(SEQ) * T
    wave["CLK"].append((t_end, 0))
    L = [f"* chip core {a.corner} {a.temp}C VDD {a.vdd} VDDA {a.vdda} VDDW {a.vddw}",
         f".lib '{MODELS / '05cmos_mosfet_corner.lib'}' {a.corner}",
         f".include '{net}'",
         ".options gmin=1e-15 reltol=1e-3 abstol=1e-12 method=gear",
         f".temp {a.temp}",
         f"VVDD VDD 0 {a.vdd}", "VVSS VSS 0 0", f"VVDDA VDDA 0 {a.vdda}", f"VVDDW VDDW 0 {a.vddw}"]
    L += [pwl(n, wave[n], a.vdd) for n in INPUTS]
    L += [f"C{n} {n} 0 0.2p" for n in OUTPUTS]
    L.append("X1 " + " ".join(ports) + " ecc_sram_core")
    meas = []
    for i, ts, _, _ in samples:
        meas += [f"meas tran s{i}_{n} find v({n}) at={ts:.6e}" for n in OUTPUTS]
    L.append(f".tran 0.5n {t_end:.4e}")
    L.append(".control\nset num_threads=1\nrun\n" + "\n".join(meas) + "\n.endc\n.end\n")
    return "\n".join(L), samples


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corner", default="TT")
    ap.add_argument("--temp", type=int, default=27)
    ap.add_argument("--vdd", type=float, default=5.0)
    ap.add_argument("--vdda", type=float, default=5.0)
    ap.add_argument("--vddw", type=float, default=5.0)
    ap.add_argument("--reuse", action="store_true", help="only compare the log of an earlier run")
    ap.add_argument("--no-extract", action="store_true",
                    help="simulate the netlist of an earlier extraction (several corners at once)")
    a = ap.parse_args(argv)
    tag = f"chip_{a.corner}{a.temp}_{a.vdd:g}_{a.vdda:g}_{a.vddw:g}"
    if a.reuse:
        _, samples = deck(BUILD / f"core_pex_x{CAP_SCALE:g}.spice", [], a)
        log = (BUILD / f"{tag}.log").read_text()
    else:
        if a.no_extract:
            net = BUILD / f"core_pex_x{CAP_SCALE:g}.spice"
            if not net.exists():
                sys.exit(f"{net} not found: run once without --no-extract")
            ports = next(line.split()[2:] for line in net.read_text().splitlines()
                         if line.lower().startswith(".subckt"))
        else:
            net, ports = extract()
        text, samples = deck(net, ports, a)
        (BUILD / f"{tag}.cir").write_text(text)
        for lib in ("05cmos_mosfet_corner.lib", ".spiceinit"):
            dst = BUILD / lib
            if not dst.exists():
                dst.symlink_to(MODELS / lib)
        p = subprocess.run(["ngspice", "-b", f"{tag}.cir"], cwd=BUILD, capture_output=True, text=True, timeout=36000)
        log = p.stdout + p.stderr
        (BUILD / f"{tag}.log").write_text(log)
    # ngspice prints measurement names in lower case
    vals = {m[1].lower(): float(m[2]) for m in re.finditer(r"^(s\d+_\w+)\s*=\s*([-\d.eE+]+)", log, re.M)}
    bad = 0
    views = {0: "raw", 1: "canary", 2: "canary set", 3: "RO"}
    for i, ts, (dout, sec, ded), (addr, mode, k) in samples:
        got = [vals.get(f"s{i}_{n}".lower()) for n in OUTPUTS]
        if None in got:
            print(f"read {i}: no sample (see {BUILD / (tag + '.log')})")
            bad += 1
            continue
        bits = [int(v > a.vdd / 2) for v in got]
        g_dout = sum(b << j for j, b in enumerate(bits[:4]))
        ok = (bits[4], bits[5]) == (sec, ded) and (dout is None or g_dout == dout)
        bad += not ok
        dev = max(min(abs(v), abs(a.vdd - v)) for v in got)
        what = f"mode {mode} pos {k}" + (f" ({views[k >> 1]} view)" if mode == 3 else "")
        exp = "-" if dout is None else f"{dout:X}"
        print(f"read addr {addr:2d} {what}: DOUT {g_dout:X} SEC {bits[4]} DED {bits[5]}"
              f"  expected {exp} {sec} {ded}  {'ok' if ok else 'WRONG'}  (outputs at most {dev:.3f} V off a rail)")
    print(f"{tag}: {len(samples)} reads, {bad} wrong")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
