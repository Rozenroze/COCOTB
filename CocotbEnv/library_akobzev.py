#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

import numpy as np
import math
import copy
import tabulate
import os
import shutil
import time
from functools import wraps

from collections import deque
# from cocotb.clock import Clock
# from cocotb.triggers import Timer, ClockCycles, FallingEdge, RisingEdge, Edge
# from cocotb.queue import Queue, QueueEmpty, QueueFull

def to_fix_my(x, pfix):
	"""
	Double to fixed point converter. This script doesn't work with complex numbers!

	Parameters:
	----------
	x: float or ndarray of floats
		Input data.
	pfix: list or array
		Convertation parameters:
		pfix[0]: bitwidth.
		pfix[1]: exponent 2 ** e.
		pfix[2]: flag of fixed point:
			pfix[2] == 0: use float.
			pfix[2] == 1: convert to fixed.
		pfix[3] - type of x:
			pfix[3] == 0: unsigned.
			pfix[3] == 1: signed.
		pfix[4] - type of rounding:
			pfix[4] == 0: floor.
			pfix[4] == 1: ceil.
			pfix[4] == 2: round.

	Return:
	------
	out: float or ndarray of floats
		Fixed-point representation of initial data for given bitwidth and exponent.
	"""
	bits_pwrs = np.roll(2. ** np.linspace(-64, 64, 129), 65)
	if pfix[2] == 0:
		return x
	elif type(x) in [complex, np.complex128] or (type(x)==np.ndarray and x.dtype in [complex, np.complex128]):
		x_out = x * bits_pwrs[-pfix[1]]

		if pfix[4] == 0:
			x_out_r = np.floor(x_out.real)
		elif pfix[4] == 1:
			x_out_r = np.ceil (x_out.real)
		elif pfix[4] == 2:
			x_out_r = np.floor(x_out.real + 0.5)
		if pfix[3] == 1:
			x_out_r = np.clip(x_out_r, -bits_pwrs[pfix[0] - 1], bits_pwrs[pfix[0] - 1] - 1)
		else:
			x_out_r = np.clip(x_out_r, 0, bits_pwrs[pfix[0]] - 1)

		if pfix[4] == 0:
			x_out_i = np.floor(x_out.imag)
		elif pfix[4] == 1:
			x_out_i = np.ceil (x_out.imag)
		elif pfix[4] == 2:
			x_out_i = np.floor(x_out.imag + 0.5)
		if pfix[3] == 1:
			x_out_i = np.clip(x_out_i, -bits_pwrs[pfix[0] - 1], bits_pwrs[pfix[0] - 1] - 1)
		else:
			x_out_i = np.clip(x_out_i, 0, bits_pwrs[pfix[0]] - 1)

		return (x_out_r + 1j*x_out_i) * bits_pwrs[pfix[1]]
	else:
		if pfix[4] == 0:
			x_out = np.floor(x * bits_pwrs[- pfix[1]])
		elif pfix[4] == 1:
			x_out = np.ceil(x * bits_pwrs[- pfix[1]])
		elif pfix[4] == 2:
			x_out = np.floor(x * bits_pwrs[- pfix[1]] + 0.5)
		if pfix[3] == 1:
			x_out = np.clip(x_out, -bits_pwrs[pfix[0] - 1], bits_pwrs[pfix[0] - 1] - 1)
		else:
			x_out = np.clip(x_out, 0, bits_pwrs[pfix[0]] - 1)
		x_out *= bits_pwrs[pfix[1]]
		return x_out


class ColorText():
	CEND      = '\33[0m'
	CBOLD     = '\33[1m'
	CITALIC   = '\33[3m'
	CURL      = '\33[4m'
	CBLINK    = '\33[5m'
	CBLINK2   = '\33[6m'
	CSELECTED = '\33[7m'

	CBLACK  = '\33[30m'
	CRED    = '\33[31m'
	CGREEN  = '\33[32m'
	CYELLOW = '\33[33m'
	CBLUE   = '\33[34m'
	CVIOLET = '\33[35m'
	CBEIGE  = '\33[36m'
	CWHITE  = '\33[37m'

	CBLACKBG  = '\33[40m'
	CREDBG    = '\33[41m'
	CGREENBG  = '\33[42m'
	CYELLOWBG = '\33[43m'
	CBLUEBG   = '\33[44m'
	CVIOLETBG = '\33[45m'
	CBEIGEBG  = '\33[46m'
	CWHITEBG  = '\33[47m'

	CGREY    = '\33[90m'
	CRED2    = '\33[91m'
	CGREEN2  = '\33[92m'
	CYELLOW2 = '\33[93m'
	CBLUE2   = '\33[94m'
	CVIOLET2 = '\33[95m'
	CBEIGE2  = '\33[96m'
	CWHITE2  = '\33[97m'

	CGREYBG    = '\33[100m'
	CREDBG2    = '\33[101m'
	CGREENBG2  = '\33[102m'
	CYELLOWBG2 = '\33[103m'
	CBLUEBG2   = '\33[104m'
	CVIOLETBG2 = '\33[105m'
	CBEIGEBG2  = '\33[106m'
	CWHITEBG2  = '\33[107m'

	@classmethod
	def Do(cls, color, text):
		return cls.__dict__[color] + text + cls.CEND


