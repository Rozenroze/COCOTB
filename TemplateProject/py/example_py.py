import sys
sys.path.append('/home/akobzev/Projects_ELVEES/Projects/CocotbEnv')
sys.path.append('/home/akobzev/Projects_ELVEES/Projects/CocotbEnv/APB_package')
sys.path.append('/home/akobzev/Projects_ELVEES/GIT/tools/COT_sim')

import cocotb
import numpy as np

import library_akobzev as la
import ModelPython as MP
import SourceClock as SC 
import SourceSignal as SS 
import LinkerSignal as LS 
import CaptureSignal as CS 
import MainController as MC
import ProbeSignal as PS

import APBMasterGenerator as AMG
import APB_Model as AM
import ScenarioAPB as SAPB

import COT_libs_fixed
from configs.param_0 import *
from configs.fixed_0 import *


################################################################
################################################################
controller = MC.MainController()
# controller.runtime = 600

################################################################
CLK_1G = SC.SourceClock('OSN', 'CLK_1G', [0, 0.5, 1], 1.2)
CLK_500M = SC.SourceClock('SEC', 'CLK_500M', [0, 1, 2], 0.1)
CLK_100M = SC.SourceClock('APB', 'PCLK', [0, 5, 10], 0.3)

################################################################
signalSEC = SS.SourceSignal('SEC', 'rising_edge')
signalOSN = SS.SourceSignal('OSN', 'rising_edge')
signalAPB = SS.SourceSignal('APB', 'rising_edge')

def stepSEC():
    if signalSEC.cnt_step in list(range(200)):
        signalSEC.signal['XIN_IN'] = np.random.randint(0, 512, 128, dtype=int)
        signalSEC.signal['XIP_IN'] = np.random.randint(0, 512, 128, dtype=int)
        signalSEC.signal['XQN_IN'] = np.random.randint(0, 512, 128, dtype=int)
        signalSEC.signal['XQP_IN'] = np.random.randint(0, 512, 128, dtype=int)
        signalSEC.signal['YIN_IN'] = np.random.randint(0, 512, 128, dtype=int)
        signalSEC.signal['YIP_IN'] = np.random.randint(0, 512, 128, dtype=int)
        signalSEC.signal['YQN_IN'] = np.random.randint(0, 512, 128, dtype=int)
        signalSEC.signal['YQP_IN'] = np.random.randint(0, 512, 128, dtype=int)
    else:
        signalSEC.signal['XIN_IN'] = np.random.randint(129, 383, 128, dtype=int)
        signalSEC.signal['XIP_IN'] = np.random.randint(129, 383, 128, dtype=int)
        signalSEC.signal['XQN_IN'] = np.random.randint(129, 383, 128, dtype=int)
        signalSEC.signal['XQP_IN'] = np.random.randint(129, 383, 128, dtype=int)
        signalSEC.signal['YIN_IN'] = np.random.randint(129, 383, 128, dtype=int)
        signalSEC.signal['YIP_IN'] = np.random.randint(129, 383, 128, dtype=int)
        signalSEC.signal['YQN_IN'] = np.random.randint(129, 383, 128, dtype=int)
        signalSEC.signal['YQP_IN'] = np.random.randint(129, 383, 128, dtype=int)

def stepOSN():
    if signalOSN.cnt_step in [0]:
        signalOSN.signal['registers'] = COT_libs_fixed.registers.registers(param_dsp_tx, param_dsp_rx, param_ad_calib, param_framer)

    # if signalOSN.cnt_step in [160]:
    #     signalOSN.signal['registers'].ADC_BUFF_CLOCK_ENABLE_MUX = 7

    # if signalOSN.cnt_step in [173]:
    #     signalOSN.signal['registers'].ADC_BUFF_CLOCK_ENABLE = True
    
    if signalOSN.cnt_step in [0,900]:
        signalOSN.signal['RSTn'] = 0
    else:
        signalOSN.signal['RSTn'] = 1

