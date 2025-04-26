import re

import pexpect
import os
import sys
from tqdm import tqdm

# Настройка окружения
os.environ["RISCV"] = "/opt/riscv"
os.environ["PATH"] = os.environ["RISCV"] + "/bin:" + os.environ["PATH"]

spike_path = os.path.join(os.environ["RISCV"], "bin", "spike")
pk_path = os.path.join(os.environ["RISCV"], "riscv32-unknown-elf", "bin", "pk")
prog = "/home/vm-admin/TMP/TEST_DATA/S_FILE/prog_2.elf"
isa = "--isa=RV32IMC"

# Запуск Spike
child = pexpect.spawn(f"{spike_path} {isa} -d {prog}",
                      encoding='utf-8',
                      timeout=5)

# Список регистров
registers = [
    "zero", "ra", "sp", "gp", "tp",
    "t0", "t1", "t2", "s0", "s1",
    "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
    "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
    "t3", "t4", "t5", "t6"
]

core_trace_log = open("TMP_PARSER/spike_core_trace.log", "w")


def get_register(reg_name):
    """Функция для корректного чтения регистров с учетом формата вывода Spike"""
    child.sendline(f"reg 0 {reg_name}")
    # Ожидаем строку со значением
    child.expect("\n")
    child.expect("\n")
    reg_value = child.before.strip()

    # Если это строка выполнения инструкции - пропускаем
    while not re.fullmatch(r"0x[0-9a-f]+", reg_value):
        child.expect("\r\n")
        if reg_value.split()[0] == "core":
            core_trace_log.write(reg_value + "\n")
        reg_value = child.before.strip()

    return reg_value

for reg in registers:
    f = open(f"TMP_PARSER/{reg}.dat", "w")

# Основной цикл выполнения
try:
    # Ожидаем начальное приглашение
    child.expect_exact("(spike)")
    # for tick in range(1, 101):
    for tick in tqdm(range(1, 1001), desc="Выполнение"):
        child.sendline("")
        child.expect_exact("(spike)")

        # Чтение и запись регистров
        for reg in registers:
            value = get_register(reg)
            with open(f"TMP_PARSER/{reg}.dat", "a") as f:
                f.write(f"{value}\n")

except KeyboardInterrupt:
    print("\nПрервано пользователем")
except Exception as e:
    print(f"\nКритическая ошибка: {str(e)}")
finally:
    child.close()
    print("Работа завершена")