import subprocess
from pathlib import Path
from argparse import ArgumentParser
from json import load, dump
from os import chdir, getcwd, get_terminal_size
from re import search, compile

EXTS = [".asm"]
LC3TOOLS = Path("/home/ubuntu/lc3tools/")
DELIMITER = "=" * get_terminal_size().columns
PATTERN = compile(r"Total points earned: (\d+)/(\d+)")

def parse_args():
    parser = ArgumentParser(description="Batch evaluate LC3 codes.")
    parser.add_argument("--data", "-d", type=str, required=True,
                        help="Path to your json of testcases (e.g. ./tests/lab1.json).")
    parser.add_argument("--target", "-t", type=str, default="./student/",
                        help="Path to codes you'd like to evaluate (default ./student/).")
    parser.add_argument("--compile", "-c", action="store_true",
                        help="Compile testcases. Used when you have modified your testcases.")
    parser.add_argument("--timeout", type=int, default=10,
                        help="Timeout for each testcase.")
    return parser.parse_args()

def sanitize(name: str) -> str:
    # Sanitize name to be a valid CPP identifier
    return name.replace("-", "_").replace(".", "_").replace(" ", "_")

def generateCode(test_dir: Path) -> str:
    testcases = {}
    with open(test_dir, "r") as f:
        testcases = load(f)
    print("Reading templates...")
    with open("./templates/code.txt") as f:
        code = f.read()
    with open("./templates/func.txt") as f:
        func = f.read()
    testFuncs = []
    testRegs = []
    before = testcases.get("$before")
    if before:
        del testcases["$before"]
    else:
        before = ""
    after = testcases.get("$after")
    if after:
        del testcases["$after"]
    else:
        after = ""

    print("Generating code...")
    for testcaseName, testcase in testcases.items():
        slug = sanitize(testcaseName)
        testFunc = func
        initMems = []
        verifies = []
        for addr, val in testcase["mem_init"].items():
            initMems.append(f"    sim.writeMem({addr}, {val});")
        for addr, val in testcase["mem_expected"].items():
            verifies.append(f'    tester.verify("{testcaseName}_{addr}", sim.readMem({addr}) == {val}, total_points);')
        testFunc = testFunc.replace("{{name}}", "test_" + slug)
        testFunc = testFunc.replace("{{initMem}}", "\n".join(initMems))
        testFunc = testFunc.replace("{{verify}}", "\n".join(verifies))
        testFuncs.append(testFunc)
        testRegs.append(f'    tester.registerTest("{testcaseName}", test_{slug}, {testcase["points"]}, false);')
    code = code.replace("{{testFunc}}", "\n\n".join(testFuncs))
    code = code.replace("{{testReg}}", "\n".join(testRegs))
    code = code.replace("{{before}}", before)
    code = code.replace("{{after}}", after)
    return code

def compileTestcases(code: str, name: str) -> bool:
    print("Writing code...")
    current_dir = getcwd()
    chdir(LC3TOOLS / "src/test/tests")
    with open(f"{name}.cpp", "w") as f:
        f.write(code)

    print("Compiling code...")
    print(DELIMITER)
    chdir(LC3TOOLS / "build")
    try:
        subprocess.run(["cmake", "-DCMAKE_BUILD_TYPE=Release", ".."], check=True)
        subprocess.run(["make"], check=True)
    except subprocess.CalledProcessError:
        print(DELIMITER)
        chdir(current_dir)
        return False
    print(DELIMITER)
    chdir(current_dir)
    return True

def evaluate(name: str, target_dir: Path, timeout: int=10) -> bool:
    try:
        targets = {}
        for target_path in target_dir.iterdir():
            if not target_path.suffix in EXTS:
                continue
            targets[target_path.stem] = target_path.absolute()
        n = len(targets)
        print(f"Evaluating {n} targets at {name}...")

        data = {}
        i = 0
        for target_name, target_path in targets.items():
            i += 1
            print(f"Evaluating {target_name}... ({i}/{n})", end="\r")
            try:
                out = subprocess.check_output([LC3TOOLS / "build/bin/" / name, "--ignore-privilege", target_path], timeout=timeout, encoding="utf-8")
            except subprocess.TimeoutExpired:
                print(f"{target_name} timed out.                     ")
                data[target_name] = {
                    "score": 0,
                    "log": "Evaluation timed out."
                }
                continue
            m = search(PATTERN, out)
            score = 0
            if m:
                score = int(m.group(1))
            data[target_name] = {
                "score": score,
                "log": out
            }
            print(f"{target_name} score: {score}                 ")

    except KeyboardInterrupt:
        print("Evaluation interrupted.")
    with open(target_dir / f"{name}.json", "w") as f:
        dump(data, f, indent=4, ensure_ascii=False)

    print(f"Report saved to {target_dir / name}.json")
    return True

def cleanUp(target_dir: Path) -> bool:
    for target_path in target_dir.glob("*.obj"):
        target_path.unlink()
    print("Clean up done.")
    return True

if __name__ == "__main__":
    args = parse_args()
    test_dir = Path(args.data) # Directory of testcases
    target_dir = Path(args.target) # Directory of codes to evaluate
    timeout = args.timeout
    if args.compile:
        code = generateCode(test_dir)
        assert compileTestcases(code, test_dir.stem), "Testcases compilation failed."
    else:
        assert (LC3TOOLS / "build/bin/" / test_dir.stem).exists(), "Testcases not compiled."
        print("Using existing compiled testcases...")
    assert evaluate(test_dir.stem, target_dir, timeout), "Evaluation failed."
    assert cleanUp(target_dir), "Clean up failed."
