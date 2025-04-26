############################################################
# STAND
TOP_DESIGN_SV  := testbench_ez
TEST_DESIGN_PY := PICORV_CCTB
VERILOG_SOURCES = $(shell cat sv/LIST_MODULES.f)
############################################################

export PYTHONPATH = $(shell pwd)/py:$PYTHONPATH

SIM = verilator
TOPLEVEL_LANG = verilog

TOPLEVEL = $(TOP_DESIGN_SV)
MODULE = $(TEST_DESIGN_PY)

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

EXTRA_ARGS += --timing
EXTRA_ARGS += -Wall --Wno-fatal
WAVE = 0
ifeq ($(WAVE),1)
	EXTRA_ARGS += --trace --trace-structs
endif

simp = 0
ifeq ($(simp),1)
	include $(shell cocotb-config --makefiles)/Makefile.sim
endif

scripts_main = main

sime:
	mkdir -p sim_builds
	verilator -cc $(shell cat sv/LIST_MODULES.f) \
	  --top-module $(TOP_DESIGN_SV) \
	  --Mdir sim_build \
	  --trace --trace-structs\
	  --timing \
	  -Wall --Wno-fatal



view:
	make -C sim_build -f Vtestbench_ez.mk Vtestbench_ez
	./sim_build/Vtestbench_ez
	gtkwave /home/vm-admin/TMP/COCOTB/TemplateProject/DUMP.vcd


syn:
	dcnxt_shell -f scripts/$(scripts_main).tcl | tee -i results/log/syn_log.log

cleanf:
	rm -rf waves.shm .simvision simvision*.diag xcelium.d sim_build work .bpad alib-52 .idea
	rm -f *.log *.so *.o *.tmp *.key *.err *.*dat *.png *.history *.xml *.out *.svf *.b *.vcd