set top_name "example"
set clock_name CLK
set T_clk 0.7

source ./scripts/head.tcl
remove_design -all -quiet
sh rm -f ./work/*.pvl ./work/*.mr ./work/*.syn

set path_results "./results"

############## read design files #################
set path_rtl /home/akobzev/Project_SystemVerilog/example/sv

analyze -format sverilog ${path_rtl}/example.sv
##################################################

############# resolve multiple instance###########
redirect -tee -file ${path_results}/log/${top_name}.elab {elaborate $top_name}
link 
# check_design
uniquify 
##################################################

############### setup enviroment #################
source ./scripts/setup_env.tcl
##################################################

############ setup timing constraints ############
create_clock ${clock_name} -period ${T_clk}
set_clock_uncertainty -setup 0.025 [get_clock ${clock_name}]
set_clock_uncertainty -hold  0.050 [get_clock ${clock_name}]

set_input_delay  [expr ${T_clk}*0.6] -clock [get_clocks ${clock_name}] [remove_from_collection [all_inputs] ${clock_name}]
set_output_delay [expr ${T_clk}*0.6] -clock [get_clocks ${clock_name}] [all_outputs]

set_max_transition 0.25 [current_design]
set_input_transition -max 0.15 [get_ports {CLK}]
set_input_transition -min 0.05 [get_ports {CLK}]
##################################################

############ setup area constraints ##############
set_max_area 0
##################################################

############### setup power opt ##################
set_dynamic_optimization true
set_leakage_optimization true
##################################################

################## compile #######################
set_host_options -max_cores 16
remove_unconnected_ports -blast_buses [get_cells * -hierarchical ]
set_fix_multiple_port_nets -all -buffer_constants
# _____________________________________________
# set compile_prefer_mux true
# set hdlin_infer_mux all
# set_size_only [get_cells -hier * -filter "@ref_name =~ *MUX_OP*"]
# _____________________________________________
compile_ultra -no_autoungroup -gate_clock
##################################################

#################### save ########################
report_qor > ${path_results}/log/${top_name}.qor
report_area -hier > ${path_results}/log/${top_name}.area
report_timing > ${path_results}/log/${top_name}.timing
report_power > ${path_results}/log/${top_name}.power
check_design > ${path_results}/log/${top_name}_check_design.log
change_names -rules verilog -hierarchy
write -hier -format verilog -output ${path_results}/netlist/${top_name}.v 
write_sdc ${path_results}/sdc/${top_name}.sdc
write_sdf ${path_results}/sdf/${top_name}.sdf
write -format ddc -hier -output ${path_results}/ddc/${top_name}.ddc
##################################################

# compile -incremental
# exit
