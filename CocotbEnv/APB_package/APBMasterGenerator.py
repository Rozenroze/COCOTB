#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************


class APBMasterGenerator():
    def __init__(self):
        self.state = 'IDLE'
        self.scenario = {}

        # self.list_rd = {3: {'type':'rd,
        #                     'data':[0xa]}}
        # self.list_wr = {10:{'type':'wr',
        #                     'data':[0xa, 35]}}


        self.signal={}
        self.signal['PRESETn'] = 1
        self.signal['PSEL']    = 0
        self.signal['PENABLE'] = 0
        self.signal['PWRITE']  = 0
        self.signal['PADDR']   = 0
        self.signal['PWDATA']  = 0


    def step_nothing(self):
        if self.state in ['IDLE', 'READY']:
            self.signal['PSEL']    = 0
            self.signal['PENABLE'] = 0
            self.signal['PWRITE']  = 0
            self.signal['PADDR']   = 0
            self.signal['PWDATA']  = 0
            self.state = 'IDLE'

    def step_rst(self, step):
        if step in self.scenario.keys() and self.scenario[step]['type'] == 'rst':
            self.signal['PRESETn'] = 0
        else:
            self.signal['PRESETn'] = 1


    def step_wr(self, step):
        if self.state == 'IDLE':
            if step in self.scenario.keys() and self.scenario[step]['type'] == 'wr':
                self.signal['PSEL']    = 1
                self.signal['PWRITE']  = 1
                self.signal['PADDR']   = self.scenario[step]['data'][0]
                self.signal['PWDATA']  = self.scenario[step]['data'][1]
                self.state = 'SETUP_WR'
        elif self.state == 'SETUP_WR':
            self.signal['PENABLE'] = 1
            self.state = 'ACCESS_WR'
        elif self.state == 'ACCESS_WR':
            self.signal['PSEL']    = 0
            self.signal['PENABLE'] = 0
            self.signal['PWRITE']  = 0
            self.signal['PADDR']   = 0
            self.signal['PWDATA']  = 0
            self.state = 'READY'

    def step_rd(self, step):
        if self.state == 'IDLE':
            if step in self.scenario.keys() and self.scenario[step]['type'] == 'rd':
                self.signal['PSEL']    = 1
                self.signal['PADDR']   = self.scenario[step]['data'][0]
                self.state = 'SETUP_RD'
        elif self.state == 'SETUP_RD':
            self.signal['PENABLE'] = 1
            self.state = 'ACCESS_RD'
        elif self.state == 'ACCESS_RD':
            self.signal['PSEL']    = 0
            self.signal['PENABLE'] = 0
            self.signal['PWRITE']  = 0
            self.signal['PADDR']   = 0
            self.signal['PWDATA']  = 0
            self.state = 'READY'
            
