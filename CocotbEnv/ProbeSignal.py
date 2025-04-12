#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************
# example:
#       import ProbeSignal as PS
#       self.probe = PS.Probe(group = 'OSN', path = 'None')
#       self.probe.shot(y, 'y_PP0', (-1,-1), [(128,9), 7, 0])
#***************************************************************

import numpy as np
import copy
import cocotb
from collections import deque
import os

import ModelPython as MP
from library_akobzev import check_timing
import library_akobzev as la

groups = {}
cnt_step = {}
dump_files = {}

class Probe():
    def __init__(self, group = 'OSN', path = None, power = True):
        self.group = group
        self.path = path
        self.power = power

        self.cnt_step = -1

        self.value = {}
        self.value[self.path] = {}

        add_group(self.group, self)

    def template_value(self, name, delay, pfix):
        self.value[self.path].update({name : {'value': None,
                                              'ram_value': None,
                                              'delay': delay, 
                                              'pfix': pfix, 
                                              'buff_size': None, 
                                              'buff': None,
                                              'zero_work_model_step': None,
                                              'local_skip_step': la.CalcDiap(),
                                              'global_skip_step': la.CalcDiap(),
                                              'not_verified': la.CalcDiap(),
                                              'create_step': 'NOTHING_PROBE',
                                              'latched_count': 0,
                                              'latched_status': False}})

    def create_buff(self, name, delay):
        tmp_buff_size = delay[1] - delay[0]
        if tmp_buff_size < 0:
            cocotb.log.error('\nОтрицательный буффер')
            raise 
        self.value[self.path][name]['buff_size'] = tmp_buff_size
        if self.value[self.path][name]['buff_size'] != 0:
            self.value[self.path][name]['buff'] = deque()
            for i in range(self.value[self.path][name]['buff_size']):
                self.value[self.path][name]['buff'].append("logical_skip")

    # @check_timing(log_to_file=True)
    def shot(self, value, name, delay, pfix):
        if self.power:
            if name not in self.value[self.path].keys():
                self.template_value(name, delay, pfix)
                self.create_buff(name, delay)
                self.value[self.path][name]['zero_work_model_step'] = self.value[self.path][name]['delay'][1] - MP.groups[self.group].setting['zero_work_model']
            self.value[self.path][name]['ram_value'] = copy.copy(value)
            self.value[self.path][name]['latched_count'] += 1
            self.value[self.path][name]['latched_status'] = True

            if isinstance(self.value[self.path][name]['ram_value'], np.ndarray):
                self.value[self.path][name]['ram_value'] = self.value[self.path][name]['ram_value'].tolist()

    # @check_timing(log_to_file=True)
    def global_step(self):
        if self.power:
            self.cnt_step += 1
            global cnt_step
            cnt_step[self.group] = self.cnt_step

            for path in self.value.keys():
                for name in self.value[path].keys():
                    #____________________________________________________________________________                        
                    if self.cnt_step in MP.groups[self.group].setting['global_stop_work_model']:
                        self.value[path][name]['value'] = "global_skip"
                        self.value[path][name]['global_skip_step'].calc_diap(self.cnt_step)
                        continue

                    #____________________________________________________________________________                        
                    if self.value[path][name]['create_step'] == 'NOTHING_PROBE':
                        self.value[path][name]['create_step'] = self.cnt_step

                    #____________________________________________________________________________                        
                    if self.cnt_step in MP.groups[self.group].setting['global_skip_list'] or \
                            'all' in MP.groups[self.group].setting['global_skip_list'] or \
                            self.cnt_step == MP.global_skip_on_signal(self.group):

                        if self.value[path][name]['buff_size'] != 0:
                            self.value[path][name]['buff'] = deque()
                            for i in range(self.value[path][name]['buff_size']):
                                self.value[path][name]['buff'].append("logical_skip")
                        self.value[path][name]['zero_work_model_step'] = self.value[path][name]['delay'][1] - MP.groups[self.group].setting['zero_work_model']
                        self.value[path][name]['value'] = "global_skip"
                        
                    #____________________________________________________________________________ 
                    elif self.value[path][name]['buff_size'] > 0:
                        if self.value[path][name]['zero_work_model_step'] > 0:
                            self.value[path][name]['zero_work_model_step'] -= 1

                            self.value[path][name]['buff'].append('logical_skip')
                            self.value[path][name]['value'] = self.value[path][name]['buff'].popleft()
                        else:
                            if self.value[path][name]['latched_status'] == True:
                                self.value[path][name]['buff'].append(self.value[path][name]['ram_value'])
                            else:
                                self.value[path][name]['buff'].append("verify_skip")
                            self.value[path][name]['value'] = self.value[path][name]['buff'].popleft()

                    #____________________________________________________________________________  
                    elif self.value[path][name]['buff_size'] == 0:
                        if self.value[path][name]['zero_work_model_step'] > 0:
                            self.value[path][name]['zero_work_model_step'] -= 1
                            self.value[path][name]['value'] = "logical_skip"
                        else:
                            if self.value[path][name]['latched_status'] == True:
                                self.value[path][name]['value'] = self.value[path][name]['ram_value']
                            else:
                                self.value[path][name]['value'] = "verify_skip"

                    #____________________________________________________________________________
                    if self.value[path][name]['value'] == "global_skip":
                        self.value[path][name]['global_skip_step'].calc_diap(self.cnt_step)
                    if self.value[path][name]['value'] == "logical_skip":
                        self.value[path][name]['local_skip_step'].calc_diap(self.cnt_step)
                    if self.value[path][name]['value'] == "verify_skip":
                        self.value[path][name]['not_verified'].calc_diap(self.cnt_step)

                    #____________________________________________________________________________   
                    self.value[path][name]['latched_status'] = False


def add_group(group, obj):
    if group not in groups.keys():
        groups[group] = []
        cnt_step[group] = -1
    for ind, probes in enumerate(groups[group]):
        if probes.path == obj.path:
            return
    groups[group].append(obj)



class ProbeFile():
    def __init__(self, path = None,  power = True):
        self.power = power
        self.path = path

        if self.power:
            os.makedirs(self.path, exist_ok=True)

            global dump_files
            if self.path not in dump_files.keys():
                dump_files.update({self.path:{}})

    def shot(self, file, data, sep = '', end = '\n'):
        global dump_files

        if self.power and self.path != None:
            if file not in dump_files[self.path].keys():
                dump_files[self.path][file] = open(f'{self.path}/{file}','w')
            
            self.write(dump_files[self.path][file], data, sep, end)


    def write(self, file, data, sep, end):
        if isinstance(data, list):
            for i in data:
                self.write(file, i, sep = sep, end = '')
        else:
            file.write(str(data) + sep)
        file.write(end)


def probe_off_group(group):
    for obj in groups[group]:
        obj.power = False

def all_probefile_off():
    for group in groups_file.keys():
        for obj in groups_file[group]:
            obj.power = False

def closer_files():
    for path in dump_files.keys():
        for file in dump_files[path].keys():
            dump_files[path][file].close()