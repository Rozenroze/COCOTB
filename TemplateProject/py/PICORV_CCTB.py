import sys
sys.path.append('/home/vm-admin/TMP/COCOTB/CocotbEnv')
sys.path.append('/home/vm-admin/TMP/COCOTB/TemplateProject/py')

import cocotb

import library_akobzev as la
import ModelPython as MP
import SourceClock as SC 
import SourceSignal as SS 
import LinkerSignal as LS 
import CaptureSignal as CS 
import MainController as MC
import ProbeSignal as PS

import ReferenceModel_reg

################################################################
################################################################
controller = MC.MainController()
# controller.runtime = 600

################################################################
CLK_1G = SC.SourceClock('OSN', 'clk', [0, 0.5, 1], 1.2)

################################################################
signalOSN = SS.SourceSignal('OSN', 'rising_edge')

################################################################
captureOSNmodel = CS.CaptureSignal('OSN', 'falling_edge', 0)
linkerOSNdut = LS.LinkerSignalDut('OSN', 'rising_edge', 0)

################################################################
modelOSN = MP.ModelPython('OSN')
modelOSN.model = ReferenceModel_reg.ReferenceModel("/home/vm-admin/TMP/TMP_PARSER/", update_period=40, init_skip_cycles=100)

modelOSN.setting['global_skip_list'] = []
# modelOSN.setting['global_stop_work_model'] = list(range(1,17))+list(range(901,917))
modelOSN.setting['zero_work_model'] = 0

modelOSN.init()

################################################################

################################################################
################################################################
# run_full
@cocotb.test()
async def TEST_0(dut):
    await cocotb.start_soon(MC.run())

# ______________________________________________________________
# run_pydebug
if __name__=='__main__':
    for i in range(controller.runtime):
        if i == 886:
            pass
        MC.run_pydebug()

