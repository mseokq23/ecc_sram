#!/usr/bin/env python3
"""Array-supply experiments: read Vmin (VDDA) vs evaluation time and keeper, the injected current that flips a
cell, and the write Vmin of the bit line drivers' supply VDDW."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell8t as c

out = {}

def read_ok(corner, temp, vdda, t_eval, keeper, sz):
    r = c.run(f"rv_{corner}_{temp}_{vdda:.4f}_{t_eval:.0e}_{keeper}_{sz['KEEP'][1]}",
              c.read_deck(corner, temp, 5.0, 0, vdda=vdda, t_eval=t_eval, keeper=keeper, sz=sz))
    return r.get("vsa_end", 0) > 2.5

def vmin_job(args):
    corner, temp, t_eval, keeper, keepL = args
    sz = dict(c.SZ); sz["KEEP"] = (1.8, keepL)
    lo, hi = 0.3, 3.0
    if not read_ok(corner, temp, hi, t_eval, keeper, sz):
        return args, None
    for _ in range(9):
        mid = 0.5 * (lo + hi)
        if read_ok(corner, temp, mid, t_eval, keeper, sz):
            hi = mid
        else:
            lo = mid
    return args, hi

from concurrent.futures import ProcessPoolExecutor
cases = [(k, t, te, True, 1.8) for k in ("TT", "SS", "FF") for t in (27, 125) for te in (100e-9, 1e-6, 10e-6)]
cases += [("TT", 27, te, True, 3.6) for te in (100e-9, 1e-6, 10e-6)]       # weaker keeper (L 3.6 um)
cases += [("TT", 27, te, False, 1.8) for te in (100e-9, 1e-6, 10e-6)]      # no keeper
with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
    res = list(ex.map(vmin_job, cases))
out["read_vmin"] = [dict(corner=a[0], temp=a[1], t_eval_ns=a[2] * 1e9, keeper=a[3], keeper_L=a[4],
                         vdda_min=round(v, 3) if v else None) for a, v in res]

# injected current needed to flip a cell vs VDDA (TT 27 C); 'down' = pull a stored 1 low (n+ junctions collect)
def ic_job(args):
    vdda, direction = args
    imax = {5.0: 2e-3, 3.0: 1e-3, 2.0: 5e-4, 1.5: 2e-4, 1.0: 5e-5, 0.8: 2e-5, 0.6: 5e-6, 0.5: 2e-6,
            0.4: 5e-7, 0.3: 2e-7}[vdda]
    for _ in range(4):
        r = c.run(f"ic_{vdda}_{direction}", c.icrit_deck("TT", 27, vdda, direction, imax))
        if isinstance(r.get("icrit"), float) and r["icrit"] < 0.95 * imax:
            return args, r["icrit"]
        imax *= 4
    return args, None

with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
    res = list(ex.map(ic_job, [(v, d) for v in (5.0, 3.0, 2.0, 1.5, 1.0, 0.8, 0.6, 0.5, 0.4, 0.3) for d in ("down", "up")]))
out["icrit_TT27"] = [dict(vdda=a[0], direction=a[1], icrit_A=v) for a, v in res]

# write Vmin of the driver supply VDDW: lowest VDDW that still writes 0 into a cell holding 1 (VDD = VDDA = 5 V)
def write_ok(corner, temp, vddw):
    r = c.run(f"wv_{corner}_{temp}_{vddw:.4f}", c.write_deck(corner, temp, 5.0, vdda=5.0, vddw=vddw))
    return r.get("qend", 9) < 0.5 and r.get("qbend", 0) > 4.5

def wvmin_job(args):
    corner, temp = args
    lo, hi = 0.2, 5.0
    if not write_ok(corner, temp, hi):
        return args, None
    for _ in range(10):
        mid = 0.5 * (lo + hi)
        if write_ok(corner, temp, mid):
            hi = mid
        else:
            lo = mid
    return args, hi

with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
    res = list(ex.map(wvmin_job, [(k, t) for k in ("TT", "SS", "FF", "SF", "FS") for t in (0, 27, 125)]))
out["write_vmin_vddw"] = [dict(corner=a[0], temp=a[1], vddw_min=round(v, 3) if v else None) for a, v in res]

json.dump(out, open(os.path.join(c.BUILD, "vdda_summary.json"), "w"), indent=1)
for row in out["read_vmin"]:
    print(row)
for row in out["icrit_TT27"]:
    print(row)
for row in out["write_vmin_vddw"]:
    print(row)
