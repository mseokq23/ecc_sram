#!/usr/bin/env python3
"""Hold SNM and data-retention voltage (DRV) from split-inverter transfer curves (static, infinite-time answer).

For each sample the two half-cells (PU, PD, PG with bitline idle at VDDA, WWL = 0) are swept with a common input.
State existence uses the composite map F(Q) = fA(fB(Q)): with g = F(Q) - Q we always have g(0) >= 0 and
g(VDDA) <= 0, so the cell is bistable exactly when g goes from negative to positive somewhere inside.
Hold SNM = largest series noise vn (applied in the direction that attacks one state) that keeps the cell bistable,
minimum over the two states. DRV = VDDA where SNM reaches 0 (linear extrapolation between grid points).
Vt mismatch uses assumed Pelgrom coefficients (PDK has no mismatch model).
"""
import os, sys, json, math
import numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell8t as c

SZ = c.SZ

def deck(corner, temp, vdda, off, tag, npts=400, bl="idle"):
    """bl = "idle": both pass gates see a bit line at VDDA. bl = "worst": the write drivers hold BL = 0 next
    to half-cell a (Q) and BLB = VDDA next to half-cell b (QB), so both pass gates leak against Q = 1."""
    L = [c.header(corner, temp), f"VDDA vdda 0 {vdda}", f"VBL bl 0 {vdda}", "VIN x 0 0"]
    if bl == "worst":
        L.append("VBL0 bl0 0 0")
    for i, (pul, pdl, pgl, pur, pdr, pgr) in enumerate(off):
        for side, (dp, dn, dg) in (("a", (pul, pdl, pgl)), ("b", (pur, pdr, pgr))):
            o = f"o{side}{i}"
            line = "bl0" if (bl == "worst" and side == "a") else "bl"
            L += [f"Vp{side}{i} gp{side}{i} x {dp:.6f}", f"Vn{side}{i} gn{side}{i} x {-dn:.6f}",
                  f"Vg{side}{i} gg{side}{i} 0 {-dg:.6f}",
                  c.mos(f"pu{side}{i}", o, f"gp{side}{i}", "vdda", "vdda", "pmos4", *SZ["PU"]),
                  c.mos(f"pd{side}{i}", o, f"gn{side}{i}", 0, 0, "nmos4", *SZ["PD"]),
                  c.mos(f"pg{side}{i}", line, f"gg{side}{i}", o, 0, "nmos4", *SZ["PG"])]
    L.append(f".dc VIN 0 {vdda} {vdda / npts:.6e}")
    L.append(".control\nrun\nset wr_singlescale\nset wr_vecnames\n"
             f"wrdata vtc_{tag}.txt " + " ".join(f"v(oa{i}) v(ob{i})" for i in range(len(off))) + "\n.endc\n.end\n")
    return "\n".join(L)

def bistable(x, fa, fb, vdda, vn):
    q = np.linspace(0.0, vdda, 3001)
    qb = np.interp(q - vn, x, fb)           # noise lowers B's input  (attacks the Q-high state for vn > 0)
    F = np.interp(qb + vn, x, fa)           # and raises A's input
    g = F - q
    thr = 1e-7
    neg = np.where(g < -thr)[0]
    if len(neg) == 0:
        return False
    return bool((g[neg[0]:] > thr).any())

def snm(x, fa, fb, vdda):
    if not bistable(x, fa, fb, vdda, 0.0):
        return 0.0
    res = []
    for s in (+1, -1):
        lo, hi = 0.0, vdda / 2
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            if bistable(x, fa, fb, vdda, s * mid):
                lo = mid
            else:
                hi = mid
        res.append(lo)
    return min(res)

def point(args):
    corner, temp, vdda, off, tag = args
    t = f"{tag}_{vdda:.4f}"
    c.run(f"bf_{t}", deck(corner, temp, vdda, off, t))
    d = np.loadtxt(os.path.join(c.BUILD, f"vtc_{t}.txt"), skiprows=1)
    x = d[:, 0]
    n = len(off)
    cols = d[:, -2 * n:]                     # last 2n columns: oa0, ob0, oa1, ob1, ...
    return vdda, [snm(x, cols[:, 2 * i], cols[:, 2 * i + 1], vdda) for i in range(n)]

