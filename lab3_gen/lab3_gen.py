from random import choice, randint
from json import dump

SEQ = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
MIN = 1
MAX = 98
CASES = 25
POINTS_PER_CASE = 4
SPECIAL_CASES = [
    ["123", "123"],
    ["hello", "hello"],
]

def rand_str(length) -> str:
    return "".join(choice(SEQ) for _ in range(length))

def hex4(n) -> str:
    return "0x" + hex(n & 0xffff)[2:].zfill(4)

def char_to_hex(c) -> str:
    return hex4(ord(c))

def str_to_hex(s) -> list:
    return [char_to_hex(c) for c in s]

def strcmp(s1, s2) -> int:
    i = 0
    while i < len(s1) and i < len(s2):
        if s1[i] != s2[i]:
            return ord(s1[i]) - ord(s2[i])
        i += 1
    if len(s1) == len(s2):
        return 0
    elif len(s1) > len(s2):
        return ord(s1[i])
    else:
        return -ord(s2[i])

def gen_testcase() -> tuple:
    s1 = rand_str(randint(MIN, MAX))
    s2 = rand_str(randint(MIN, MAX))
    return (s1, s2, strcmp(s1, s2))

def testcase_to_json(testcase) -> dict:
    memInit = {}
    mem1 = str_to_hex(testcase[0])
    mem2 = str_to_hex(testcase[1])
    for i in range(len(mem1)):
        memInit[hex4(0x3100 + i)] = mem1[i]
    for i in range(len(mem2)):
        memInit[hex4(0x3200 + i)] = mem2[i]
    return {
        "points": POINTS_PER_CASE,
        "mem_init": memInit,
        "mem_expected": {
            "0x3300": hex4(testcase[2])
        },
        "note": {
            "s1": testcase[0],
            "s2": testcase[1]
        },
        "input": "",
        "output": ""
    }

def main():
    data = {}
    for i in range(CASES - len(SPECIAL_CASES)):
        case_ = gen_testcase()
        data[f"case{i}"] = testcase_to_json(case_)
    for i, case_ in enumerate(SPECIAL_CASES):
        case_.append(strcmp(case_[0], case_[1]))
        data[f"case{CASES - len(SPECIAL_CASES) + i}"] = testcase_to_json(case_)
    with open("tests/lab3.json", "w") as f:
        dump(data, f, indent=4)

if __name__ == "__main__":
    main()
