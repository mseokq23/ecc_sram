# Control block ecc_fi_ctrl: RTL simulation, synthesis with the kit liberty, gate-level simulation
#   make sim       RTL + self-checking testbench (Icarus Verilog)
#   make synth     Yosys with the kit liberty (without XOR2X1, XNOR2X1, FAX1, HAX1, LATCH, TBUFX*:
#                  their metal2 is 0.93-0.95 um apart inside the cell, the rule is 1.0 um)
#                  -> build/ecc_fi_ctrl_syn.v, cell count and LEF area
#   make gatesim   the same testbench on the synthesized netlist with the kit cell models
#   make flow      place and route with qflow (run_flow.sh)
#   make qflowsim  the testbench on the netlist qflow synthesized (build/qflow/synthesis)
#   make macrosim  the testbench on the frozen macro's gate netlist (macro/ecc_fi_ctrl.v, what the chip uses)
REPO  := $(abspath ../../..)
B     := build
KIT   ?= $(firstword $(wildcard $(REPO)/.pdk/ETRI050_DesignKit) $(wildcard $(HOME)/ETRI050_DesignKit))
LIB   := $(KIT)/digital_ETRI/khu_etri05_stdcells.lib
LEF   := $(KIT)/digital_ETRI/etri050_stdcells.lef
CELLV := $(KIT)/digital_ETRI/khu_etri05_stdcells.v
YOSYS ?= yosys
TOP   := ecc_fi_ctrl
NOX   := $(B)/nox.lib

.PHONY: all sim synth gatesim flow qflowsim macrosim proposal clean check-kit
all: sim synth gatesim proposal

check-kit:
	@test -f "$(LIB)" || { echo "ETRI kit not found (KIT=$(KIT)); run scripts/setup-etri050.sh"; exit 1; }

sim: | $(B)
	iverilog -g2005 -o $(B)/tb_rtl.vvp tb/tb_$(TOP).v $(TOP)/$(TOP).v
	vvp -n $(B)/tb_rtl.vvp | tee $(B)/sim_rtl.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_rtl.log

$(NOX): check-kit | $(B)
	python3 make_nox_lib.py $(LIB) $(NOX)

synth: $(NOX)
	$(YOSYS) -q -l $(B)/synth.log -p "read_verilog $(TOP)/$(TOP).v; synth -top $(TOP) -flatten; dfflibmap -liberty $(NOX); abc -liberty $(NOX); opt_clean; stat -liberty $(NOX); write_verilog -noattr $(B)/$(TOP)_syn.v"
	python3 cell_area.py $(B)/$(TOP)_syn.v $(LEF) $(TOP) | tee $(B)/area.txt

gatesim: synth
	iverilog -g2005 -Ttyp -o $(B)/tb_gate.vvp tb/tb_$(TOP).v $(B)/$(TOP)_syn.v $(CELLV)
	vvp -n $(B)/tb_gate.vvp | tee $(B)/sim_gate.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_gate.log

flow: check-kit
	bash run_flow.sh

qflowsim: check-kit
	python3 strip_port_wires.py $(B)/qflow/synthesis/$(TOP).rtlnopwr.v $(B)/$(TOP)_qflow.v
	iverilog -g2005 -Ttyp -o $(B)/tb_qflow.vvp tb/tb_$(TOP).v $(B)/$(TOP)_qflow.v $(CELLV)
	vvp -n $(B)/tb_qflow.vvp | tee $(B)/sim_qflow.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_qflow.log

macrosim: check-kit | $(B)
	python3 strip_port_wires.py macro/$(TOP).v $(B)/$(TOP)_macro.v
	iverilog -g2005 -Ttyp -o $(B)/tb_macro.vvp tb/tb_$(TOP).v $(B)/$(TOP)_macro.v $(CELLV)
	vvp -n $(B)/tb_macro.vvp | tee $(B)/sim_macro.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_macro.log

# the first proposal's RTL (8 words) against an independent Hamming model: 36,864 reads
proposal: | $(B)
	iverilog -g2005 -o $(B)/tb_proposal.vvp proposal/tb_fault_injection_ecc.v proposal/fault_injection_ecc_sram_top.v
	vvp -n $(B)/tb_proposal.vvp | tee $(B)/sim_proposal.log
	@grep -q 'TB RESULT: PASS' $(B)/sim_proposal.log

$(B):
	mkdir -p $@

clean:
	rm -rf $(B)