def DopCode(data, param):
	if isinstance(data, int):
		if data < 0:
			must_width = math.ceil(math.log2(abs(data))) + 1
			if param < must_width:
				print(ColorText.Do('CYELLOW','[WARNING]') + f' : "param" must be >= {must_width}. Reconfig "param"')
				param = must_width
			tmp = f'{2**param + data:0>{param}b}'
		else:
			tmp = f'{data:0>{param}b}'
		return tmp

	if isinstance(data, str):
		tmp = data
		if param and data[0]=='1':
			tmp = 2**len(data) - int(tmp,2)
			return -tmp
		return int(tmp,2)

def to_bin_from_float_with_to_fix(value,spec):
	spec_my = spec
	spec_my[2] = 1
	tmp = int(to_fix_my(value, spec_my) * (2 ** -spec[1]))
	return DopCode(tmp, spec[0])

def to_float_from_bin_with_to_fix(value,spec):
	tmp = DopCode(value, spec[3])
	return tmp * (2 ** int(spec[1]))


def Convert(data, intype, outtype, inwidth, outwidth, insign=0):
	if isinstance(data, list) and intype[:4] != 'list':
		tmp = []
		for i in range(len(data)):
			tmp.append(Convert(data[i], intype, outtype, inwidth, outwidth, insign))
		return tmp

	if intype == 'int':
		if outtype == 'bin':
			return DopCode(data, outwidth)
		if outtype == 'hex':
			tmp = DopCode(data, outwidth)
			return f'{int(tmp,2):0>{math.ceil(outwidth/4)}x}'

	if intype == 'hex':
		if outtype == 'bin':
			tmp = f'{int(data,16):0>{inwidth}b}'
			return tmp.rjust(outwidth, tmp[0] if insign else '0')
		if outtype == 'int':
			tmp = f'{int(data,16):0>{outwidth}b}'
			return DopCode(tmp, insign)
		if outtype == 'listbin':
			tmp = f'{int(data,16):0>{inwidth}b}'
			tmp = tmp.rjust(outwidth, tmp[0] if insign else '0')
			return [int(i) for i in tmp]

	if intype == 'bin':
		if outtype == 'hex':
			tmp = data.rjust(inwidth, '0')
			tmp = tmp.rjust(outwidth, tmp[0] if insign else '0')
			return f'{int(tmp,2):0>{math.ceil(outwidth/4)}x}'
		if outtype == 'int':
			return DopCode(data, insign)
		if outtype == 'listbin':
			return [int(i) for i in data]

	if intype == 'listbin':
		tmp = ''.join([str(int(i)) for i in data])
		tmp = Convert(tmp, 'bin', outtype, inwidth, outwidth, insign)
		return tmp

