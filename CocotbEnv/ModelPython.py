#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import numpy as np
import cocotb

import MainController as MC
import ProbeSignal as PS
import library_akobzev as la

groups = {}
cnt_step = {}
cnt_step_global = {}

class ModelPython():
    def __init__(self, group = 'OSN'):
        self.group = group
        self.cnt_step = -1
        self.cnt_step_global = -1

        self.setting = {'global_skip_list': [],
                        'global_skip_on_signal': None,
                        'global_stop_work_model': [],
                        'zero_work_model': 0}

        self.list_in_signal = []
        self.list_out_signal = []
        self.model = None

        self.probe = None
        
        self.in_signal = None
        self.out_signal = None

        add_group(self.group, self)

    def step(self):
        tmp = self.in_signal.values()
        tmp = self.model.step(*tmp)
        if isinstance(tmp, list) or isinstance(tmp, tuple):
            self.list_out_signal = dict(zip(self.out_signal.keys(), tmp))
        else:
            self.list_out_signal = dict(zip(self.out_signal.keys(), [tmp]))

    def step_wrap(self):
        self.cnt_step_global += 1
        global cnt_step_global
        cnt_step_global[self.group] = self.cnt_step_global

        if self.cnt_step_global in self.setting['global_stop_work_model']:
            return

        self.cnt_step += 1
        global cnt_step
        cnt_step[self.group] = self.cnt_step
        
        self.step()

        if MC.OBJ.mode == 'fullout':
            self.probe_shot_fullout()

    def create_probe_fullout(self):
        cocotb.log.warning(f'Отсутствует объект probe для проверки выхода группы {self.group}\n')

    def probe_shot_fullout(self):
        pass

    def init(self):
        self.in_signal = dict.fromkeys(self.list_in_signal)
        self.out_signal = dict.fromkeys(self.list_out_signal)

        if MC.OBJ.mode == 'fullout':
            PS.probe_off_group(self.group)
            self.create_probe_fullout()


def global_skip_on_signal(group):
    if groups[group].setting['global_skip_on_signal'] != None:
        if type(groups[group].setting['global_skip_on_signal'][0].signal[groups[group].setting['global_skip_on_signal'][1]]) != type(groups[group].setting['global_skip_on_signal'][2]):
            raise
        if groups[group].setting['global_skip_on_signal'][0].signal[groups[group].setting['global_skip_on_signal'][1]] == groups[group].setting['global_skip_on_signal'][2]:
            return cnt_step_global[group]
    return None

def add_group(group, obj):
    groups[group] = obj
    cnt_step[group] = -1
    cnt_step_global[group] = -1