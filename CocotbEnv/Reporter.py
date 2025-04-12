#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import cocotb
import datetime

import ProbeSignal as PS
import MainController as MC
import ModelPython as MP


groups = {}

class ReportProbeSignal():
    def __init__(self, group):
        self.typerep = 'probe'
        self.group = group

        self.lentemplate = 0
        self.value = {}

        add_group(self.group, self)

        
    def checker_len(self, name, data):
        if name in ['local_skip_step', 'global_skip_step', 'not_verified']:
            data = data.convert()
        else:
            data = str(data)

        if self.value[name] < len(data):
            self.value[name] = len(data)

    def calc_template_len(self):
        self.value['path']             = len('path')
        self.value['name']             = len('name')
        self.value['pfix']             = len('pfix')
        self.value['delay']            = len('delay')
        self.value['buff_size']        = len('buff_size')
        self.value['latched_count']    = len('latched_count')
        self.value['create_step']      = len('create_step')
        self.value['global_skip_step'] = len('global_skip_step')
        self.value['local_skip_step']  = len('local_skip_step')
        self.value['not_verified']     = len('not_verified')

        for obj in PS.groups[self.group]:
            for path in obj.value.keys():
                self.checker_len('path', path)
                for name in obj.value[path].keys():
                    self.checker_len('name',             name)
                    self.checker_len('pfix',             obj.value[path][name]['pfix'])
                    self.checker_len('delay',            obj.value[path][name]['delay'])
                    self.checker_len('buff_size',        obj.value[path][name]['buff_size'])
                    self.checker_len('latched_count',    obj.value[path][name]['latched_count'])
                    self.checker_len('create_step',      obj.value[path][name]['create_step'])
                    self.checker_len('global_skip_step', obj.value[path][name]['global_skip_step'])
                    self.checker_len('local_skip_step',  obj.value[path][name]['local_skip_step'])
                    self.checker_len('not_verified',     obj.value[path][name]['not_verified'])
                    
        for i in self.value.keys():
            self.value[i] = self.value[i] + 5
            self.lentemplate = self.lentemplate + self.value[i]


    def title(self, file):
        file.write('='*self.lentemplate+'\n\n')
        file.write(f'  - group:       {self.group}'+'\n')
        file.write(f'  - time finish: {cocotb.utils.get_sim_time("ns")}/{MC.OBJ.runtime} ns'+'\n')
        if MP.groups[self.group].setting['global_stop_work_model']:
            file.write(f'  - global_stop_work_model: {MP.groups[self.group].setting["global_stop_work_model"]}'+'\n')
        file.write('\n')
        file.write('-'*self.lentemplate+'\n')
        for i,j in self.value.items():
            file.write(f'{i:<{j}}')
        file.write('\n')
        file.write('-'*self.lentemplate+'\n')
    

    def write_step(self, file, name, data):
        if name in ['local_skip_step', 'global_skip_step', 'not_verified']:
            data = data.diap_str
        file.write(f'{str(data):<{self.value[name]}}')

    def write_probe(self, file):
        for obj in PS.groups[self.group]:
            for path in obj.value.keys():
                if len(obj.value[path].keys()) == 0:
                    if MC.OBJ.mode != 'fullout':
                        self.write_step(file, 'path', path)
                        file.write('NOTHING_PROBE\n')
                for name in obj.value[path].keys():
                    self.write_step(file, 'path',             path)
                    self.write_step(file, 'name',             name)
                    self.write_step(file, 'pfix',             obj.value[path][name]['pfix'])
                    self.write_step(file, 'delay',            obj.value[path][name]['delay'])
                    self.write_step(file, 'buff_size',        obj.value[path][name]['buff_size'])
                    self.write_step(file, 'latched_count',    obj.value[path][name]['latched_count'])
                    self.write_step(file, 'create_step',      obj.value[path][name]['create_step'])
                    self.write_step(file, 'global_skip_step', obj.value[path][name]['global_skip_step'])
                    self.write_step(file, 'local_skip_step',  obj.value[path][name]['local_skip_step'])
                    self.write_step(file, 'not_verified',     obj.value[path][name]['not_verified'])
                    file.write('\n')
        file.write('\n'*5)

    def step(self, file):
        self.calc_template_len()
        self.title(file)
        self.write_probe(file)



def create_report():
    file = open('results/log/cocotb.log', 'w')
    file.write(f'\n  - time save:   {datetime.datetime.now()}'+'\n\n')

    global groups
    groups = {}

    for group in PS.groups.keys():
        ReportProbeSignal(group)

    for group in groups:
        for obj in groups[group]:
            obj.step(file)

    file.close() 




def add_group(group, obj):
    if group not in groups.keys():
        groups[group] = []
    groups[group].append(obj)