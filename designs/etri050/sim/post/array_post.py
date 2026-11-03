#!/usr/bin/env python3
"""Post-layout check of the drawn 15 x 8 array: Magic extraction (devices + parasitic C) of
designs/etri050/sram/build/sram_array.mag, column circuits from the schematic, official PDK models.

Every corner run writes two patterns (checkerboard and its inverse) into all 15 rows, reads every row
back through RBL -> precharge/keeper -> sense inverter, and compares all 8 bits of every read.
The VDDA dip runs write the checkerboard at VDDA = 5 V, take VDDA down to a low value for 2 us, restore 5 V and read: they
check that the array and the always-on VDDA write drivers come back without touching the data. 2 us is far
too short for leakage to move a cell below its retention voltage (that takes about a second at 27 C, see
sim/cell/retention_time.py), so these runs are not retention tests.

  python3 designs/etri050/sim/post/array_post.py               # corners + VDDA dip cases
  python3 designs/etri050/sim/post/array_post.py --quick       # TT 27 C 5 V only
  CAP_SCALE=1.5 python3 ...                                    # extracted C x 1.5 (margin)

Magic's extraction in this kit uses AMI 0.5 um coefficients (not ETRI's table 5.5), so the
capacitance is scaled by CAP_SCALE (default 1.5) on top of the extracted values.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BUILD = HERE / "build"
MODELS = REPO / "designs/etri050/sim/models"
ARRAY = REPO / "designs/etri050/sram/build/sram_array.mag"
ROWS, COLS = 15, 8
T = 100e-9                 # cycle: CLK low (precharge, inputs change) then CLK high (read / write)
EDGE = 1e-9
CAP_SCALE = float(os.environ.get("CAP_SCALE", "1.5"))

# column circuit sizes (um): precharge, keeper, sense and output inverters (VDD), write drivers (VDDA)
COL = dict(PRE=(6.0, 0.6), KEEP=(1.8, 1.8), SAP=(4.5, 0.6), SAN=(1.8, 0.6), OP=(3.6, 0.6), ON=(1.8, 0.6),
           WIP=(3.6, 0.6), WIN=(1.8, 0.6), WDP=(12.0, 0.6), WDN=(6.0, 0.6))


def magicrc():
    dk = os.environ.get("ETRI050_DK", str(REPO / ".pdk/ETRI050_DesignKit"))
    return os.environ.get("ETRI050_MAGICRC", os.path.join(dk, "tech/etri050.magicrc"))


def extract() -> tuple[Path, list[str]]:
    """Magic extraction with capacitance; returns the netlist (nmos4/pmos4) and its port order."""
    BUILD.mkdir(parents=True, exist_ok=True)
    if not ARRAY.exists():
        sys.exit(f"{ARRAY} not found: run python3 designs/etri050/gen/sram8t.py array")
    work = BUILD / "pex"
    work.mkdir(exist_ok=True)
    (work / "sram_array.mag").write_text(ARRAY.read_text())
    script = """load sram_array -force
