############################################################
# STAND
TOP_DESIGN_SV  := example_sv
TEST_DESIGN_PY := example_py
############################################################

export PYTHONPATH = $(shell pwd)/py:$PYTHONPATH

SIM = xcelium
TOPLEVEL_LANG = verilog

TOPLEVEL = $(TOP_DESIGN_SV)
MODULE = $(TEST_DESIGN_PY)

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

SIM_ARGS = -f sv/LIST_MODULES.f 
# SIM_ARGS += -gui 
WAVE = 1
ifeq ($(WAVE),1)
	SIM_ARGS += -input scripts/xrun_write_shm.tcl
endif

simp = 0
ifeq ($(simp),1)
	include $(shell cocotb-config --makefiles)/Makefile.sim
endif

scripts_main = main

sime:
	mkdir -p sim_build
	xrun -f sv/LIST_MODULES.f -elaborate -xmlibdirpath sim_build

view: 
	simvision waves.shm

syn:
	dcnxt_shell -f scripts/$(scripts_main).tcl | tee -i results/log/syn_log.log

cleanf:
	rm -rf waves.shm .simvision simvision*.diag xcelium.d sim_build work .bpad alib-52 .idea
	rm -f *.log *.so *.o *.tmp *.key *.err *.*dat *.png *.history *.xml *.out *.svf *.b