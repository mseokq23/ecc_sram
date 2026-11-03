#!/usr/bin/env python3
"""Corner sweeps: write delay, write trip, read-0 delay, read-1 hold (keeper / no keeper), injected-current flip."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell8t as c

CORNERS = ["TT", "SS", "FF", "SF", "FS"]
TEMPS = [0, 27, 125]
VDDS = [4.5, 5.0, 5.5]
out = {}

# 1) write delay and final state, all corners
jobs = [("write", f"w_{k}_{t}_{v}", dict(corner=k, temp=t, vdd=v)) for k in CORNERS for t in TEMPS for v in VDDS]
res = c.pmap(jobs)
ok = [r for _, kw, r in res if r.get("qend", 9) < 0.1 * kw["vdd"] and r.get("qbend", 0) > 0.9 * kw["vdd"]]
tw = [(r["tw"], kw) for _, kw, r in res if isinstance(r.get("tw"), float)]
out["write"] = dict(n=len(res), n_ok=len(ok), tw_max_ns=max(tw)[0] * 1e9, tw_max_at=max(tw)[1],
                    tw_min_ns=min(tw)[0] * 1e9)

# 2) write trip (BL level that flips the cell with BLB at VDD), all corners at 4.5 V
jobs = [("wtrip", f"wt_{k}_{t}", dict(corner=k, temp=t, vdd=4.5)) for k in CORNERS for t in TEMPS]
res = c.pmap(jobs)
vt = [(r.get("vbl_trip", float("nan")), kw["corner"], kw["temp"]) for _, kw, r in res]
out["write_trip_4p5V"] = dict(min_V=min(vt), max_V=max(vt), all=vt)

# 3) read 0: delay and final RBL, all corners/temps/VDD, 200 ns evaluation
jobs = [("read", f"r0_{k}_{t}_{v}", dict(corner=k, temp=t, vdd=v, data=0, t_eval=200e-9))
        for k in CORNERS for t in TEMPS for v in VDDS]
res = c.pmap(jobs)
tr = [(r["tread"], kw["corner"], kw["temp"], kw["vdd"]) for _, kw, r in res if isinstance(r.get("tread"), float)]
disturb = max(abs(r.get("qmin", 0)) for _, kw, r in res)
out["read0"] = dict(n=len(res), n_ok=len(tr), tread_max_ns=max(tr)[0] * 1e9, worst=max(tr)[1:],
                    tread_min_ns=min(tr)[0] * 1e9, q_disturb_max_V=disturb)

# 4) read 1 with 15 leaky cells: keeper vs no keeper, long evaluation at hot/fast corners
jobs = []
for k in ["FF", "FS", "TT"]:
    for keep in (True, False):
        for te in (1e-6, 100e-6):
            jobs.append(("read", f"r1_{k}_{keep}_{te}", dict(corner=k, temp=125, vdd=5.5, data=1, t_eval=te, keeper=keep)))
res = c.pmap(jobs)
out["read1_125C_5p5V"] = [dict(corner=kw["corner"], keeper=kw["keeper"], t_eval_us=kw["t_eval"] * 1e6,
                               vrbl_end=r.get("vrbl_end"), saout_end=r.get("vsa_end")) for _, kw, r in res]

json.dump(out, open(os.path.join(c.BUILD, "basic_summary.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
