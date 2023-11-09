import subprocess
from pathlib import Path
from argparse import ArgumentParser
from json import load, dump
from os import chdir, getcwd, get_terminal_size
from re import search

LC3TOOLS = Path("/home/ubuntu/lc3tools/")
DELIMITER = "=" * get_terminal_size().columns
subprocess.check_output
def parse_args():
    parser = ArgumentParser(description="Batch evaluate LC3 codes.")
    parser.add_argument("--test", type=str, default="./tests/lab1/",
                        help="Path to your directory of testcases (default ./tests/lab1/).")
    parser.add_argument("--target", type=str, default="./student/",
                        help="Path to codes you'd like to evaluate (default ./student/).")
    parser.add_argument("--output", type=str, default="./output/",
                        help="Path to output directory (default ./output/).")
    # parser.add_argument("--timeout", type=int, default=10,
    #                     help="Timeout for each testcase.")
    return parser.parse_args()

def sanitize(name: str) -> str:
    # Sanitize name to be a valid CPP identifier
    return name.replace("-", "_").replace(".", "_").replace(" ", "_")

def loadTestcases(test_dir: Path) -> dict:
    testcases = {}
    for file in test_dir.iterdir():
        if file.suffix != ".json":
            continue
        with open(file, "r") as f:
            testcases[file.stem] = load(f)
    return testcases

def compileTestcases(testcases: dict, name: str) -> bool:
    print("Reading templates...")
    with open("./templates/code.txt") as f:
        code = f.read()
    with open("./templates/func.txt") as f:
        func = f.read()
    testFuncs = []
    testRegs = []

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

def evaluate(name: str, target_dir: Path) -> bool:
    targets = {}
    for target_path in target_dir.iterdir():
        if not target_path.suffix in [".asm", ".bin"]:
            continue
        targets[target_path.stem] = target_path.absolute()

    print(f"Evaluating {len(targets)} targets at {name}...")

    data = {}
    for target_name, target_path in targets.items():
        print(f"Evaluating {target_name}...")
        out = subprocess.check_output([LC3TOOLS / "build/bin/" / name, "--ignore-privilege", target_path], timeout=10, encoding="utf-8")
        m = search(r"Total points earned: (\d+)/(\d+)", out)
        score = 0
        if m:
            score = int(m.group(1))
        data[target_name] = score
        print(f"{target_name} score: {score}")

    with open(target_dir / f"{name}.json", "w") as f:
        dump(data, f, indent=4, ensure_ascii=False)

    print(f"Report saved to {target_dir / name}.json")
    return True

def cleanUp(target_dir: Path) -> bool:
    for target_path in target_dir.iterdir():
        if target_path.suffix == ".obj":
            target_path.unlink()
    print("Clean up done.")
    return True

if __name__ == "__main__":
    args = parse_args()
    test_dir = Path(args.test) # Directory of testcases
    target_dir = Path(args.target) # Directory of codes to evaluate
    # timeout = args.timeout
    testcases = loadTestcases(test_dir)
    assert compileTestcases(testcases, test_dir.stem), "Testcases compilation failed."
    assert evaluate(test_dir.stem, target_dir), "Evaluation failed."
    assert cleanUp(target_dir), "Clean up failed."

    #     print(f"Cleaning up {target_name}...")
    #     obj_path.unlink()
