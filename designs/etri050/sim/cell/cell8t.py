#!/usr/bin/env python3
"""8T SRAM bit cell + column checks with the official PDK model (05cmos_mosfet_corner.lib, nmos4/pmos4).

Sizes on the drawable grid of the flow (W >= 1.8 um, L >= 0.6 um, 0.3 um steps), as drawn by gen/sram8t.py:
  PU 1.8/0.6, PD 3.0/0.6, PG 1.8/0.6, RD1/RD2 3.0/0.6,
  precharge 6.0/0.6, keeper 1.8/1.8, sense inverter P 4.5/0.6 N 1.8/0.6,
  write drivers (VDDA, always on): WDB = not WD (P 3.6 N 1.8), BL = not WDB and BLB = not WD (P 12.0 N 6.0).
Models: designs/etri050/sim/models (bash scripts/get-models.sh). Each run prints 'RES key=value' lines.
"""
import os, re, subprocess, sys, itertools, json
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "..", "models")
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

SZ = dict(PU=(1.8, 0.6), PD=(3.0, 0.6), PG=(1.8, 0.6), RD1=(3.0, 0.6), RD2=(3.0, 0.6),
          PRE=(6.0, 0.6), KEEP=(1.8, 1.8), SAP=(4.5, 0.6), SAN=(1.8, 0.6),
          WDP=(12.0, 0.6), WDN=(6.0, 0.6), WIP=(3.6, 0.6), WIN=(1.8, 0.6))


def mos(name, d, g, s, b, typ, w, l, m=1):
    ad = w * 2.1
    pd = 2 * (w + 2.1)
    return (f"M{name} {d} {g} {s} {b} {typ} W={w}u L={l}u AD={ad:.3f}p AS={ad:.3f}p "
            f"PD={pd:.3f}u PS={pd:.3f}u m={m}")


def cell(prefix, q, qb, bl, blb, wwl, rwl, rbl, vdda, sz, nm=None):
    """8T cell: cross-coupled pair at VDDA, write port PG to BL/BLB, read port RD2(RWL)-RD1(QB) to RBL."""
    nm = nm or f"nm_{prefix}"
    pu, pd, pg, r1, r2 = sz["PU"], sz["PD"], sz["PG"], sz["RD1"], sz["RD2"]
    return "\n".join([
        mos(f"{prefix}pul", q, qb, vdda, vdda, "pmos4", *pu),
        mos(f"{prefix}pur", qb, q, vdda, vdda, "pmos4", *pu),
        mos(f"{prefix}pdl", q, qb, 0, 0, "nmos4", *pd),
        mos(f"{prefix}pdr", qb, q, 0, 0, "nmos4", *pd),
        mos(f"{prefix}pgl", bl, wwl, q, 0, "nmos4", *pg),
        mos(f"{prefix}pgr", blb, wwl, qb, 0, "nmos4", *pg),
        mos(f"{prefix}rd1", nm, qb, 0, 0, "nmos4", *r1),
        mos(f"{prefix}rd2", rbl, rwl, nm, 0, "nmos4", *r2),
    ])


def header(corner, temp):
    return (f"* 8T column check {corner} {temp}C\n"
            f".lib '05cmos_mosfet_corner.lib' {corner}\n"
            f".options gmin=1e-15 abstol=1e-14 reltol=1e-4 method=gear\n"
            f".temp {temp}\n")


def run(name, deck):
    path = os.path.join(BUILD, name + ".cir")
    with open(path, "w") as f:
        f.write(deck)
    for lib in ("05cmos_mosfet_corner.lib", ".spiceinit"):
        src, dst = os.path.join(MODELS, lib), os.path.join(BUILD, lib)
        if not os.path.exists(src):
            sys.exit(f"{src} not found: run bash scripts/get-models.sh")
        if not os.path.exists(dst):
            os.symlink(os.path.abspath(src), dst)
    p = subprocess.run(["ngspice", "-b", name + ".cir"], cwd=BUILD, capture_output=True, text=True, timeout=600)
    out = p.stdout + p.stderr
    with open(os.path.join(BUILD, name + ".log"), "w") as f:
        f.write(out)
    res = {}
    for m in re.finditer(r"RES[ \t]+(\w+)[ \t]*=[ \t]*(\S+)", out):
        try:
            res[m.group(1)] = float(m.group(2))
        except ValueError:
            res[m.group(1)] = m.group(2)
    return res


