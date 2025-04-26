import os
import sys

sys.path.append('/home/vm-admin/TMP/COCOTB/CocotbEnv')

import ProbeSignal as PS

class ReferenceModel:
    def __init__(self, reg_dir, update_period=1, init_skip_cycles=0):
        self.reg_order = [
            "zero", "ra", "sp", "gp", "tp",
            "t0", "t1", "t2", "s0", "s1",
            "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
            "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
            "t3", "t4", "t5", "t6"
        ]
        self.reg_dir = reg_dir
        self.regs = {name: 0 for name in self.reg_order}
        self.reg_lines = {name: [] for name in self.reg_order}
        self.update_period = update_period
        self.init_skip_cycles = init_skip_cycles
        self.clk_count = 0
        self.step_num = 0
        self._load_all_files()
        self.probe = PS.Probe(group='OSN', path='picorv32_m')

    def _load_all_files(self):
        for reg in self.reg_order:
            path = os.path.join(self.reg_dir, f"{reg}.dat")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing register file: {path}")
            with open(path, "r") as f:
                lines = f.read().strip().splitlines()
                self.reg_lines[reg] = lines

    def step(self):
        self.clk_count += 1

        if self.clk_count >= self.init_skip_cycles:
            if (self.clk_count - self.init_skip_cycles) % self.update_period == 0:
                for reg in self.reg_order:
                    lines = self.reg_lines[reg]
                    if self.step_num < len(lines):
                        self.regs[reg] = int(lines[self.step_num], 16)
                self.step_num += 1

                for i, reg in enumerate(self.reg_order):
                    value = self.regs[reg]
                    signal_name = f"dbg_reg_x{i}"
                    self.probe.shot(value, signal_name, (0, 0), [(32), 0, 0])