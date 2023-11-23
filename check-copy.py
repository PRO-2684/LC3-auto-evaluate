from pathlib import Path
from argparse import ArgumentParser
from json import load, dump
from os import get_terminal_size
from chardet import detect

EXT = ".asm"
COMMENT = ";"
DELIMITER = "=" * get_terminal_size().columns

def parse_args():
    parser = ArgumentParser(description="Check copy.")
    parser.add_argument("--target", "-t", type=str, default="./student/",
                        help="Path to codes you'd like to check (default ./student/).")
    return parser.parse_args()

def purge(string: str) -> str:
    new = ""
    string = string.replace(" ", "").replace("\t", "")
    for line in string.split("\n"):
        parts = line.split(COMMENT)
        new += parts[0] # Remove comments and newlines
    return new

def check(target_dir: Path) -> bool:
    targets = {} # {content: [fname, ...]}
    duplicates = set() # fnames
    for target_path in target_dir.iterdir():
        if not target_path.suffix == EXT:
            continue
        print(f"Checking {target_path.stem}...")
        content = target_path.read_bytes()
        encoding = detect(content)["encoding"]
        content = content.decode(encoding)
        content = purge(content)
        targets.setdefault(content, []).append(target_path.stem)
    for content, ids in targets.items():
        if len(ids) > 1:
            duplicates.update(ids)
    print(DELIMITER)
    if duplicates:
        for fname in duplicates:
            print(f"{fname} is duplicated.")

if __name__ == "__main__":
    args = parse_args()
    target_dir = Path(args.target) # Directory of codes to evaluate
    check(target_dir)
