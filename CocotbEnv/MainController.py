#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import os
import random
import numpy as np
import tabulate
import cocotb
from cocotb.triggers import Timer
from cocotb.types import Bit,Logic, LogicArray
import cProfile

import library_akobzev as la
import CaptureSignal as CS
import LinkerSignal as LS
import SourceClock as SC
import SourceSignal as SS
import Reporter as R
import ProbeSignal as PS


pb = None
start_status = False
OBJ = None

class MainController():
    def __init__(self):
        self.random_seed = int(os.getenv("RANDOM_SEED", 0))
        self.runtime = int(os.getenv("RUNTIME", 1000))
        self.mode = os.getenv("MODE", 'full')
        self.wave = os.getenv("WAVE", '1')

        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

        self.report = [('RUNTIME', f"{str(self.runtime)} ns"),
                       ('RANDOM_SEED', str(self.random_seed)),
                       ('MODE', self.mode),
                       ('WAVE', '1' if self.wave=='1' else '0'),]

        global OBJ
        OBJ = self


async def pb_run():
    global pb
    while True:
        await Timer(1, 'ns')
        pb.next()

def head_info():
    cocotb.log.info(tabulate.tabulate(OBJ.report, tablefmt='grid', colalign=("left","right")))

    if PS.dump_files.keys():
        for path in PS.dump_files.keys():
            cocotb.log.warning(f'Запись файлов в директорию: {path}')

async def run():
    # profiler = cProfile.Profile()
    # profiler.enable()

    head_info()

    global pb
    pb = la.ProgressBar(OBJ.runtime, "INFO     progress test", mod=[12,44])

    cocotb.start_soon(pb_run())
    cocotb.start_soon(SC.run())
    cocotb.start_soon(SS.run())
    if OBJ.mode in ['full', 'fullout']:
        cocotb.start_soon(LS.run_full())
        cocotb.start_soon(CS.run())
    if OBJ.mode in ['simjust']:
        cocotb.start_soon(LS.run_simjust())
    if OBJ.mode in ['pydebug']:
        cocotb.start_soon(LS.run_pydebug())
        
    await Timer(OBJ.runtime, 'ns')
    pb.next()

    if OBJ.mode in ['full', 'fullout']:
        R.create_report()

    PS.closer_files()
                
    # profiler.disable()  
    # profiler.print_stats(sort='time')  

def run_pydebug():
    global start_status
    global pb
    
    if not start_status:
        OBJ.report[0] = ('CNT_STEP', f"{str(OBJ.runtime)}")
        OBJ.report[2] = ('MODE', 'pydebug')
        OBJ.report[3] = ('WAVE', '0')
        print(tabulate.tabulate(OBJ.report, tablefmt='grid', colalign=("left","right")))
        pb = la.ProgressBar(OBJ.runtime, "Progress")
        start_status = True
    LS.link_pydebug()
    pb.next()