# ---------------------------------------------------------------- write: delay and final state
def write_deck(corner, temp, vdd, vdda=None, sz=SZ):
    """Write 0 into a cell holding 1: WD = 0 -> BL = 0, BLB = VDDA (drivers in the VDDA domain)."""
    vdda = vdd if vdda is None else vdda
    wdp, wdn, wip, win = sz["WDP"], sz["WDN"], sz["WIP"], sz["WIN"]
    return header(corner, temp) + f"""
VDD vdd 0 {vdd}
VDDA vdda 0 {vdda}
VWD wd 0 0
{mos('wip', 'wdb', 'wd', 'vdda', 'vdda', 'pmos4', *wip)}
{mos('win', 'wdb', 'wd', 0, 0, 'nmos4', *win)}
{mos('wbp', 'bl', 'wdb', 'vdda', 'vdda', 'pmos4', *wdp)}
{mos('wbn', 'bl', 'wdb', 0, 0, 'nmos4', *wdn)}
{mos('wcp', 'blb', 'wd', 'vdda', 'vdda', 'pmos4', *wdp)}
{mos('wcn', 'blb', 'wd', 0, 0, 'nmos4', *wdn)}
CBL bl 0 25f
CBLB blb 0 25f
VWWL wwl 0 PULSE(0 {vdd} 5n 1n 1n 20n 100n)
VRWL rwl 0 0
VRBL rbl 0 {vdd}
{cell('c0', 'q', 'qb', 'bl', 'blb', 'wwl', 'rwl', 'rbl', 'vdda', sz)}
* 15 unselected cells on the same BL/BLB (load), holding the opposite data
{cell('cx', 'qx', 'qbx', 'bl', 'blb', '0', '0', 'rbl', 'vdda', sz)}
.ic v(q)={vdda} v(qb)=0 v(qx)=0 v(qbx)={vdda}
.tran 0.02n 50n uic
.control
run
meas tran tw trig v(wwl) val={vdd/2} rise=1 targ v(q) val={vdda/2} fall=1
meas tran qend find v(q) at=45n
meas tran qbend find v(qb) at=45n
echo "RES tw=$&tw"
echo "RES qend=$&qend"
echo "RES qbend=$&qbend"
.endc
.end
"""


# ---------------------------------------------------------------- write trip: slow BL ramp with WWL on
def wtrip_deck(corner, temp, vdd, sz=SZ):
    return header(corner, temp) + f"""
VDD vdd 0 {vdd}
VBL bl 0 PWL(0 {vdd} 1u {vdd} 21u 0)
VBLB blb 0 {vdd}
VWWL wwl 0 {vdd}
VRWL rwl 0 0
VRBL rbl 0 {vdd}
{cell('c0', 'q', 'qb', 'bl', 'blb', 'wwl', 'rwl', 'rbl', 'vdd', sz)}
.ic v(q)={vdd} v(qb)=0
.tran 5n 22u uic
.control
run
meas tran tflip when v(q)={vdd/2} fall=1
let vbltrip = {vdd} - ({vdd}/20u)*(tflip-1u)
echo "RES vbl_trip=$&vbltrip"
.endc
.end
"""


