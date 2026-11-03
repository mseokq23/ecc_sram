#!/usr/bin/env python3
"""Retention time of one 8T cell held at low VDDA (transient), for the retention measurement plan.

The DC retention voltage (drv_butterfly.py, drv_mc_small.py) is the lowest VDDA at which the cell keeps two
stable states. A measurement holds VDDA low for a finite time, and two things are slow there: a stored 1 that
was above the new VDDA sits on a node that only subthreshold and junction leakage discharge, and a cell below
its DC retention voltage drifts into the one state left at the pace of those leakages.

For a cell holding Q = 1 this finds
  Q-QB    v(Q) - v(QB) at 1 ms, 10 ms, ... into the hold
  t_flip  time into the hold at which v(Q) - v(QB) first falls through 0 ("-": not within the hold)
  read    what the cell holds once VDDA is back at 5 V. The hold is simulated with ordinary steps and the
          ramp back up starts from the node voltages at the end of the hold with fine steps (with long
          steps an implicit integrator can sit on the metastable point and report Q = QB).
VDDA: 5 V -> V_hold in T_RAMP, held T_HOLD, back to 5 V in T_RAMP. Bit lines: the write drivers are always
on in the VDDA domain, so one of BL/BLB is 0 V and the other VDDA; the worst case (BL = 0 next to Q = 1,
BLB = VDDA next to QB = 0) is simulated. Mismatch: K sigma towards Q = 0 (PU_L weaker, PD_L stronger;
assumed Pelgrom A_VT 12/15 mV.um as in drv_mc_small.py). The DC retention voltage of the same cell is
printed for both bit line conditions.

  python3 designs/etri050/sim/cell/retention_time.py        (TT 27 C, K = 0 and 3, T_HOLD 100 s, T_RAMP 1 ms)
  CORNER=TT TEMP=27 K_LIST=0,2 T_HOLD=10 T_RAMP=1e-3 python3 designs/etri050/sim/cell/retention_time.py
"""
import os, sys, json, math
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell8t as c
import drv_mc_small as mcs

SZ = c.SZ
SP = 15e-3 / math.sqrt(SZ["PU"][0] * SZ["PU"][1])
SN = 12e-3 / math.sqrt(SZ["PD"][0] * SZ["PD"][1])
CORNER = os.environ.get("CORNER", "TT")
TEMP = int(os.environ.get("TEMP", "27"))
T_HOLD = float(os.environ.get("T_HOLD", "100"))
T_RAMP = float(os.environ.get("T_RAMP", "1e-3"))
K_LIST = [float(k) for k in os.environ.get("K_LIST", "0,3").split(",")]
V_LIST = [float(v) for v in os.environ.get("V_LIST", "0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50").split(",")]
MARKS = [m for m in (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0) if m <= T_HOLD]


def offsets(k):
    return [k * SP, -k * SN, 0.0, 0.0, 0.0, 0.0]          # pul, pdl, pgl, pur, pdr, pgr


def cell_lines(k):
    pul, pdl, pgl, pur, pdr, pgr = offsets(k)
    return f"""Vpl gpl qb {pul:.6f}
Vnl gnl qb {-pdl:.6f}
Vgl ggl 0 {-pgl:.6f}
Vpr gpr q {pur:.6f}
Vnr gnr q {-pdr:.6f}
Vgr ggr 0 {-pgr:.6f}
{c.mos('pul', 'q', 'gpl', 'vdda', 'vdda', 'pmos4', *SZ['PU'])}
{c.mos('pdl', 'q', 'gnl', 0, 0, 'nmos4', *SZ['PD'])}
{c.mos('pgl', 'bl', 'ggl', 'q', 0, 'nmos4', *SZ['PG'])}
{c.mos('pur', 'qb', 'gpr', 'vdda', 'vdda', 'pmos4', *SZ['PU'])}
{c.mos('pdr', 'qb', 'gnr', 0, 0, 'nmos4', *SZ['PD'])}
{c.mos('pgr', 'blb', 'ggr', 'qb', 0, 'nmos4', *SZ['PG'])}
{c.mos('rd1', 'nm', 'qb', 0, 0, 'nmos4', *SZ['RD1'])}
Cq q 0 3f
Cqb qb 0 3f
VBL bl 0 0"""


