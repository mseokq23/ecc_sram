#!/usr/bin/env python3
"""Vt-mismatch spread of the retention voltage: one half-cell pair per netlist (avoids solver coupling between
samples in a large DC sweep), bisection on VDDA with the bistability test of drv_butterfly.py.
usage: python3 drv_mc_small.py <corner> <temp> <M> <A_VT,n mV.um> <A_VT,p mV.um>
"""
import os, sys, json, math
import numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell8t as c
import drv_butterfly as bf

def one(args):
    """(corner, temp, idx, offsets[, bit lines "idle" | "worst"]) -> (idx, retention voltage or None)"""
    corner, temp, idx, off, *rest = args
    bl = rest[0] if rest else "idle"
    def ok(v):
        tag = f"mcs_{corner}{temp}_{bl}_{idx}_{v:.5f}"
        c.run(tag, bf.deck(corner, temp, v, [off], tag, bl=bl))
        d = np.loadtxt(os.path.join(c.BUILD, f"vtc_{tag}.txt"), skiprows=1)
        return bf.bistable(d[:, 0], d[:, -2], d[:, -1], v, 0.0)
    lo, hi = 0.15, 0.80
    if not ok(hi):
        return idx, None
    for _ in range(10):                      # ~0.6 mV
        mid = 0.5 * (lo + hi)
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return idx, hi

def main():
    corner, temp, M, an, ap = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
    sz = c.SZ
    sp = ap * 1e-3 / math.sqrt(sz["PU"][0] * sz["PU"][1])
    sn = an * 1e-3 / math.sqrt(sz["PD"][0] * sz["PD"][1])
    sg = an * 1e-3 / math.sqrt(sz["PG"][0] * sz["PG"][1])
    rng = np.random.default_rng(20261103)
    off = np.column_stack([rng.normal(0, s, M) for s in (sp, sn, sg, sp, sn, sg)])
    off[0, :] = 0.0
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        res = dict(ex.map(one, [(corner, temp, i, off[i].tolist()) for i in range(M)]))
    drv = np.array([res[i] if res[i] is not None else np.nan for i in range(M)])
    out = dict(corner=corner, temp=temp, M=M, avt=dict(n=an, p=ap), sigma_mV=dict(PU=sp * 1e3, PD=sn * 1e3, PG=sg * 1e3),
               drv_nominal=float(drv[0]), drv_mean=float(np.nanmean(drv)), drv_std=float(np.nanstd(drv)),
               drv_p1=float(np.nanpercentile(drv, 1)), drv_p99=float(np.nanpercentile(drv, 99)),
               drv_min=float(np.nanmin(drv)), drv_max=float(np.nanmax(drv)), drv_all=drv.round(4).tolist())
    json.dump(out, open(os.path.join(c.BUILD, f"mcs_{corner}{temp}_A{int(an)}.json"), "w"), indent=1)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items() if k != "drv_all"})

if __name__ == "__main__":
    main()
