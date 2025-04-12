#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge
import numpy as np
from termcolor import colored
import tabulate

import library_akobzev as la
from library_akobzev import check_timing
import LinkerSignal as LS
import ProbeSignal as PS
import SourceClock as SC
import ModelPython as MP
import Reporter as R


groups = {}
cnt_step = {}

class CaptureSignal():
    def __init__(self, group = 'OSN', edge_capture = 'falling_edge', initial_delay = 0):
        self.group = group
        self.edge_capture = edge_capture
        self.initial_delay = initial_delay

        self.cnt_step = -1
        
        add_group(self.group, self)

    # @check_timing(log_to_file=True)
    def step_wrap(self):
        self.cnt_step += 1
        global cnt_step
        cnt_step[self.group] = self.cnt_step

        for obj in PS.groups[self.group]:
            obj.global_step()

            Probe = obj.value
            for path in Probe.keys():
                for name in Probe[path].keys():
                    if Probe[path][name]['value'] not in ["logical_skip", "global_skip", "verify_skip"]:
                        value_model = convert_out_model(Probe[path][name]['value'])
                        value_dut = convert_out_dut(path, name, Probe[path][name]['pfix'])
                        try:
                            assert value_model == value_dut
                            if value_model == "'x":
                                print('\n')
                                cocotb.log.warning(f"value_model {path}.{name}: 'x\n")
                        except AssertionError:
                            R.create_report()
                            print('\n')
                            cocotb.log.warning(f'Несовпадение данных : {path}.{name}')
                            report_err = [('group', self.group),
                                          ('model step error', MP.cnt_step[self.group] - Probe[path][name]['buff_size']),
                                          ('time error', f'{cocotb.utils.get_sim_time("ns")} ns')]
                            cocotb.log.warning(tabulate.tabulate(report_err, tablefmt='grid', colalign=("left","left")))
                            color_match(value_model, value_dut)
                            print(la.ColorText.Do('CRED','========================================'))
                            ans = input(la.ColorText.Do('CBLUE', 'Продолжить выполнение программы? [N/y] : '))
                            print(la.ColorText.Do('CRED','========================================'))
                            if ans != 'y':              
                                raise AssertionError


    def check_probe(self):
        if self.group not in PS.groups.keys():
            print('\n')
            cocotb.log.warning("Отсутсвует 'probe'")
            raise

    async def start(self):
        self.check_probe()
        while True:
            if self.edge_capture == 'rising_edge':
                await RisingEdge(SC.groups[self.group].clk)
            if self.edge_capture == 'falling_edge':
                await FallingEdge(SC.groups[self.group].clk)
            if self.initial_delay != 0:
                await Timer(self.initial_delay, units="ns")

            if LS.cnt_step_dut[self.group] != -1:
                self.step_wrap()

async def run():
    if groups:
        for group in groups.keys():
            cocotb.start_soon(groups[group].start())

def convert_out_model(value):
    if isinstance(value, str):
        if value == "skip":
            return value
    if isinstance(value, np.ndarray): #позже убрать - перенесено в probe.shot
        if value.dtype == np.dtype('bool'):
            tmp = value.astype(int)
        else:
            tmp = value
        tmp = tmp.tolist()
        return tmp
    if isinstance(value,list):
        tmp = np.array(value)
        tmp = tmp.astype(int)
        tmp = tmp.tolist()
        return tmp
    return value


def convert_from_list(data):
    if isinstance(data, list):
        tmp = [convert_from_list(i) for i in data]
        return ''.join(tmp)
    return data.binstr
    
def recurcive_convert_out_dut_value(data, shape, lenshape, pfix):
    if lenshape > 1:
        return [recurcive_convert_out_dut_value(i, shape, lenshape-1, pfix) for i in data]
    tmp = ''.join(data)
    if "x" in tmp: return "'x"
    tmp = la.to_float_from_bin_with_to_fix(tmp, [shape, pfix[1], 1, pfix[2], 0])
    return tmp

def convert_out_dut_value(value, pfix):
    tmp = list(convert_from_list(value))
    tmp = np.array(tmp)
    if isinstance(pfix[0], int):
        shape = [pfix[0]]
    elif isinstance(pfix[0], tuple):
        shape = list(pfix[0])
    if len(shape) > 1:
        tmp = tmp.reshape(shape)
    tmp = tmp.tolist()
    tmp = recurcive_convert_out_dut_value(tmp, shape[-1], len(shape), pfix)
    return tmp

def convert_out_dut(path, name, pfix):
    t_path = path.split('.')
    del t_path[0]
    tmp = cocotb.top
    for st_path in t_path:
        tmp = tmp._id(st_path, extended=False)
    dut_path = tmp._id(name, extended=False)
    return convert_out_dut_value(dut_path.value, pfix)


def color_match(arg1, arg2):
    def to_numpy(array):
        if isinstance(array, (list, tuple)):
            return np.array(array)
        elif isinstance(array, np.ndarray) or isinstance(array, np.int64):
            return array
        elif isinstance(array, bool) or isinstance(array, (int, float)) or array == "'x":
            return np.array(array)
        else:
            raise ValueError(f"Неподдерживаемый тип данных для {array}. Type = {array}")

    def compare_and_color(a, b):
        if a.shape != b.shape:
            return (
                np.vectorize(lambda x: colored(str(x), 'red'))(a),
                np.vectorize(lambda x: colored(str(x), 'red'))(b)
            )

        def color_value(val1, val2):
            if val1 == val2:
                if val1 == "'x":
                    return colored(str(val1), 'yellow'), colored(str(val2), 'yellow')
                return colored(str(val1), 'green'), colored(str(val2), 'green')
            else:
                return colored(str(val1), 'red'), colored(str(val2), 'red')
        colored_a, colored_b = np.vectorize(color_value)(a, b)
        return colored_a, colored_b

    def format_array_with_colors(array, colored_data):
        def recursive_format(arr, colors):
            if isinstance(arr, np.ndarray):
                if arr.ndim == 0:
                    return str(colors)
                elif arr.ndim == 1 and len(arr) == 1:
                    return str(colors[0])
                elif arr.ndim == 1:
                    return "[" + ", ".join(recursive_format(item, color) for item, color in zip(arr, colors)) + "]"
                elif arr.ndim > 1:
                    return "[" + ", ".join(
                        recursive_format(sub_arr, sub_colors) for sub_arr, sub_colors in zip(arr, colors)) + "]"
            else:
                return str(colors)

        return recursive_format(array, colored_data)
    try:
        np_arg1 = to_numpy(arg1)
        np_arg2 = to_numpy(arg2)
    except ValueError as e:
        print(f"Ошибка: {e}")
        raise

    colored_arg1, colored_arg2 = compare_and_color(np_arg1, np_arg2)
    formatted_arg1 = format_array_with_colors(np_arg1, colored_arg1)
    formatted_arg2 = format_array_with_colors(np_arg2, colored_arg2)

    print('PY_SIGNAL:\n')
    print(formatted_arg1)
    print('\n')
    print('SV_SIGNAL:\n')
    print(formatted_arg2)
    print('\n')


def add_group(group, obj):
    groups[group] = obj
    cnt_step[group] = -1