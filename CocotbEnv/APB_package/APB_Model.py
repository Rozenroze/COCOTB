#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import sys
sys.path.append('/home/akobzev/Projects_ELVEES/Projects/CocotbEnv')
import ProbeSignal as PS
import Buffer as BF

class APBMasterModel():
    def __init__(self):
        self.state = 'IDLE' #SETUP_WR, SETUP_RD, ACCESS, IDLE
        self.prestate = 'IDLE'

        self.probe = PS.Probe(group = 'APB', path = 'AD_CALIB')

        self.registers = None


    def step(self, PRESETn, PSEL, PENABLE, PWRITE, PADDR, PWDATA):
        PRDATA = 0
        PREADY = 0

        if PRESETn == 0:
            for addr in self.registers.keys():
                if 'w' in self.registers[addr]['typereg']:
                    self.registers[addr]['datareg'] = self.registers[addr]['defaultreg']


        if self.state == 'IDLE':
            if PSEL and not PENABLE and PWRITE:
                self.state = 'SETUP_WR'
                self.prestate = 'IDLE'
                PRDATA = 0
                PREADY = 0
            if PSEL and not PENABLE and not PWRITE:
                self.state = 'SETUP_RD'
                self.prestate = 'IDLE'
                PRDATA = 0
                PREADY = 0

        if self.state == 'SETUP_WR':
            if PSEL and PENABLE:
                self.state = 'ACCESS'
                self.prestate = 'SETUP_WR'
                PRDATA = 0
                PREADY = 1

        if self.state == 'SETUP_RD':
            if PSEL and PENABLE:
                self.state = 'ACCESS'
                self.prestate = 'SETUP_RD'
                PRDATA = 0
                PREADY = 1

        if self.state == 'ACCESS':
            if not PSEL:
                self.state = 'IDLE'
                self.prestate = 'ACCESS'
                PRDATA = 0
                PREADY = 0


        if self.state == 'ACCESS' and self.prestate == 'SETUP_WR':
            self.task_write(PADDR, PWDATA)


        if self.state == 'ACCESS' and self.prestate == 'SETUP_RD':
            PRDATA = self.task_read(PADDR)


        self.probe.shot(PRDATA, 'PRDATA', (0,0), ((32),0,0))
        self.probe.shot(PREADY, 'PREADY', (0,0), ((1),0,0))
        return PRDATA, PREADY



    def task_write(self, PADDR, PWDATA):
        if PADDR in self.registers.keys():
            if self.registers[PADDR]['typereg'] == 'r':
                print("Нельзя записать в регистр чтения")
                raise
            self.registers[PADDR]['datareg'] = PWDATA & ~self.registers[PADDR]['selfreset']

    def task_read(self, PADDR):
        if PADDR in self.registers.keys():
            if isinstance(self.registers[PADDR]['datareg'], BF.Buffer):
                return self.registers[PADDR]['datareg'].get()
            return self.registers[PADDR]['datareg']
        return 0

        

    