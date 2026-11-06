#!/usr/bin/env python3
"""Canary latches of the retention early warning (gen/canary.py), with the official PDK model.

Each canary is a latch on the array supply VDDA whose set state (A = 1, B = 0) is held by a weak PMOS P1
against the off-state leakage of a wide NMOS N1 (the skewed inverter CINV; the latch's other inverter is a
kit NOR2X1 whose second input is CSET). Below some VDDA the PMOS's subthreshold current no longer
beats that leakage and the latch falls into its other state; the same contest (PU against PD and PG leakage)
sets the retention voltage of the 8T cells, with a much smaller skew. Eight sizings give a ladder of these
voltages above the array's.

  python3 designs/etri050/sim/cell/canary_sim.py ladder   retention voltage of every canary and of the 8T cell
                                                       (nominal), 5 corners at 27 C and TT at 0 / 125 C
  python3 designs/etri050/sim/cell/canary_sim.py mc       Vt-mismatch spread of every canary (TT 27 C, Pelgrom
                                                       A_VT 12 / 15 mV.um as for the cell), one latch per netlist
  python3 designs/etri050/sim/cell/canary_sim.py snm      set-state noise margin at VDDA = 4.5 and 5.0 V, corners
  python3 designs/etri050/sim/cell/canary_sim.py set      CSET pulse: every canary from its preferred state to the
                                                       set state, corners, 100 ns pulse
  python3 designs/etri050/sim/cell/canary_sim.py hold     VDDA held 10 s 30 mV above and below each canary's retention
                                                       voltage (TT 27 C), then back to 5 V: kept / lost, time to flip
  python3 designs/etri050/sim/cell/canary_sim.py readout  read-out gate: CAN = not A with CRD_N = 0, 0 with CRD_N = 1;
                                                       VDD current at VDDA = 1.4 V with the gate on and off
Results: designs/etri050/sim/cell/build/canary_<what>.json, 'RES' lines in the logs as in cell8t.py.

Retention voltage (DC): the lowest VDDA at which the set state keeps a noise margin (composite-map test of
drv_butterfly.py on the two transfer curves, series noise at the inputs) above 1 mV: a 20 mV scan down from
1.2 V, then bisection to 0.5 mV. One latch per
netlist and the sweep starts at -0.1 V: with many latches in one netlist, or with the first sweep point at 0 V,
ngspice's operating point on these pA-level nodes can stop short of the true solution.
"""
import os, sys, json, math
import numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "gen"))
import cell8t as c
import drv_butterfly as bf
import drv_mc_small as mcs
import canary as cg                                   # gen/canary.py: sizes of the drawn block

CORNERS = [("TT", 27), ("SS", 27), ("FF", 27), ("SF", 27), ("FS", 27), ("TT", 0), ("TT", 125)]


def latch_lines(k, off=(0.0, 0.0, 0.0, 0.0), x="x", vdda="vdda"):
    """The latch of canary k as two transfer curves with input x: oa = CINV (A from B), ob = the latch NOR2X1
    with CSET = 0 (B from A). Gate offsets (P1, N1, NOR PMOS on A, NOR NMOS on A)."""
    s = cg.sizes(k)
    o1p, o1n, o2p, o2n = off
    return "\n".join([
        f"Vpa gpa {x} {o1p:.6f}", f"Vna gna {x} {-o1n:.6f}", f"Vpb gpb {x} {o2p:.6f}", f"Vnb gnb {x} {-o2n:.6f}",
        c.mos("p1", "oa", "gpa", vdda, vdda, "pmos4", *s["P1"]),
        c.mos("n1", "oa", "gna", 0, 0, "nmos4", *s["N1"]),
        c.mos("lpa", "mid", "gpb", vdda, vdda, "pmos4", *s["NP"]),
        c.mos("lpb", "ob", 0, "mid", vdda, "pmos4", *s["NP"]),
        c.mos("lna", "ob", "gnb", 0, 0, "nmos4", *s["NN"]),
        c.mos("lnb", "ob", 0, 0, 0, "nmos4", *s["NN"])])