def drv_from(grid, S):
    """S: [len(grid), n] SNM. DRV per sample by linear extrapolation of the two lowest positive points."""
    out = []
    for i in range(S.shape[1]):
        s = S[:, i]
        pos = np.where(s > 0)[0]
        if len(pos) == 0:
            out.append(float("nan")); continue
        k = pos[0]
        if k + 1 < len(grid) and s[k + 1] > s[k]:
            v = grid[k] - s[k] * (grid[k + 1] - grid[k]) / (s[k + 1] - s[k])
            out.append(float(max(v, grid[k - 1] if k > 0 else grid[k] - 0.01)))
        else:
            out.append(float(grid[k]))
    return np.array(out)

def run_case(corner, temp, M, avt_n=12.0, avt_p=15.0, grid=None, seed=20261103):
    g0, g1, gs = (float(v) for v in os.environ.get("BF_GRID", "0.20,0.70,0.01").split(","))
    grid = np.round(np.arange(g0, g1 + gs / 2, gs), 4) if grid is None else grid
    sp = avt_p * 1e-3 / math.sqrt(SZ["PU"][0] * SZ["PU"][1])
    sn = avt_n * 1e-3 / math.sqrt(SZ["PD"][0] * SZ["PD"][1])
    sg = avt_n * 1e-3 / math.sqrt(SZ["PG"][0] * SZ["PG"][1])
    rng = np.random.default_rng(seed)
    off = np.column_stack([rng.normal(0, s, M) for s in (sp, sn, sg, sp, sn, sg)]) if M > 1 else np.zeros((1, 6))
    off[0, :] = 0.0
    tag = f"{corner}{temp}_M{M}_A{int(avt_n)}"
    jobs = [(corner, temp, float(v), off, tag) for v in grid]
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        pts = dict(ex.map(point, jobs))
    S = np.array([pts[float(v)] for v in grid])
    drv = drv_from(grid, S)
    snm5 = point((corner, temp, 5.0, off[:min(M, 50)], tag + "_5V"))[1]
    r = dict(corner=corner, temp=temp, M=M, avt=dict(n=avt_n, p=avt_p),
             sigma_mV=dict(PU=sp * 1e3, PD=sn * 1e3, PG=sg * 1e3),
             drv_nominal=float(drv[0]), snm5_nominal=float(snm5[0]), snm5_min=float(min(snm5)),
             snm_nominal_vs_vdda={f"{v:.2f}": float(S[j, 0]) for j, v in enumerate(grid)})
    if M > 1:
        r.update(drv_mean=float(np.nanmean(drv)), drv_std=float(np.nanstd(drv)),
                 drv_p1=float(np.nanpercentile(drv, 1)), drv_p99=float(np.nanpercentile(drv, 99)),
                 drv_min=float(np.nanmin(drv)), drv_max=float(np.nanmax(drv)), drv_all=drv.round(4).tolist())
    return r

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "nominal"
    out = {}
    if which == "nominal":
        for k, t in (("TT", 27), ("TT", 125), ("TT", 0), ("SS", 27), ("FF", 27), ("SF", 27), ("FS", 27)):
            out[f"{k}{t}"] = run_case(k, t, 1)
            print(k, t, "DRV", round(out[f"{k}{t}"]["drv_nominal"], 4), "SNM5", round(out[f"{k}{t}"]["snm5_nominal"], 3), flush=True)
    else:
        k, t, M, an, ap = which.split(",")
        out[which] = run_case(k, int(t), int(M), float(an), float(ap))
        r = out[which]
        print({kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in r.items() if kk not in ("drv_all", "snm_nominal_vs_vdda")})
    json.dump(out, open(os.path.join(c.BUILD, f"bf_{which.replace(',', '_')}.json"), "w"), indent=1)