def stepAPB():
    APBMasterGenerator.step_rst(signalAPB.cnt_step)
    APBMasterGenerator.step_rd(signalAPB.cnt_step)
    APBMasterGenerator.step_wr(signalAPB.cnt_step)
    APBMasterGenerator.step_nothing()
    signalAPB.signal['PRESETn'] = APBMasterGenerator.signal['PRESETn']
    signalAPB.signal['PSEL']    = APBMasterGenerator.signal['PSEL']
    signalAPB.signal['PENABLE'] = APBMasterGenerator.signal['PENABLE']
    signalAPB.signal['PWRITE']  = APBMasterGenerator.signal['PWRITE']
    signalAPB.signal['PADDR']   = APBMasterGenerator.signal['PADDR']
    signalAPB.signal['PWDATA']  = APBMasterGenerator.signal['PWDATA']

signalOSN.step = stepOSN
signalSEC.step = stepSEC
signalAPB.step = stepAPB

################################################################
linkerOSNmodel = LS.LinkerSignalModel('OSN', 'rising_edge', 0)
linkerAPBmodel = LS.LinkerSignalModel('APB', 'rising_edge', 0)

linkerOSNdut = LS.LinkerSignalDut('OSN', 'rising_edge', 0)
linkerSECdut = LS.LinkerSignalDut('SEC', 'rising_edge', 0)
linkerAPBdut = LS.LinkerSignalDut('APB', 'rising_edge', 0)