def vtc_deck(corner, temp, vdda, k, off, tag, npts=600, x0=-0.1):
    return (c.header(corner, temp) + f"VDDA vdda 0 {vdda}\nVIN x 0 0\n" + latch_lines(k, off) + "\n"
            + f".dc VIN {x0} {vdda} {(vdda - x0) / npts:.6e}\n"
            + f".control\nrun\nset wr_singlescale\nset wr_vecnames\nwrdata vtc_{tag}.txt v(oa) v(ob)\n.endc\n.end\n")


def bistable(corner, temp, vdda, k, off, tag, vn=0.0):
    t = f"{tag}_{vdda:.5f}"
    c.run(t, vtc_deck(corner, temp, vdda, k, off, t))
    d = np.loadtxt(os.path.join(c.BUILD, f"vtc_{t}.txt"), skiprows=1)
    return d, bf.bistable(d[:, 0], d[:, 1], d[:, 2], vdda, vn)


def drv_job(args):
    """(corner, temp, k, offsets, key) -> (key, retention voltage of the set state): the lowest VDDA at which
    the set state keeps a noise margin above SNM_EPS. Scan down in 20 mV steps from 1.2 V to the first VDDA
    without it, then bisect to 0.5 mV (a scan, not a plain bisection: well below the retention voltage the
    curves sit at a few mV and their numerical noise can mimic a second state)."""
    corner, temp, k, off, key, *rest = args
    start, step = (rest[0], 0.01) if rest else (1.20, 0.02)

    def ok(v):
        d, bi = bistable(corner, temp, v, k, off, key)
        return bi and set_snm(d, v) > SNM_EPS
    hi = start
    if not ok(hi):
        return key, None
    while hi > 0.11:
        lo = round(hi - step, 4)
        if not ok(lo):
            break
        hi = lo
    else:
        return key, hi
    for _ in range(6 if step > 0.015 else 5):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return key, hi


SNM_EPS = 1e-3


def set_snm(d, vdda):
    """Noise margin of the set state (A high): largest series noise that keeps the latch bistable."""
    x, fa, fb = d[:, 0], d[:, 1], d[:, 2]
    if not bf.bistable(x, fa, fb, vdda, 0.0):
        return 0.0
    lo, hi = 0.0, vdda / 2
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if bf.bistable(x, fa, fb, vdda, mid):
            lo = mid
        else:
            hi = mid
    return lo


def pool():
    return ProcessPoolExecutor(max_workers=os.cpu_count())


def link_models():
    for lib in ("05cmos_mosfet_corner.lib", ".spiceinit"):
        dst = os.path.join(c.BUILD, lib)
        if not os.path.exists(dst):
            os.symlink(os.path.abspath(os.path.join(c.MODELS, lib)), dst)


# ---------------------------------------------------------------- ladder
def ladder():
    jobs = [(co, t, k, (0, 0, 0, 0), f"cl_{co}{t}_{k}") for co, t in CORNERS for k in range(cg.N)]
    cell = [(co, t, f"cell_{co}{t}_{bl}", [0.0] * 6, bl) for co, t in CORNERS for bl in ("idle", "worst")]
    with pool() as ex:
        r = dict(ex.map(drv_job, jobs))
        rc = dict(ex.map(mcs.one, cell))
    out = {}
    print("retention voltage of the set state (V); cell = 8T cell nominal (bit lines idle / BL = 0 next to Q = 1)")
    print("corner   " + " ".join(f"   C{k}" for k in range(cg.N)) + "   cell idle  worst   C0-cell  C7-cell")
    for co, t in CORNERS:
        v = [r[f"cl_{co}{t}_{k}"] for k in range(cg.N)]
        ci, cw = rc[f"cell_{co}{t}_idle"], rc[f"cell_{co}{t}_worst"]
        out[f"{co}{t}"] = dict(canary=v, cell_idle=ci, cell_worst=cw)
        print(f"{co} {t:>3} C " + " ".join(f"{x:.3f}" for x in v)
              + f"   {ci:.3f}  {cw:.3f}   {v[0] - cw:+.3f}   {v[-1] - cw:+.3f}")
    return out