# ---------------------------------------------------------------- read: precharge, evaluate, keeper
def read_deck(corner, temp, vdd, data, vdda=None, t_eval=1e-6, keeper=True, sz=SZ, nleak=15):
    """data = stored Q of the selected cell. RBL follows Q (Q=0 -> RD1 on -> RBL discharges)."""
    vdda = vdd if vdda is None else vdda
    q0, qb0 = (0, vdda) if data == 0 else (vdda, 0)
    t_pre_off = 20e-9
    t_rwl = 21e-9
    t_end = t_rwl + t_eval
    kp = sz["KEEP"]
    keep = mos("keep", "rbl", "saout", "vdd", "vdd", "pmos4", *kp) if keeper else "* no keeper"
    # leakage-worst unselected cells: QB=1 so RD1 is on and RD2 (gate 0) sees full RBL voltage
    leak = (mos("lk2", "rbl", 0, "nmx", 0, "nmos4", *sz["RD2"], m=nleak) + "\n" +
            mos("lk1", "nmx", "vdda", 0, 0, "nmos4", *sz["RD1"], m=nleak)) if nleak else "* no leakers"
    return header(corner, temp) + f"""
VDD vdd 0 {vdd}
VDDA vdda 0 {vdda}
VPREB preb 0 PWL(0 0 {t_pre_off} 0 {t_pre_off+0.5e-9} {vdd})
VRWL rwl 0 PWL(0 0 {t_rwl} 0 {t_rwl+1e-9} {vdd})
VWWL wwl 0 0
VBL bl 0 {vdda}
VBLB blb 0 {vdda}
{mos('pre', 'rbl', 'preb', 'vdd', 'vdd', 'pmos4', *sz['PRE'])}
{keep}
{mos('sap', 'saout', 'rbl', 'vdd', 'vdd', 'pmos4', *sz['SAP'])}
{mos('san', 'saout', 'rbl', 0, 0, 'nmos4', *sz['SAN'])}
{mos('o2p', 'dout', 'saout', 'vdd', 'vdd', 'pmos4', 3.6, 0.6)}
{mos('o2n', 'dout', 'saout', 0, 0, 'nmos4', 1.8, 0.6)}
CRBL rbl 0 20f
COUT dout 0 30f
{cell('c0', 'q', 'qb', 'bl', 'blb', 'wwl', 'rwl', 'rbl', 'vdda', sz)}
{leak}
.ic v(q)={q0} v(qb)={qb0} v(rbl)={vdd} v(saout)=0 v(dout)={vdd}
.tran {max(t_eval/4000, 0.02e-9):.3e} {t_end:.4e} uic
.control
run
meas tran tread trig v(rwl) val={vdd/2} rise=1 targ v(saout) val={vdd/2} rise=1
meas tran vrbl_end find v(rbl) at={t_end*0.999:.4e}
meas tran vsa_end find v(saout) at={t_end*0.999:.4e}
meas tran qmin min v(q) from={t_rwl} to={t_end*0.999:.4e}
meas tran qbmin min v(qb) from={t_rwl} to={t_end*0.999:.4e}
echo "RES tread=$&tread"
echo "RES vrbl_end=$&vrbl_end"
echo "RES vsa_end=$&vsa_end"
echo "RES qmin=$&qmin"
echo "RES qbmin=$&qbmin"
.endc
.end
"""


# ---------------------------------------------------------------- critical injected current (light / particle)
def icrit_deck(corner, temp, vdda, direction, imax, sz=SZ):
    """direction 'down': sink current from Q while Q=1 (n+ junction collects). 'up': source into Q while Q=0."""
    q0, qb0 = (vdda, 0) if direction == "down" else (0, vdda)
    # ramp the injected current slowly instead of a DC sweep (keeps the latch on its branch)
    src = (f"IINJ q 0 PWL(0 0 2000u {imax})" if direction == "down"
           else f"IINJ 0 q PWL(0 0 2000u {imax})")
    return header(corner, temp) + f"""
VDDA vdda 0 {vdda}
VBL bl 0 0
VBLB blb 0 0
{cell('c0', 'q', 'qb', 'bl', 'blb', '0', '0', 'rbl', 'vdda', sz)}
VRBL rbl 0 0
{src}
.ic v(q)={q0} v(qb)={qb0}
.tran 1u 2000u uic
.control
run
meas tran tflip when v(qb)={vdda/2} {'rise' if direction=='down' else 'fall'}=1
let icrit = {imax}*tflip/2000e-6
echo "RES icrit=$&icrit"
.endc
.end
"""


def _job(args):
    kind, name, kw = args
    deck = {"write": write_deck, "wtrip": wtrip_deck, "read": read_deck, "icrit": icrit_deck}[kind](**kw)
    return name, kw, run(name, deck)


def pmap(jobs, workers=None):
    with ProcessPoolExecutor(max_workers=workers or os.cpu_count()) as ex:
        return list(ex.map(_job, jobs))


if __name__ == "__main__":
    print("module only")
