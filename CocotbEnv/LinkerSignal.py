#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge, Combine

import ModelPython as MP 
import SourceSignal as SS
import SourceClock as SC
import ProbeSignal as PS
import CaptureSignal as CS


groups_dut = {}
groups_model = {}

cnt_step_dut = {}
cnt_step_model = {}

class LinkerSignalModel():
    def __init__(self, group = 'OSN', edge_link = 'rising_edge', initial_delay = 0.1):
        self.group = group
        self.edge_link = edge_link
        self.initial_delay = initial_delay

        self.cnt_step = -1            

        add_group_model(self.group, self)

    def link(self):
        pass

    def link_wrap(self):
        self.cnt_step += 1
        global cnt_step_model
        cnt_step_model[self.group] = self.cnt_step
        self.link()

    async def start(self):
        while True:
            if self.edge_link == 'rising_edge':
                await RisingEdge(SC.groups[self.group].clk)
            if self.edge_link == 'falling_edge':
                await FallingEdge(SC.groups[self.group].clk)
            if self.initial_delay != 0:
                await Timer(self.initial_delay, units="ns")
            if SS.cnt_step[self.group] != -1:
                self.link_wrap()
                MP.groups[self.group].step_wrap()
                

class LinkerSignalDut():
    def __init__(self, group = 'OSN', edge_link = 'rising_edge', initial_delay = 0.1):
        self.group = group
        self.edge_link = edge_link
        self.initial_delay = initial_delay

        self.cnt_step = -1   

        add_group_dut(self.group, self)

    def link(self):
        pass

    def link_wrap(self):
        self.cnt_step += 1
        global cnt_step_dut
        cnt_step_dut[self.group] = self.cnt_step
        self.link()

    async def start(self):
        while True:
            if self.edge_link == 'rising_edge':
                await RisingEdge(SC.groups[self.group].clk)
            if self.edge_link == 'falling_edge':
                await FallingEdge(SC.groups[self.group].clk)
            if self.initial_delay != 0:
                await Timer(self.initial_delay, units="ns")
            if SS.cnt_step[self.group] != -1:
                self.link_wrap()


async def run_full():
    if groups_model and groups_dut:
        for group in groups_dut.keys():
            for obj in groups_dut[group]:
                cocotb.start_soon(obj.start())
        for group in groups_model.keys():
            cocotb.start_soon(groups_model[group].start())
    else:
        raise

async def run_simjust():
    if groups_dut:
        for group in groups_dut.keys():
            for obj in groups_dut[group]:
                cocotb.start_soon(obj.start())
    else:
        raise

async def run_pydebug():
    if groups_model:
        for group in groups_model.keys():
            cocotb.start_soon(groups_model[group].start())
    else:
        raise


def link_pydebug():
    for group in SS.groups.keys():
        for obj in SS.groups[group]:
            obj.step_wrap()

    for group in groups_model.keys():
        groups_model[group].link_wrap()
        MP.cnt_step[group] += 1
        MP.groups[group].step()
    
    for group in PS.groups.keys():
        for obj in PS.groups[group]:
            obj.global_step()


def add_group_dut(group, obj):
    if group not in groups_dut.keys():
        groups_dut[group] = []
        cnt_step_dut[group] = -1
    groups_dut[group].append(obj)

def add_group_model(group, obj):
    groups_model[group] = obj
    cnt_step_model[group] = -1

