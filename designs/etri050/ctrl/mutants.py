#!/usr/bin/env python3
"""Does the control block's testbench see the monitor views? Nine wrong versions of the RTL, each with one
mistake in the canary or ring-oscillator views, must all fail tb/tb_ecc_fi_ctrl.v.

  python3 designs/etri050/ctrl/mutants.py        (or make -C designs/etri050/ctrl mutants)

Each mutant is ecc_fi_ctrl/ecc_fi_ctrl.v with one line changed (MUTANTS below); results in build/mut/.
Exit 0 when every mutant is caught (TB RESULT: FAIL).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RTL = HERE / "ecc_fi_ctrl/ecc_fi_ctrl.v"
TB = HERE / "tb/tb_ecc_fi_ctrl.v"
OUT = HERE / "build/mut"

EN = "assign RO_EN = {v_ro & (DIN[1:0] == 2'b10), v_ro & (DIN[1:0] == 2'b01), v_ro & (DIN[1:0] == 2'b00)};"
CANV = "wire [3:0] canv = FI_POS[0] ? CAN[7:4] : CAN[3:0];"
MUTANTS = {   # name: (what is wrong, original text, replacement)
    "crd_inverted": ("CRD_N inverted", "assign CRD_N = ~(v_can | v_set);", "assign CRD_N = (v_can | v_set);"),
    "cset_no_clk": ("CSET without CLK", "assign CSET = CLK & v_set;", "assign CSET = v_set;"),
    "set_in_view": ("CSET also in the canary view", "assign CSET = CLK & v_set;", "assign CSET = CLK & (v_set | v_can);"),
    "halves_swapped": ("canary halves swapped", CANV, "wire [3:0] canv = FI_POS[0] ? CAN[3:0] : CAN[7:4];"),
    "can_inverted": ("canary bits inverted", CANV, "wire [3:0] canv = ~(FI_POS[0] ? CAN[7:4] : CAN[3:0]);"),
    "pos21_ignored": ("FI_POS[2:1] ignored (raw view only)",
                      "wire v_can = v_mon & (FI_POS[2:1] == 2'b01);\n    wire v_set = v_mon & (FI_POS[2:1] == 2'b10);\n"
                      "    wire v_ro  = v_mon & (FI_POS[2:1] == 2'b11);",
                      "wire v_can = 1'b0;\n    wire v_set = 1'b0;\n    wire v_ro  = 1'b0;"),
    "ro_en_any_view": ("RO_EN outside the RO view", EN, EN.replace("v_ro &", "view &")),
    "ring_select_swapped": ("NAND and NOR enables swapped", EN,
                            "assign RO_EN = {v_ro & (DIN[1:0] == 2'b01), v_ro & (DIN[1:0] == 2'b10), v_ro & (DIN[1:0] == 2'b00)};"),
    "rodiv_inverted": ("RO_DIV inverted on DOUT0", "{3'b000, RO_DIV}", "{3'b000, ~RO_DIV}"),
}


def main() -> int:
    src = RTL.read_text()
    OUT.mkdir(parents=True, exist_ok=True)
    caught = 0
    for name, (what, a, b) in MUTANTS.items():
        if src.count(a) != 1:
            sys.exit(f"{name}: the text to change is not in {RTL.name} exactly once")
        v = OUT / f"{name}.v"
        v.write_text(src.replace(a, b))
        vvp = OUT / f"{name}.vvp"
        subprocess.run(["iverilog", "-g2005", "-o", str(vvp), str(TB), str(v)], check=True)
        p = subprocess.run(["vvp", "-n", str(vvp)], capture_output=True, text=True, timeout=1800)
        (OUT / f"{name}.log").write_text(p.stdout + p.stderr)
        m = re.search(r"TB RESULT: (\w+)", p.stdout)
        line = next((l for l in p.stdout.splitlines() if l.startswith("checks=")), "")
        e = re.findall(r"\berrors=(\d+)", line)                  # the last one: all errors
        ok = bool(m) and m[1] == "FAIL"
        caught += ok
        print(f"{name:20s} {what:38s} {'caught' if ok else 'NOT CAUGHT'}" + (f" ({int(e[-1]):,} errors)" if e else ""))
    print(f"mutants: {caught} of {len(MUTANTS)} caught")
    return 0 if caught == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
