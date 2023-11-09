from json import load
from re import compile, search

with open("./student/lab1.json") as f:
    data = load(f)

PTRN_FNAME = compile(r"([a-zA-Z]{2}\d{8})_([^.]+)")
PTRN_MEM = compile(r"Mem\[0x3101\]=(\d+)")

for fname, out in data.items():
    out = out["log"]
    stu = search(PTRN_FNAME, fname)
    if not stu:
        print(f"Incorrect filename: {fname}")
        continue
    stuId = stu.group(1)
    stuEnd = int(stuId[-1])
    mem = int(search(PTRN_MEM, out).group(1))
    if not stuEnd == mem:
        stuName = stu.group(2)
        print(f'Student {stuId} ({stuName}) gave wrong answer "{mem}".')