class ProgressBar():
	def __init__(self, length, pretxt = 'Progress: ', afttxt = 'Complete',view = True, mod=[0,40]):
		self.length = length
		self.mod = mod
		self.pretxt = pretxt
		self.afttxt = afttxt
		self.view = view
		self.oneCube = self.length/50
		self.load = 0
		self.percent = 0
		self.sum = 0
		self.starttime = time.time()
		self.plotBar()

	def next(self):
		if self.view:
			self.math()
			if self.sum >= self.length:
				self.finish()
			else:
				self.plotBar()

	def finish(self):
		print(f"\r{'':>{self.mod[0]}}{self.pretxt:<{self.mod[1]}}{chr(9475)}{chr(9618)*50}{chr(9475)}  {time.strftime('%H:%M:%S', time.gmtime(time.time() - self.starttime))}   {str(self.percent):<5}%   {self.sum}/{self.length}   {ColorText.Do('CGREEN',self.afttxt)}   ")

	def math(self):
		self.sum = self.sum + 1
		self.load = int(self.sum//self.oneCube)
		self.percent = round((self.sum/self.length)*100,2)
		
	def plotBar(self):
		print(f"\r{'':>{self.mod[0]}}{self.pretxt:<{self.mod[1]}}{chr(9475)}{chr(9618)*self.load}{'-'*(50-self.load)}{chr(9475)}  {time.strftime('%H:%M:%S', time.gmtime(time.time() - self.starttime))}   {str(self.percent):<5}%   {self.sum}/{self.length}   ",end='')

	
class WriteFile():
	def __init__(self, adr, DoOpenFile = True):
		self.adr = adr
		self.file = None
		self.DoOpenFile = DoOpenFile
		if self.DoOpenFile:
			self.open()
		
	def open(self):
		self.file = open(self.adr, 'w')

	def close(self):
		self.file.close()

	def write(self, data, sep = ' ', end = '\n'):
		if isinstance(data, list):
			for i in data:
				self.write(i, sep = sep, end = '')
		else:
			self.file.write(str(data) + sep)
		self.file.write(end)


class ReadFile():
	def __init__(self, adr, DoOpenFile=True, DoReadFile = True, DoSplitlines = True, DoCloseFile = True):
		self.adr = adr
		self.file = None
		self.DoOpenFile = DoOpenFile
		self.DoReadFile = DoReadFile
		self.DoSplitlines = DoSplitlines
		self.DoCloseFile = DoCloseFile

		if self.DoOpenFile:
			self.open()
		if self.DoReadFile:
			self.read()
		if self.DoCloseFile:
			self.close()

	def open(self):
		self.file = open(self.adr, 'r')

	def close(self):
		self.file.close()

	def read(self):
		if self.DoSplitlines:
			self.data = self.file.read().splitlines()
		else:
			self.data = self.file.read()


class Singleton(object):
	_instance = None
	def __new__(class_, *args, **kwargs):
		if not isinstance(class_._instance, class_):
			class_._instance = object.__new__(class_, *args, **kwargs)
		return class_._instance


class MyCustomError(Exception):
	pass



class CalcDiap():
	def __init__(self):
		self.savevalue = None
		self.firstvalue = None
		self.diap_list = []
		self.diap_str = ''

	def calc_diap(self, step):
		if len(self.diap_list) == 0:
			self.diap_list.append(step)
			self.savevalue = step
			self.firstvalue = step
			return

		if len(self.diap_list) != 0:
			if step-1 == self.savevalue:
				if step-1 == self.firstvalue:
					self.diap_list.append(step)
					self.savevalue = step
				else:
					del self.diap_list[-1]
					self.diap_list.append(step)
					self.savevalue = step
			else:
				self.diap_list.append(',')
				self.diap_list.append(step)
				self.savevalue = step
				self.firstvalue = step
			return

	def convert(self):
		self.firstvalue = 0
		self.diap_str = ''
		for i in self.diap_list:
			if not isinstance(i,str):
				if self.firstvalue == 0:
					self.diap_str = self.diap_str + str(i)
					self.firstvalue = 1
				else:
					self.diap_str = self.diap_str + '-' + str(i)
					self.firstvalue = 0
			else:
				self.diap_str = self.diap_str + i + ' '
				self.firstvalue = 0
		return self.diap_str


def check_timing(log_to_file=False, filename="check_timing.log"):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			start_time = time.time()
			result = func(*args, **kwargs)
			end_time = time.time()
			elapsed_time = end_time - start_time

			message = f"Функция {func.__name__} : {elapsed_time:.6f} секунд"
			
			if log_to_file:
				with open(filename, "a") as file:
					file.write(message + "\n")

			return result
		return wrapper
	return decorator


############################################################################


if __name__ == "__main__":

	lst = 0.005859375
	spec = [ 8,-6,  1,  1,0]
	# spec = [9,6,1,0,2]
	# spec = [13,-11,1,0,2]
	# spec = [4,4,1,1,2]
	# spec = [3,-11,1,1,2]
	t=to_bin_from_float_with_to_fix(lst, spec)


	# binValue= '0011100110'
	binValue= '010000000'

	spec = [ 10,7,  1,  1,0]
	t1=to_float_from_bin_with_to_fix(binValue,spec)
	
	
	print(t)
	print(t1)
	# print(to_bin_f_hex('fa',64))

	# x = [[1,2],[3,4]]
	# f = WriteFile('del.txt')
	# f.write(x)
	# f.close()