# ---------------------------------------------------------------- Vt mismatch
def mc(M=int(os.environ.get("MC_M", "100"))):
    out = {}
    jobs = []
    with pool() as ex:
        nom = dict(ex.map(drv_job, [("TT", 27, k, (0, 0, 0, 0), f"cmn_{k}") for k in range(cg.N)]))
    for k in range(cg.N):
        s = cg.sizes(k)
        sig = [a * 1e-3 / math.sqrt(s[dev][0] * s[dev][1]) for a, dev in ((15, "P1"), (12, "N1"), (15, "NP"), (12, "NN"))]
        rng = np.random.default_rng(20261106 + k)
        off = np.column_stack([rng.normal(0, sg, M) for sg in sig])
        off[0, :] = 0
        jobs += [("TT", 27, k, tuple(off[i]), f"cm_{k}_{i}", round(nom[f"cmn_{k}"] + 0.10, 3)) for i in range(M)]
        out[f"C{k}"] = dict(sigma_vt_mV=[round(sg * 1e3, 2) for sg in sig])
    with pool() as ex:
        r = dict(ex.map(drv_job, jobs))
    print(f"TT 27 C, {M} samples per canary (sample 0 nominal)")
    for k in range(cg.N):
        d = np.array([r[f"cm_{k}_{i}"] for i in range(M)], dtype=float)
        out[f"C{k}"].update(nominal=float(d[0]), mean=float(np.nanmean(d)), std=float(np.nanstd(d)),
                            p1=float(np.nanpercentile(d, 1)), p99=float(np.nanpercentile(d, 99)),
                            min=float(np.nanmin(d)), max=float(np.nanmax(d)))
        o = out[f"C{k}"]
        print(f"C{k}: nominal {o['nominal']:.3f} V  mean {o['mean']:.3f}  sigma {o['std'] * 1e3:.1f} mV  "
              f"1-99 % {o['p1']:.3f}-{o['p99']:.3f}  min-max {o['min']:.3f}-{o['max']:.3f}")
    return out


# ---------------------------------------------------------------- set-state noise margin at the working supply
def snm_job(args):
    corner, temp, v, k = args
    d, _ = bistable(corner, temp, v, k, (0, 0, 0, 0), f"cs_{corner}{temp}_{k}")
    return (corner, temp, v, k), set_snm(d, v)


def snm():
    jobs = [(co, t, v, k) for co, t in CORNERS for v in (4.5, 5.0) for k in range(cg.N)]
    with pool() as ex:
        r = dict(ex.map(snm_job, jobs))
    out = {}
    print("set-state noise margin (V)")
    for co, t in CORNERS:
        for v in (4.5, 5.0):
            s = [r[(co, t, v, k)] for k in range(cg.N)]
            out[f"{co}{t}_{v}"] = s
            print(f"{co} {t:>3} C VDDA {v} V: " + " ".join(f"{x:.3f}" for x in s))
    return out


# ---------------------------------------------------------------- transients
def canary_tran_lines(k, cset="cset", crdn="crdn"):
    """Canary k as drawn (gen/canary.py devices with the PDK models); nodes a, b, can."""
    s = cg.sizes(k)
    L = []
    for name, (d, g, src, b, typ, dev) in cg.devices("a", "b", "can", "midl", "midr", cset, crdn,
                                                    "vdd", "vdda", "0").items():
        L.append(c.mos(name, d, g, src, b, "pmos4" if typ == "p" else "nmos4", *s[dev]))
    L.append("Ccan can 0 100f")                       # wire to the control block
    return "\n".join(L)


