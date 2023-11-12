from json import load, dump
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
        print(f"Student {stuId} failed to compile or timeout")
        assert data[fname]["score"] == 0
        data[fname]["log"] += "\nRe-check: Failed to compile or timeout"
    elif not stuEnd == mem:
        print(f'Student {stuId} gave wrong answer "{mem}" (expected "{stuEnd}")')
        data[fname]["score"] = data[fname]["score"] // 2 # half score if not match
        data[fname]["log"] += f"\nRe-check: Mem at 0x3101 ({mem}) does not match last digit of student ID ({stuEnd}), half score"
    else:
        data[fname]["log"] += f"\nRe-check: Correct"

with open("./student/lab1.json", "w") as f:
    dump(data, f, indent=4, ensure_ascii=False)
