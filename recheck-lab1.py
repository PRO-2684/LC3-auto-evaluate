from json import load
from re import compile, search

with open("./student/lab1.json") as f:
    data = load(f)

PTRN_FNAME = compile(r"([a-z]{2}\d{8})")
PTRN_MEM = compile(r"Mem\[0x3101\]=(\d+)")

for fname, out in data.items():
    out = out["log"]
    stu = search(PTRN_FNAME, fname)
    if not stu:
        print(f"Incorrect filename: {fname}")
        continue
    stuId = stu.group(1)
    stuEnd = int(stuId[-1])
    m = search(PTRN_MEM, out)
    mem = int(m.group(1)) if m else -1
    if mem == -1:
        print(f"Student {stuId} gave no answer")
    elif not stuEnd == mem:
        print(f'Student {stuId} gave wrong answer "{mem}" (expected "{stuEnd}")')