def set_deck(corner, temp, v, k):
    return c.header(corner, temp) + f"""
VDD vdd 0 {v}
VDDA vdda 0 {v}
VSET cset 0 PWL(0 0 10n 0 10.5n {v} 110n {v} 110.5n 0)
VRD crdn 0 0
{canary_tran_lines(k)}
.ic v(a)=0 v(b)={v} v(can)={v}
.tran 0.05n 200n uic
.control
run
meas tran tset trig v(cset) val={v / 2} rise=1 targ v(a) val={v / 2} rise=1
meas tran tcan trig v(cset) val={v / 2} rise=1 targ v(can) val={v / 2} fall=1
meas tran aend find v(a) at=190n
meas tran bend find v(b) at=190n
meas tran canend find v(can) at=190n
echo "RES tset=$&tset"
echo "RES tcan=$&tcan"
echo "RES aend=$&aend"
echo "RES bend=$&bend"
echo "RES canend=$&canend"
.endc
.end
"""


def set_job(args):
    corner, temp, v, k = args
    return args, c.run(f"cset_{corner}{temp}_{v}_{k}", set_deck(corner, temp, v, k))


def set_():
    conds = [("TT", 27, 5.0), ("SS", 125, 4.5), ("FF", 0, 5.5), ("SF", 27, 5.0), ("FS", 27, 5.0), ("SS", 0, 4.5),
             ("FS", 125, 4.5)]
    with pool() as ex:
        r = dict(ex.map(set_job, [(co, t, v, k) for co, t, v in conds for k in range(cg.N)]))
    out = {}
    print("CSET pulse 100 ns: time from CSET to A = VDDA / 2 and to CAN = VDD / 2, end state")
    for co, t, v in conds:
        rows = [r[(co, t, v, k)] for k in range(cg.N)]
        out[f"{co}{t}_{v}"] = rows
        ok = all(isinstance(x.get("aend"), float) and x["aend"] > 0.9 * v and x["bend"] < 0.1 * v
                 and x["canend"] < 0.1 * v for x in rows)
        ts = [x.get("tset") for x in rows]
        print(f"{co} {t:>3} C {v} V: " + " ".join(f"{x * 1e9:.2f}" if isinstance(x, float) else "-" for x in ts)
              + f" ns  {'all set' if ok else 'NOT ALL SET'}")
    return out


T_HOLD = float(os.environ.get("T_HOLD", "10"))
T_RAMP = 1e-3


def hold_deck(k, v):
    ta, tb = 10e-6, 10e-6 + T_RAMP
    tc = tb + T_HOLD
    pwl = f"PWL(0 5 {ta:.6e} 5 {tb:.6e} {v} {tc:.6e} {v})"
    return c.header("TT", 27) + f"""
VDD vdd 0 5
VDDA vdda 0 {pwl}
VSET cset 0 0
VRD crdn 0 5
{canary_tran_lines(k)}
.ic v(a)=5 v(b)=0 v(can)=0
.tran 1u {tc:.6e} 0 {max(T_HOLD / 50000, 1e-6):.6e}
.control
run
let dab = v(a) - v(b)
meas tran tflip when dab=0 fall=1
meas tran ah find v(a) at={tc:.6e}
meas tran bh find v(b) at={tc:.6e}
echo "RES tflip=$&tflip"
echo "RES ah=$&ah"
echo "RES bh=$&bh"
.endc
.end
"""


def up_deck(k, v, a, b):
    ta, tb = 1e-6, 1e-6 + T_RAMP
    te = tb + 50e-6
    pwl = f"PWL(0 {v} {ta:.6e} {v} {tb:.6e} 5 {te:.6e} 5)"
    return c.header("TT", 27) + f"""
VDD vdd 0 5
VDDA vdda 0 {pwl}
VSET cset 0 0
VRD crdn 0 0
{canary_tran_lines(k)}
.ic v(a)={a:.6g} v(b)={b:.6g} v(can)=0
.tran 1n {te:.6e} 0 {T_RAMP / 2000:.6e}
.control
run
meas tran aend find v(a) at={te - 1e-6:.6e}
meas tran canend find v(can) at={te - 1e-6:.6e}
echo "RES aend=$&aend"
echo "RES canend=$&canend"
.endc
.end
"""


