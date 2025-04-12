#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import cocotb
from cocotb.triggers import Timer

groups = {}

class SourceClock():
    def __init__(self, group = 'OSN', name = 'CLK', wafe = [0, 0.5, 1], initial_delay = 0):
        self.group = group
        self.name = name
        self.wafe = wafe
        self.initial_delay = initial_delay
        self.clk = None

        add_group(self.group, self)

    async def start(self):
        await Timer(self.initial_delay, units="ns")
        while True:
            self.clk.value = 0
            if self.wafe[0] != 0:
                await Timer(round(self.wafe[0], 2), units="ns")

            self.clk.value = 1
            if self.wafe[1]-self.wafe[0] != 0:
                await Timer(round(self.wafe[1]-self.wafe[0], 2), units="ns")

            self.clk.value = 0
            if self.wafe[2]-self.wafe[1] != 0:
                await Timer(round(self.wafe[2]-self.wafe[1], 2), units="ns")

def add_group(group, obj):
    groups[group] = obj
    
async def run():
    if groups:
        for group in groups.keys():
            groups[group].clk = cocotb.top._id(groups[group].name, extended=False)
            cocotb.start_soon(groups[group].start())