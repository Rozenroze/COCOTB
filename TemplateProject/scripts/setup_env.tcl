# set_operating_conditions ssg0p81vm40c
set operating_condition ssg0p81v0p81vm40c
set_wire_load_selection_group -max WireAreaForZero
set_load -pin_load 0.01 [all_outputs]    
# set port_load [load_of tcbn28hpcplusbwp12t30p140ssg0p81vm40c_ccs/INVD4BWP12T30P140/I]
set port_load [load_of tcbn28hpcplusbwp7t30p140ssg0p81v0p81vm40c_ccs/ISOHID1BWP7T30P140/I]
set input_cap [expr (4 * $port_load)]
set_max_capacitance $input_cap [all_inputs]
set_max_transition 0.25 [current_design]
set_max_fanout 16 [current_design]