def link_model_OSN():
    modelOSN.in_signal['registers'] = signalOSN.signal['registers']
    modelOSN.in_signal['RSTn']      = signalOSN.signal['RSTn']
    modelOSN.in_signal['XIN_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['XIN_IN']])
    modelOSN.in_signal['XIP_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['XIP_IN']])
    modelOSN.in_signal['XQN_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['XQN_IN']])
    modelOSN.in_signal['XQP_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['XQP_IN']])
    modelOSN.in_signal['YIN_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['YIN_IN']])
    modelOSN.in_signal['YIP_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['YIP_IN']])
    modelOSN.in_signal['YQN_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['YQN_IN']])
    modelOSN.in_signal['YQP_IN']    = np.array([la.to_float_from_bin_with_to_fix(la.Convert(int(i),'int','bin',9,9,0),[9,7,1,0,0]) for i in signalSEC.signal['YQP_IN']])

def link_model_APB():
    modelAPB.in_signal['PRESETn']   = signalAPB.signal['PRESETn']                  
    modelAPB.in_signal['PSEL']      = signalAPB.signal['PSEL']               
    modelAPB.in_signal['PENABLE']   = signalAPB.signal['PENABLE']                  
    modelAPB.in_signal['PWRITE']    = signalAPB.signal['PWRITE']                 
    modelAPB.in_signal['PADDR']     = signalAPB.signal['PADDR']                
    modelAPB.in_signal['PWDATA']    = signalAPB.signal['PWDATA']                 

def link_dut_OSN():
    cocotb.top.RSTn.value = int(signalOSN.signal['RSTn'])

def link_dut_SEC():
    for i in range(128):
        cocotb.top.XIN_IN[i].value = int(signalSEC.signal['XIN_IN'][i])
        cocotb.top.XIP_IN[i].value = int(signalSEC.signal['XIP_IN'][i])
        cocotb.top.XQN_IN[i].value = int(signalSEC.signal['XQN_IN'][i])
        cocotb.top.XQP_IN[i].value = int(signalSEC.signal['XQP_IN'][i])
        cocotb.top.YIN_IN[i].value = int(signalSEC.signal['YIN_IN'][i])
        cocotb.top.YIP_IN[i].value = int(signalSEC.signal['YIP_IN'][i])
        cocotb.top.YQN_IN[i].value = int(signalSEC.signal['YQN_IN'][i])
        cocotb.top.YQP_IN[i].value = int(signalSEC.signal['YQP_IN'][i])

def link_dut_APB():
    cocotb.top.PRESETn.value = int(signalAPB.signal['PRESETn'])
    cocotb.top.PSEL.value    = int(signalAPB.signal['PSEL'])
    cocotb.top.PENABLE.value = int(signalAPB.signal['PENABLE'])
    cocotb.top.PWRITE.value  = int(signalAPB.signal['PWRITE'])
    cocotb.top.PADDR.value   = int(signalAPB.signal['PADDR'])
    cocotb.top.PWDATA.value  = int(signalAPB.signal['PWDATA'])

linkerOSNmodel.link = link_model_OSN
linkerAPBmodel.link = link_model_APB
linkerOSNdut.link = link_dut_OSN
linkerSECdut.link = link_dut_SEC
linkerAPBdut.link = link_dut_APB


################################################################
captureOSNmodel = CS.CaptureSignal('OSN', 'falling_edge', 0)
captureAPBmodel = CS.CaptureSignal('APB', 'falling_edge', 0)


################################################################
modelOSN = MP.ModelPython('OSN')
modelOSN.model = COT_libs_fixed.ad_calib.ad_calib(param_ad_calib)

modelOSN.list_in_signal = ['RSTn', 'XIP_IN', 'XIN_IN', 'XQP_IN', 'XQN_IN', 'YIP_IN', 'YIN_IN', 'YQP_IN', 'YQN_IN', 'registers']
modelOSN.list_out_signal = ['XI_OUT', 'XQ_OUT', 'YI_OUT', 'YQ_OUT', 'registers']

modelOSN.setting['global_skip_list'] = []
# modelOSN.setting['global_skip_list'] = ['all']
modelOSN.setting['global_skip_on_signal'] = [signalOSN, 'RSTn', 0]
modelOSN.setting['global_stop_work_model'] = list(range(1,17))+list(range(901,917))
modelOSN.setting['zero_work_model'] = 0

def create_probe_fullout():
    modelOSN.probe = PS.Probe(group = 'OSN', path='AD_CALIB')

def probe_shot_fullout():
    modelOSN.probe.shot([modelOSN.list_out_signal['XI_OUT'][63-i] for i in range(64)], 'XI_OUT', (15,15), [(64,9), 7, 1])
    modelOSN.probe.shot([modelOSN.list_out_signal['XQ_OUT'][63-i] for i in range(64)], 'XQ_OUT', (15,15), [(64,9), 7, 1])
    modelOSN.probe.shot([modelOSN.list_out_signal['YI_OUT'][63-i] for i in range(64)], 'YI_OUT', (15,15), [(64,9), 7, 1])
    modelOSN.probe.shot([modelOSN.list_out_signal['YQ_OUT'][63-i] for i in range(64)], 'YQ_OUT', (15,15), [(64,9), 7, 1])

modelOSN.create_probe_fullout = create_probe_fullout
modelOSN.probe_shot_fullout = probe_shot_fullout
modelOSN.init()


################################################################
modelAPB = MP.ModelPython('APB')
modelAPB.model = AM.APBMasterModel()
modelAPB.model.registers = SAPB.dump_registers()

modelAPB.list_in_signal = ['PRESETn', 'PSEL', 'PENABLE', 'PWRITE', 'PADDR', 'PWDATA']
modelAPB.list_out_signal = ['PRDATA', 'PREADY']

# modelAPB.setting['global_skip_list'] = []
modelAPB.setting['global_skip_list'] = ['all']
# modelAPB.setting['global_skip_on_signal'] = [signalOSN, 'RSTn', 0]
# modelAPB.setting['global_stop_work_model'] = list(range(1,17))
modelAPB.setting['zero_work_model'] = 0

# def create_probe_fullout():
#     modelAPB.probe = PS.Probe(group = 'OSN', path='AD_CALIB')

# def probe_shot_fullout():
#     modelAPB.probe.shot([modelAPB.list_out_signal['XI_OUT'][63-i] for i in range(64)], 'XI_OUT', (15,15), [(64,9), 7, 1])
#     modelAPB.probe.shot([modelAPB.list_out_signal['XQ_OUT'][63-i] for i in range(64)], 'XQ_OUT', (15,15), [(64,9), 7, 1])
#     modelAPB.probe.shot([modelAPB.list_out_signal['YI_OUT'][63-i] for i in range(64)], 'YI_OUT', (15,15), [(64,9), 7, 1])
#     modelAPB.probe.shot([modelAPB.list_out_signal['YQ_OUT'][63-i] for i in range(64)], 'YQ_OUT', (15,15), [(64,9), 7, 1])

# modelAPB.create_probe_fullout = create_probe_fullout
# modelAPB.probe_shot_fullout = probe_shot_fullout
modelAPB.init()

#===============================================================
# APB_Generator
APBMasterGenerator = AMG.APBMasterGenerator()
APBMasterGenerator.scenario = SAPB.scenario()



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

