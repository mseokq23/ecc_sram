#!/usr/bin/env python3
"""Which way do writes fail when the bit line drivers' supply VDDW is lowered? (VDD = VDDA = 5 V)

Writing 0 over a stored 1 needs BL pulled low by the BL driver's NMOS, whose gate is BLB at the VDDW level:
it weakens as VDDW drops and the write fails (the write Vmin of sweep_vdda.py). Writing 1 over a stored 0
needs BLB pulled low by the BLB driver's NMOS, whose gate is WD at the 5 V level, so it should not depend on
VDDW. This sweeps both writes over VDDW for every corner and temperature: if only the 0-writes fail, a
low-VDDW write failure can only leave a 1 where a 0 was meant (0 -> 1), which the direction view assumes.

Below about 1 V neither driver holds its bit line any more (the BL driver's PMOS and NMOS both see gate
voltages near their thresholds), so a write there depends on where the floating bit lines were: the sweep
reports those points too, and the measurement plan keeps VDDW at 1 V or more.

  python3 designs/etri050/sim/cell/write_dir.py
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell8t as c

CORNERS = ("TT", "SS", "FF", "SF", "FS")
TEMPS = (0, 27, 125)
VDDW = (0.3, 0.6, 0.9, 1.2, 1.5, 1.7, 1.8, 1.9, 2.0)


def deck(corner, temp, vddw, data, vdd=5.0, vdda=5.0, sz=c.SZ):
    """Write `data` into a cell holding the other value; WWL is on for 200 ns."""
    wdp, wdn = sz["WDP"], sz["WDN"]
    wd = vdd if data == 1 else 0
    q0, qb0 = (0, vdda) if data == 1 else (vdda, 0)
    return c.header(corner, temp) + f"""
VDD vdd 0 {vdd}
VDDA vdda 0 {vdda}
VDDW vddw 0 {vddw}
VWD wd 0 {wd}
{c.mos('wcp', 'blb', 'wd', 'vddw', 'vddw', 'pmos4', *wdp)}
{c.mos('wcn', 'blb', 'wd', 0, 0, 'nmos4', *wdn)}
{c.mos('wbp', 'bl', 'blb', 'vddw', 'vddw', 'pmos4', *wdp)}
{c.mos('wbn', 'bl', 'blb', 0, 0, 'nmos4', *wdn)}
CBL bl 0 25f
CBLB blb 0 25f
VWWL wwl 0 PULSE(0 {vdd} 5n 1n 1n 200n 1u)
VRWL rwl 0 0
VRBL rbl 0 {vdd}
{c.cell('c0', 'q', 'qb', 'bl', 'blb', 'wwl', 'rwl', 'rbl', 'vdda', sz)}
* 15 unselected cells on the same bit lines (load), holding the opposite of c0's old value
{c.cell('cx', 'qx', 'qbx', 'bl', 'blb', '0', '0', 'rbl', 'vdda', sz)}
.ic v(q)={q0} v(qb)={qb0} v(qx)={qb0} v(qbx)={q0}
.tran 0.05n 400n uic
.control
run
meas tran qend find v(q) at=390n
meas tran qbend find v(qb) at=390n
echo "RES qend=$&qend"
echo "RES qbend=$&qbend"
.endc
.end
"""


def written(args):
    corner, temp, vddw, data = args
    r = c.run(f"wdir{data}_{corner}_{temp}_{vddw:.2f}", deck(corner, temp, vddw, data))
    q, qb = r.get("qend", -1.0), r.get("qbend", -1.0)
    ok = (q > 4.5 and qb < 0.5) if data == 1 else (q < 0.5 and qb > 4.5)
    return args, ok


def main():
    os.makedirs(c.BUILD, exist_ok=True)
    for lib in ("05cmos_mosfet_corner.lib", ".spiceinit"):      # link once before the parallel runs
        src, dst = os.path.join(c.MODELS, lib), os.path.join(c.BUILD, lib)
        if os.path.exists(src) and not os.path.lexists(dst):
            os.symlink(os.path.abspath(src), dst)
    cases = [(k, t, v, d) for k in CORNERS for t in TEMPS for v in VDDW for d in (1, 0)]
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        res = dict(ex.map(written, cases))
    print("write into a cell holding the other value, VDD = VDDA = 5 V, WWL 200 ns")
    print("  1 / 0: written,  . / x: not written")
    print("           VDDW " + " ".join(f"{v:4.1f}" for v in VDDW))
    one_fails = 0
    for k in CORNERS:
        for t in TEMPS:
            w1 = " ".join("   1" if res[(k, t, v, 1)] else "   ." for v in VDDW)
            w0 = " ".join("   0" if res[(k, t, v, 0)] else "   x" for v in VDDW)
            one_fails += sum(not res[(k, t, v, 1)] for v in VDDW)
            print(f"{k} {t:>3} C  write 1 {w1}")
            print(f"          write 0 {w0}")
    print(f"failed 1-writes: {one_fails}")


if __name__ == "__main__":
    main()