def hold_job(args):
    k, v = args
    tag = f"ch_{k}_{v:.3f}_{T_HOLD:g}s"
    h = c.run(tag + "_hold", hold_deck(k, v))
    if not all(isinstance(h.get(n), float) for n in ("ah", "bh")):
        raise RuntimeError(f"{tag}: hold run failed ({c.BUILD}/{tag}_hold.log)")
    u = c.run(tag + "_up", up_deck(k, v, h["ah"], h["bh"]))
    tf = h.get("tflip")
    tf = tf - (10e-6 + T_RAMP) if isinstance(tf, float) else None
    return args, dict(t_flip=tf, a_end=u["aend"], can=u["canend"], kept=u["aend"] > 2.5)


def hold():
    with pool() as ex:
        ref = dict(ex.map(drv_job, [("TT", 27, k, (0, 0, 0, 0), f"chr_{k}") for k in range(cg.N)]))
        jobs = []
        for k in range(cg.N):
            d = ref[f"chr_{k}"]
            jobs += [(k, round(d + 0.03, 3)), (k, round(d - 0.03, 3))]
        r = dict(ex.map(hold_job, jobs))
    out = {}
    print(f"TT 27 C: set at 5 V, VDDA ramps in 1 ms, held {T_HOLD:g} s, back to 5 V, read (CRD_N = 0)")
    for k in range(cg.N):
        d = ref[f"chr_{k}"]
        lines = []
        for v in (round(d + 0.03, 3), round(d - 0.03, 3)):
            x = r[(k, v)]
            out[f"C{k}_{v:.3f}"] = x
            tf = x["t_flip"]
            lines.append(f"{v:.3f} V: {'kept' if x['kept'] else 'lost'}"
                         + (f" (flip after {tf:.3g} s)" if isinstance(tf, float) and tf >= 0 else
                            " (flip on the ramp)" if isinstance(tf, float) else "") + f", CAN {x['can']:.2f} V")
        out[f"C{k}"] = d
        print(f"C{k} (retention voltage {d:.3f} V): " + "; ".join(lines))
    return out


def readout_deck(k, vdda, crdn, a_state):
    return c.header("TT", 27) + f"""
VDD vdd 0 5
VDDA vdda 0 {vdda}
VSET cset 0 0
VRD crdn 0 {crdn}
{canary_tran_lines(k)}
.nodeset v(a)={vdda if a_state else 0} v(b)={0 if a_state else vdda}
.op
.control
run
let ivdd = -i(VDD)
echo "RES a=$&v(a)"
echo "RES can=$&v(can)"
echo "RES ivdd=$&ivdd"
.endc
.end
"""


def readout():
    out = {}
    print("read-out gate of canary 0 (TT 27 C, VDD 5 V): CAN and VDD current")
    for vdda, crdn, st in ((5.0, 0, 1), (5.0, 0, 0), (5.0, 5, 1), (5.0, 5, 0), (1.4, 0, 1), (1.4, 5, 1), (2.5, 0, 1),
                           (2.5, 5, 1)):
        r = c.run(f"cro_{vdda}_{crdn}_{st}", readout_deck(0, vdda, crdn, st))
        out[f"{vdda}_{crdn}_{st}"] = r
        print(f"VDDA {vdda} V, CRD_N {crdn} V, A {'set' if st else 'lost'}: A = {r['a']:.3f} V, CAN = {r['can']:.3f} V,"
              f" I(VDD) = {r['ivdd'] * 1e6:.3f} uA")
    return out


if __name__ == "__main__":
    link_models()
    what = sys.argv[1] if len(sys.argv) > 1 else "ladder"
    fn = dict(ladder=ladder, mc=mc, snm=snm, set=set_, hold=hold, readout=readout)[what]
    res = fn()
    json.dump(res, open(os.path.join(c.BUILD, f"canary_{what}.json"), "w"), indent=1, default=str)
