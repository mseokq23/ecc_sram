# Control block ecc_fi_ctrl and decoder block ecc_dec: RTL simulation, synthesis with the kit liberty,
# gate-level simulation, place and route, frozen macros. tb/core_logic.v wires the two blocks as the chip
# does (the read word R and VIEW, V_DIR, HALF over the top channel), with the ports of the former single
# control block, so one chip-core testbench (tb/tb_core.v) covers both.
#   make sim          RTL of both blocks + tb/tb_core.v (Icarus Verilog)
#   make dec_sim      ecc_dec alone, all 2^11 inputs against models without its structure (tb/tb_dec.v)
#   make synth        Yosys with the kit liberty (without XOR2X1, XNOR2X1, FAX1, HAX1, LATCH, TBUFX*:
#                     their metal2 is 0.93-0.95 um apart inside the cell, the rule is 1.0 um), both blocks
#                     -> build/ecc_fi_ctrl_syn.v, build/ecc_dec_syn.v, cell counts and LEF areas
#   make gatesim      tb_core.v and tb_dec.v on the synthesized netlists with the kit cell models
#   make flow         place and route ecc_fi_ctrl with qflow (run_flow.sh); make dec_flow: ecc_dec
#   make qflowsim     both testbenches on the netlists qflow synthesized (build/qflow*/synthesis)
#   make macrosim     both testbenches on the frozen macros' gate netlists (macro/*.v, what the chip uses)
#   make mutants      14 wrong versions of the RTL must all fail tb_core.v (mutants.py)
REPO  := $(abspath ../../..)
B     := build
KIT   ?= $(firstword $(wildcard $(REPO)/.pdk/ETRI050_DesignKit) $(wildcard $(HOME)/ETRI050_DesignKit))
LIB   := $(KIT)/digital_ETRI/khu_etri05_stdcells.lib
LEF   := $(KIT)/digital_ETRI/etri050_stdcells.lef
CELLV := $(KIT)/digital_ETRI/khu_etri05_stdcells.v
YOSYS ?= yosys
NOX   := $(B)/nox.lib
CORE  := tb/tb_core.v tb/core_logic.v
SYN    = synth -top $(1) -flatten; dfflibmap -liberty $(NOX); abc -liberty $(NOX); opt_clean; stat -liberty $(NOX)

.PHONY: all sim dec_sim synth gatesim flow dec_flow qflowsim macrosim mutants proposal clean check-kit
all: sim dec_sim synth gatesim proposal

check-kit:
	@test -f "$(LIB)" || { echo "ETRI kit not found (KIT=$(KIT)); run scripts/setup-etri050.sh"; exit 1; }

sim: | $(B)
	iverilog -g2005 -o $(B)/tb_rtl.vvp $(CORE) ecc_fi_ctrl/ecc_fi_ctrl.v ecc_dec/ecc_dec.v
	vvp -n $(B)/tb_rtl.vvp | tee $(B)/sim_rtl.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_rtl.log

dec_sim: | $(B)
	iverilog -g2005 -o $(B)/tb_dec_rtl.vvp tb/tb_dec.v ecc_dec/ecc_dec.v
	vvp -n $(B)/tb_dec_rtl.vvp | tee $(B)/sim_dec_rtl.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_dec_rtl.log

$(NOX): check-kit | $(B)
	python3 make_nox_lib.py $(LIB) $(NOX)

synth: $(NOX)
	$(YOSYS) -q -l $(B)/synth.log -p "read_verilog ecc_fi_ctrl/ecc_fi_ctrl.v; $(call SYN,ecc_fi_ctrl); write_verilog -noattr $(B)/ecc_fi_ctrl_syn.v"
	$(YOSYS) -q -l $(B)/synth_dec.log -p "read_verilog ecc_dec/ecc_dec.v; $(call SYN,ecc_dec); write_verilog -noattr $(B)/ecc_dec_syn.v"
	python3 cell_area.py $(B)/ecc_fi_ctrl_syn.v $(LEF) ecc_fi_ctrl | tee $(B)/area.txt
	python3 cell_area.py $(B)/ecc_dec_syn.v $(LEF) ecc_dec | tee $(B)/area_dec.txt

gatesim: synth
	iverilog -g2005 -Ttyp -o $(B)/tb_gate.vvp $(CORE) $(B)/ecc_fi_ctrl_syn.v $(B)/ecc_dec_syn.v $(CELLV)
	vvp -n $(B)/tb_gate.vvp | tee $(B)/sim_gate.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_gate.log
	iverilog -g2005 -Ttyp -o $(B)/tb_dec_gate.vvp tb/tb_dec.v $(B)/ecc_dec_syn.v $(CELLV)
	vvp -n $(B)/tb_dec_gate.vvp | tee $(B)/sim_dec_gate.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_dec_gate.log

flow: check-kit
	bash run_flow.sh

dec_flow: check-kit
	TOP=ecc_dec bash run_flow.sh

qflowsim: check-kit
	python3 strip_port_wires.py $(B)/qflow/synthesis/ecc_fi_ctrl.rtlnopwr.v $(B)/ecc_fi_ctrl_qflow.v
	python3 strip_port_wires.py $(B)/qflow_ecc_dec/synthesis/ecc_dec.rtlnopwr.v $(B)/ecc_dec_qflow.v
	iverilog -g2005 -Ttyp -o $(B)/tb_qflow.vvp $(CORE) $(B)/ecc_fi_ctrl_qflow.v $(B)/ecc_dec_qflow.v $(CELLV)
	vvp -n $(B)/tb_qflow.vvp | tee $(B)/sim_qflow.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_qflow.log
	iverilog -g2005 -Ttyp -o $(B)/tb_dec_qflow.vvp tb/tb_dec.v $(B)/ecc_dec_qflow.v $(CELLV)
	vvp -n $(B)/tb_dec_qflow.vvp | tee $(B)/sim_dec_qflow.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_dec_qflow.log

macrosim: check-kit | $(B)
	python3 strip_port_wires.py macro/ecc_fi_ctrl.v $(B)/ecc_fi_ctrl_macro.v
	python3 strip_port_wires.py macro/ecc_dec.v $(B)/ecc_dec_macro.v
	iverilog -g2005 -Ttyp -o $(B)/tb_macro.vvp $(CORE) $(B)/ecc_fi_ctrl_macro.v $(B)/ecc_dec_macro.v $(CELLV)
	vvp -n $(B)/tb_macro.vvp | tee $(B)/sim_macro.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_macro.log
	iverilog -g2005 -Ttyp -o $(B)/tb_dec_macro.vvp tb/tb_dec.v $(B)/ecc_dec_macro.v $(CELLV)
	vvp -n $(B)/tb_dec_macro.vvp | tee $(B)/sim_dec_macro.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_dec_macro.log

mutants: | $(B)
	python3 mutants.py

# the first proposal's RTL (8 words) against an independent Hamming model: 36,864 reads
proposal: | $(B)
	iverilog -g2005 -o $(B)/tb_proposal.vvp proposal/tb_fault_injection_ecc.v proposal/fault_injection_ecc_sram_top.v
	vvp -n $(B)/tb_proposal.vvp | tee $(B)/sim_proposal.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_proposal.log

$(B):
	mkdir -p $@

clean:
	rm -rf $(B)
