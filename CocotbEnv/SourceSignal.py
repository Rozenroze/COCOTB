#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge

import SourceClock as SC

groups = {}
cnt_step = {}

class SourceSignal():
    def __init__(self, group = 'OSN', edge_signal = 'rising_edge'):
        self.group = group
        self.edge_signal = edge_signal

        self.signal = {}
        self.cnt_step = -1
        
        add_group(self.group, self)


    def step(self):
        pass

    def step_wrap(self):
        self.cnt_step += 1
        global cnt_step
        cnt_step[self.group] = self.cnt_step
        self.step()
        
    async def start(self):
        while True:
            if self.edge_signal == 'rising_edge':
                await RisingEdge(SC.groups[self.group].clk)
            elif self.edge_signal == 'falling_edge':
                await FallingEdge(SC.groups[self.group].clk)
            else:
                print('Неправильноа указан источник сигнала')
                raise
            self.step_wrap()


def add_group(group, obj):
    if group not in groups.keys():
        groups[group] = []
        cnt_step[group] = -1
    groups[group].append(obj)

async def run():
    if groups:
        for group in groups.keys():
            for obj in groups[group]:
                cocotb.start_soon(obj.start())



