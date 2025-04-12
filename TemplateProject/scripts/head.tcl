set dw_hdl [getenv SYNOPSYS]/dw/sim_ver
set dw_lib [getenv SYNOPSYS]/libraries/syn

define_design_lib work -path ./work

# set lib_svt /opt/corp/fabs/current/TSMC/CRN28HPCplus/libs/logic/tcbn28hpcplusbwp12t30p140/timing_power_noise/CCS/tcbn28hpcplusbwp12t30p140_180a
# set lib_lvt /opt/corp/fabs/current/TSMC/CRN28HPCplus/libs/logic/tcbn28hpcplusbwp12t30p140lvt/timing_power_noise/CCS/tcbn28hpcplusbwp12t30p140lvt_180b
# set lib_hvt /opt/corp/fabs/current/TSMC/CRN28HPCplus/libs/logic/tcbn28hpcplusbwp12t30p140hvt/timing_power_noise/CCS/tcbn28hpcplusbwp12t30p140hvt_180a
set lib_lvt /icd/projects/rmb/tech/TSMC_CRN28HPCPLUS/std/tcbn28hpcplusbwp7t30p140lvt/timing_power_noise/CCS/tcbn28hpcplusbwp7t30p140lvt_180a
set lib_hvt /icd/projects/rmb/tech/TSMC_CRN28HPCPLUS/std/tcbn28hpcplusbwp7t30p140hvt/timing_power_noise/CCS/tcbn28hpcplusbwp7t30p140hvt_180a
set lib_svt /icd/projects/rmb/tech/TSMC_CRN28HPCPLUS/std/tcbn28hpcplusbwp7t30p140/timing_power_noise/CCS/tcbn28hpcplusbwp7t30p140_180a

set search_path "${dw_lib} ${lib_svt} ${lib_lvt} ${lib_hvt}"

# set target_library {tcbn28hpcplusbwp12t30p140hvtssg0p81vm40c_ccs.db tcbn28hpcplusbwp12t30p140ssg0p81vm40c_ccs.db}
set target_library "tcbn28hpcplusbwp7t30p140ssg0p81vm40c_ccs.db tcbn28hpcplusbwp7t30p140ssg0p81v0p81vm40c_ccs.db tcbn28hpcplusbwp7t30p140hvtssg0p81vm40c_ccs.db tcbn28hpcplusbwp7t30p140lvtssg0p81vm40c_ccs.db"

set synthetic_library dw_foundation.sldb

# set link_library {"*" tcbn28hpcplusbwp12t30p140ssg0p81vm40c_ccs.db tcbn28hpcplusbwp12t30p140hvtssg0p81vm40c_ccs.db dw_foundation.sldb }
set link_library "* tcbn28hpcplusbwp7t30p140ssg0p81vm40c_ccs.db tcbn28hpcplusbwp7t30p140ssg0p81v0p81vm40c_ccs.db tcbn28hpcplusbwp7t30p140hvtssg0p81vm40c_ccs.db tcbn28hpcplusbwp7t30p140lvtssg0p81vm40c_ccs.db dw_foundation.sldb"
