#***************************************************************
# author  : Кобзев Андрей Сергеевич
# contact : akobzev@elvees.com  
#***************************************************************

from collections import deque

import library_akobzev as la

dump = {}

class Buffer():
    def __init__(self, name, delay):
        self.name = name
        self.delay = delay
        self.buff_size = None
        self.buff = None
        self.value = "'x"

        self.create_buff()

        add_group(self.name, self)


    def create_buff(self):
        tmp_buff_size = self.delay[1] - self.delay[0]
        if tmp_buff_size < 0:
            raise 
        self.buff_size = tmp_buff_size
        if tmp_buff_size != 0:
            self.buff = deque(maxlen=tmp_buff_size)
            for i in range(tmp_buff_size):
                self.buff.append("logical_skip")

    def put(self, value):
        if self.buff_size != 0:
            self.value = self.buff.popleft()
            self.buff.append(value)

        if self.buff_size == 0:
            self.value = value

    def get(self):
        return self.value
    

def add_group(name, obj):
    if name not in dump.keys():
        dump[name] = obj
    else:
        print(la.ColorText.Do('CRED','С таким именем буффер уже существует'))
        raise