def hold_deck(v, k):
    ta, tb = 10e-6, 10e-6 + T_RAMP
    tc = tb + T_HOLD
    pwl = f"PWL(0 5 {ta:.6e} 5 {tb:.6e} {v} {tc:.6e} {v})"
    meas = "\n".join(f"meas tran d{i} find dqq at={tb + m:.6e}\necho \"RES d{i}=$&d{i}\"" for i, m in enumerate(MARKS))
    return c.header(CORNER, TEMP) + f"""
VDDA vdda 0 {pwl}
VBLB blb 0 {pwl}
{cell_lines(k)}
.ic v(q)=5 v(qb)=0
.tran 1u {tc:.6e} 0 {max(T_HOLD / 50000, 1e-6):.6e}
.control
run
let dqq = v(q) - v(qb)
meas tran tflip when dqq=0 fall=1
meas tran qh find v(q) at={tc:.6e}
meas tran qbh find v(qb) at={tc:.6e}
meas tran nmh find v(nm) at={tc:.6e}
echo "RES tflip=$&tflip"
echo "RES qh=$&qh"
echo "RES qbh=$&qbh"
echo "RES nmh=$&nmh"
{meas}
.endc
.end
"""


def rampup_deck(v, k, q, qb, nm):
    ta, tb = 1e-6, 1e-6 + T_RAMP
    te = tb + 50e-6
    pwl = f"PWL(0 {v} {ta:.6e} {v} {tb:.6e} 5 {te:.6e} 5)"
    return c.header(CORNER, TEMP) + f"""
VDDA vdda 0 {pwl}
VBLB blb 0 {pwl}
{cell_lines(k)}
.ic v(q)={q:.6g} v(qb)={qb:.6g} v(nm)={nm:.6g}
.tran 1n {te:.6e} 0 {T_RAMP / 2000:.6e}
.control
run
meas tran qend find v(q) at={te - 1e-6:.6e}
meas tran qbend find v(qb) at={te - 1e-6:.6e}
echo "RES qend=$&qend"
echo "RES qbend=$&qbend"
.endc
.end
"""


def job(a):
    v, k = a
    tag = f"rt_{CORNER}{TEMP}_k{k:g}_{v:.3f}_{T_HOLD:g}s"
    h = c.run(tag + "_hold", hold_deck(v, k))
    if not all(isinstance(h.get(n), float) for n in ("qh", "qbh", "nmh")):
        raise RuntimeError(f"{tag}: hold run failed, see {c.BUILD}/{tag}_hold.log")
    u = c.run(tag + "_up", rampup_deck(v, k, h["qh"], h["qbh"], h["nmh"]))
    tf = h.get("tflip")
    tf = tf - (10e-6 + T_RAMP) if isinstance(tf, float) else None
    return dict(k_sigma=k, v_hold=v, t_flip=tf, read=("1" if u["qend"] > u["qbend"] else "0"),
                q_minus_qb={f"{m:g}s": h.get(f"d{i}") for i, m in enumerate(MARKS)})


def fmt_t(t):
    if t is None:
        return "-"
    if t < 0:
        return "ramp"
    return f"{t * 1e3:.3g} ms" if t < 1 else f"{t:.3g} s"


def main():
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        dc = list(ex.map(mcs.one, [(CORNER, TEMP, f"k{k:g}", offsets(k), bl) for k in K_LIST for bl in ("worst", "idle")]))
        res = list(ex.map(job, [(v, k) for k in K_LIST for v in V_LIST]))
    dcv = {(k, bl): dc[2 * i + j][1] for i, k in enumerate(K_LIST) for j, bl in enumerate(("worst", "idle"))}
    print(f"{CORNER} {TEMP} C, VDDA ramps {T_RAMP * 1e3:g} ms, hold {T_HOLD:g} s, cell holds Q = 1, "
          f"BL = 0 / BLB = VDDA during the hold")
    for k in K_LIST:
        w, i = dcv[(k, "worst")], dcv[(k, "idle")]
        print(f"\nK = {k:g} sigma towards Q = 0 (PU_L +{k * SP * 1e3:.1f} mV, PD_L -{k * SN * 1e3:.1f} mV): "
              f"DC retention voltage {w if w is None else round(w, 3)} V (these bit lines), "
              f"{i if i is None else round(i, 3)} V (both bit lines at VDDA)")
        print("  V_hold  Q-QB at " + " ".join(f"{m:>7g}s" for m in MARKS) + "    t_flip    read")
        for r in [r for r in res if r["k_sigma"] == k]:
            d = " ".join(f"{(r['q_minus_qb'][f'{m:g}s'] or float('nan')):8.3f}" for m in MARKS)
            print(f"  {r['v_hold']:5.2f} V          {d}  {fmt_t(r['t_flip']):>8s}    {r['read']}")
    out = dict(corner=CORNER, temp=TEMP, t_hold=T_HOLD, t_ramp=T_RAMP,
               dc_retention={f"k{k:g}_{bl}": dcv[(k, bl)] for k in K_LIST for bl in ("worst", "idle")}, runs=res)
    json.dump(out, open(os.path.join(c.BUILD, f"retention_time_{CORNER}{TEMP}_{T_HOLD:g}s.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