extract do capacitance
extract do coupling
extract all
ext2spice cthresh 0
ext2spice format ngspice
ext2spice scale off
ext2spice subcircuit top on
ext2spice -o sram_array_pex.spice
quit -noprompt
"""
    subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", magicrc()], input=script, text=True,
                   cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    raw = (work / "sram_array_pex.spice").read_text()
    lines, ports = [], []
    for line in raw.splitlines():            # join continuation lines
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
        line = re.sub(r"\bnfet\b", "nmos4", re.sub(r"\bpfet\b", "pmos4", line))
        out.append(line)
    net = BUILD / f"sram_array_pex_x{CAP_SCALE:g}.spice"
    net.write_text("\n".join(out) + "\n")
    return net, ports


def mos(name, d, g, s, b, typ, wl):
    w, l = wl
    a = w * 2.1
    return f"M{name} {d} {g} {s} {b} {typ} W={w}u L={l}u AD={a:.3f}p AS={a:.3f}p PD={2 * (w + 2.1):.3f}u PS={2 * (w + 2.1):.3f}u"


def column(c):
    """Read path (VDD) and write drivers (VDDA) of column c."""
    g = COL
    return "\n".join([
        mos(f"pre{c}", f"RBL{c}", "PREN", "VDD", "VDD", "pmos4", g["PRE"]),
        mos(f"kp{c}", f"RBL{c}", f"SA{c}", "VDD", "VDD", "pmos4", g["KEEP"]),
        mos(f"sap{c}", f"SA{c}", f"RBL{c}", "VDD", "VDD", "pmos4", g["SAP"]),
        mos(f"san{c}", f"SA{c}", f"RBL{c}", "0", "0", "nmos4", g["SAN"]),
        mos(f"op{c}", f"DOUT{c}", f"SA{c}", "VDD", "VDD", "pmos4", g["OP"]),
        mos(f"on{c}", f"DOUT{c}", f"SA{c}", "0", "0", "nmos4", g["ON"]),
        f"CDOUT{c} DOUT{c} 0 30f",
        # write drivers: BLB = not WD, BL = not (not WD); inputs come at VDD levels
        mos(f"wip{c}", f"WDB{c}", f"WD{c}", "VDDA", "VDDA", "pmos4", g["WIP"]),
        mos(f"win{c}", f"WDB{c}", f"WD{c}", "0", "0", "nmos4", g["WIN"]),
        mos(f"wbp{c}", f"BL{c}", f"WDB{c}", "VDDA", "VDDA", "pmos4", g["WDP"]),
        mos(f"wbn{c}", f"BL{c}", f"WDB{c}", "0", "0", "nmos4", g["WDN"]),
        mos(f"wcp{c}", f"BLB{c}", f"WD{c}", "VDDA", "VDDA", "pmos4", g["WDP"]),
        mos(f"wcn{c}", f"BLB{c}", f"WD{c}", "0", "0", "nmos4", g["WDN"]),
    ])


def pwl(points, name, node, vhi, rs=None):
    """PWL source from [(t, level 0/1)], edges EDGE wide."""
    pts, last = [], None
    for t, v in points:
        val = vhi if v else 0.0
        if last is None:
            pts.append((0.0, val))
        elif val != last:
            pts.append((t, last))
            pts.append((t + EDGE, val))
        last = val
    txt = " ".join(f"{t:.4e} {v:g}" for t, v in pts)
    if rs:
        return f"V{name} {name}_src 0 PWL({txt})\nR{name} {name}_src {node} {rs}"
    return f"V{name} {node} 0 PWL({txt})"


def pattern(p, r, c):
    """Bit of row r, column c for pattern p (0 checkerboard, 1 inverse)."""
    return ((r + c) % 2) ^ p


def schedule(retention=None):
    """Cycles: (kind, row, pattern). Writes all rows, reads them back, for both patterns.
    retention: (v_low, t_low) -> write pattern 0, VDDA at v_low for t_low, restore, read."""
    cyc = []
    pats = [0] if retention else [0, 1]
    for p in pats:
        cyc += [("W", r, p) for r in range(ROWS)]
        if retention:
            cyc += [("HOLD", None, p)]
        cyc += [("R", r, p) for r in range(ROWS)]
    return cyc


def deck(net, ports, corner, temp, vdd, vdda, retention=None):
    cyc = schedule(retention)
    t_hold = retention[1] if retention else 0.0
    times, t = [], 0.0
    for kind, r, p in cyc:
        times.append(t)
        t += t_hold if kind == "HOLD" else T
    t_end = t
    clk = []
    wwl = {r: [] for r in range(ROWS)}
    rwl = {r: [] for r in range(ROWS)}
    wd = {c: [] for c in range(COLS)}
    samples = []
    for (kind, r, p), t0 in zip(cyc, times):
        if kind == "HOLD":
            clk.append((t0, 0))
            continue
        clk += [(t0, 0), (t0 + T / 2, 1)]
        for rr in range(ROWS):
            wwl[rr] += [(t0, 0), (t0 + T / 2, 1 if (kind == "W" and rr == r) else 0)]
            rwl[rr] += [(t0, 0), (t0 + T / 2, 1 if (kind == "R" and rr == r) else 0)]
        if kind == "W":
            for c in range(COLS):
                wd[c] += [(t0 + 2e-9, pattern(p, r, c))]
        else:
            samples.append((t0 + T - 3e-9, r, p))
    clk.append((t_end, 0))
    L = [f"* post-layout array check {corner} {temp}C VDD {vdd} VDDA {vdda}",
         f".lib '{MODELS / '05cmos_mosfet_corner.lib'}' {corner}",
         f".include '{net}'",
         ".options gmin=1e-15 reltol=1e-3 abstol=1e-12 method=gear",
         f".temp {temp}",
         f"VVDD VDD 0 {vdd}"]
    if retention:
        v_hold, th = retention
        t_h0 = times[[k for k, *_ in cyc].index("HOLD")]
        L.append(f"VVDDA VDDA 0 PWL(0 {vdda} {t_h0 + 5e-9:.4e} {vdda} {t_h0 + 15e-9:.4e} {v_hold} "
                 f"{t_h0 + th - 25e-9:.4e} {v_hold} {t_h0 + th - 15e-9:.4e} {vdda})")
    else:
        L.append(f"VVDDA VDDA 0 {vdda}")
    L.append(pwl(clk, "PREN", "PREN", vdd))
    for r in range(ROWS):
        L.append(pwl(wwl[r], f"WWL{r}", f"WWL{r}", vdd, rs="1k"))
        L.append(pwl(rwl[r], f"RWL{r}", f"RWL{r}", vdd, rs="1k"))
    for c in range(COLS):
        L.append(pwl(wd[c] or [(0, 0)], f"WD{c}", f"WD{c}", vdd))
    L.append("Xarr " + " ".join(ports) + " sram_array")
    for c in range(COLS):
        L.append(column(c))
    # sample DOUT at the end of each read cycle with the ngspice 'meas' command
    meas = []
    for k, (ts, r, p) in enumerate(samples):
        for c in range(COLS):
            meas.append(f"meas tran s{k}_{c} find v(DOUT{c}) at={ts:.6e}")
    L.append(f".tran 0.5n {t_end:.4e}")
    L.append(".control\nset num_threads=1\nrun\n" + "\n".join(meas) + "\n.endc\n.end\n")
    return "\n".join(L), samples


def run_case(args):
    name, net, ports, corner, temp, vdd, vdda, retention = args
    text, samples = deck(net, ports, corner, temp, vdd, vdda, retention)
    cir = BUILD / f"{name}.cir"
    cir.write_text(text)
    p = subprocess.run(["ngspice", "-b", str(cir)], cwd=BUILD, capture_output=True, text=True, timeout=7200)
    log = p.stdout + p.stderr
    (BUILD / f"{name}.log").write_text(log)
    vals = {m[1]: float(m[2]) for m in re.finditer(r"^(s\d+_\d+)\s*=\s*([-\d.eE+]+)", log, re.M)}
    bad, worst_hi, worst_lo = 0, vdd, 0.0
    for k, (ts, r, p) in enumerate(samples):
        for c in range(COLS):
            v = vals.get(f"s{k}_{c}")
            exp = pattern(p, r, c)
            if v is None:
                bad += 1
                continue
            got = 1 if v > vdd / 2 else 0
            bad += got != exp
            if exp:
                worst_hi = min(worst_hi, v)
            else:
                worst_lo = max(worst_lo, v)
    return dict(name=name, corner=corner, temp=temp, vdd=vdd, vdda=vdda, retention=retention,
                reads=len(samples), bits=len(samples) * COLS, errors=bad,
                dout1_min=round(worst_hi, 3), dout0_max=round(worst_lo, 3))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args(argv)
    net, ports = extract()
    cases = [("tt27", "TT", 27, 5.0, 5.0, None)]
    if not a.quick:
        cases += [("ss125_4v5", "SS", 125, 4.5, 4.5, None), ("ff0_5v5", "FF", 0, 5.5, 5.5, None),
                  ("sf27", "SF", 27, 5.0, 5.0, None), ("fs27", "FS", 27, 5.0, 5.0, None),
                  ("tt27_vdda2", "TT", 27, 5.0, 2.0, None),
                  ("dip_0v6", "TT", 27, 5.0, 5.0, (0.6, 2e-6)),
                  ("dip_0v2", "TT", 27, 5.0, 5.0, (0.2, 2e-6))]
    jobs = [(n, net, ports, k, t, vdd, vdda, ret) for n, k, t, vdd, vdda, ret in cases]
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        res = list(ex.map(run_case, jobs))
    for r in res:
        print(f"{r['name']:12s} {r['corner']} {r['temp']:>3} C VDD {r['vdd']} VDDA {r['vdda']}"
              f"{'' if not r['retention'] else ' VDDA dip to %.1f V' % r['retention'][0]}: "
              f"{r['bits']} bits read, {r['errors']} wrong, DOUT '1' min {r['dout1_min']} V, '0' max {r['dout0_max']} V")
    (BUILD / "array_post.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
