from pathlib import Path
from os import chdir, system, get_terminal_size

chdir("student")
cwd = Path(".")
target = None
# Find the zip file
for f in cwd.glob("*.zip"):
    target = f
    break
assert target is not None, "No zip file found"

# Unzip and rename
system(f"unzip {target}")
target.unlink()
for f in cwd.iterdir():
    if f.is_dir():
        continue
    if not f.name.endswith(".asm"):
        f.unlink()
    else:
        # Rename like: Lab 2 (.asm file)_pbxxxxxxxx_尝试_2023-11-21-20-12-54_lab2.asm -> pbxxxxxxxx.asm
        newName = f.name.split("_")[1] + ".asm"
        f = f.rename(newName)
        print(newName)
