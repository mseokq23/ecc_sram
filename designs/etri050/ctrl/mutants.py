#!/usr/bin/env python3
"""Wrong versions of the control block and the decoder block: each must fail tb/tb_core.v.

Each mutant is one small change of the RTL (a missing condition, a swapped half, a wrong bit); the run
stops at the first few mismatches (FASTFAIL) and uses 20,000 random operations instead of 100,000.

usage: python3 mutants.py   (from designs/etri050/ctrl; work files in build/mut)
"""
import subprocess, pathlib, sys
from concurrent.futures import ThreadPoolExecutor
D = pathlib.Path(__file__).resolve().parent
CTRL = (D / 'ecc_fi_ctrl/ecc_fi_ctrl.v').read_text(); DEC = (D / 'ecc_dec/ecc_dec.v').read_text()
M = [
 ('dec', 'single bad bit taken without the direction', "wire       z1 = Q & |(sd & u);", "wire       z1 = Q;"),
 ('dec', 'direction reversed', "wire [7:0] u  = HALF ? R : ~R;", "wire [7:0] u  = HALF ? ~R : R;"),
 ('dec', 'two-bit rule without the direction', "wire       z2   = (popc(u) == 4'd2);", "wire       z2   = (popc(R) == 4'd2);"),
 ('dec', 'two corrected bits shown as detected', "assign SEC_FLAG = V_DIR ? (z1 | z2) : Q;", "assign SEC_FLAG = V_DIR ? z1 : Q;"),
 ('dec', 'two corrected bits not flagged', "assign DED_FLAG = V_DIR ? (z2 | zbad)", "assign DED_FLAG = V_DIR ? (zbad)"),
 ('dec', 'detection misses even errors', "wire       zbad = (Q | (S != 3'd0)) & ~z1 & ~z2;", "wire       zbad = Q & ~z1 & ~z2;"),
 ('dec', 'two-bit rule on three bits', "wire       z2   = (popc(u) == 4'd2);", "wire       z2   = (popc(u) == 4'd3);"),
 ('dec', 'two-bit correction flips S', "wire [7:0] fix  = ({8{z1}} & sd) | ({8{z2}} & u);", "wire [7:0] fix  = ({8{z1 | z2}} & sd);"),
 ('dec', 'raw halves swapped', "wire [3:0] raw  = HALF ? {R[7], R[6], R[5], R[3]} : {R[4], R[2], R[1], R[0]};", "wire [3:0] raw  = HALF ? {R[4], R[2], R[1], R[0]} : {R[7], R[6], R[5], R[3]};"),
 ('dec', 'standard correction misses D0', "R[5] ^ (Q & (S == 3'd5)), R[3] ^ (Q & (S == 3'd3))};", "R[5] ^ (Q & (S == 3'd5)), R[3]};"),
 ('ctrl', 'DIN flip without DIN[3]', ": (V_DIR & DIN[3]) ? (8'd1 << DIN[2:0]) : 8'd0;", ": V_DIR ? (8'd1 << DIN[2:0]) : 8'd0;"),
 ('ctrl', 'DIN flip outside the direction view', ": (V_DIR & DIN[3]) ? (8'd1 << DIN[2:0]) : 8'd0;", ": (view & DIN[3]) ? (8'd1 << DIN[2:0]) : 8'd0;"),
 ('ctrl', 'HALF from the wrong bit', "assign HALF  = FI_POS[0];", "assign HALF  = FI_POS[1];"),
 ('ctrl', 'direction view on the wrong code', "assign V_DIR = ~WE & view & (FI_POS[2:1] == 2'b01);", "assign V_DIR = ~WE & view & (FI_POS[2:1] == 2'b10);"),
]
W = D / 'build/mut'; W.mkdir(parents=True, exist_ok=True)
def run(i):
    blk, name, a, b = M[i]
    src = CTRL if blk == 'ctrl' else DEC
    if a not in src: return i, name, 'pattern not found'
    f = W / f'{blk}_{i}.v'; f.write_text(src.replace(a, b, 1))
    other = D / ('ecc_dec/ecc_dec.v' if blk == 'ctrl' else 'ecc_fi_ctrl/ecc_fi_ctrl.v')
    vvp = W / f'm{i}.vvp'
    subprocess.run(['iverilog', '-g2005', '-Ptb.NRAND=20000', '-DFASTFAIL', '-o', str(vvp), str(D / 'tb/tb_core.v'),
                    str(D / 'tb/core_logic.v'), str(f), str(other)], check=True, capture_output=True)
    out = subprocess.run(['vvp', '-n', str(vvp)], capture_output=True, text=True).stdout
    return i, name, 'caught' if 'TB RESULT: FAIL' in out else 'NOT CAUGHT'
with ThreadPoolExecutor(2) as ex:
    res = sorted(ex.map(run, range(len(M))))
for i, name, st in res: print(f'{i:2d} {M[i][0]:4s} {name:40s} {st}')
n = sum(st == 'caught' for _, _, st in res); print(f'caught {n} of {len(M)}'); sys.exit(0 if n == len(M) else 1)
