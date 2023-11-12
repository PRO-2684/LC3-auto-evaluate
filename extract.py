from pathlib import Path
from os import chdir, system

EXT = ".bin"

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
zipFiles: list[Path] = []
for f in cwd.iterdir():
    if f.is_dir():
        continue
    if not f.name.endswith(".zip"):
        f.unlink()
    else:
        # Rename like: Lab 1_pbxxxxxxxx_尝试_xxxxx_PBxxxxxxxx_xxx.zip -> pbxxxxxxxx.zip
        newName = f.name.split("_")[1] + ".zip"
        print(f"{f.name} -> {newName}")
        f = f.rename(newName)
        zipFiles.append(f)

# Unzip and organize
temp = Path("temp")
temp.mkdir(exist_ok=True)
for zipFile in zipFiles:
    system(f"unzip {zipFile} -d temp")
    # Find files with EXT
    for f in temp.rglob(f"*{EXT}"):
        # Rename like: *.bin -> pbxxxxxxxx.bin and move to cwd
        newName = zipFile.stem + EXT
        f = f.rename(cwd / newName)
        # Clean temp
        system(f"rm -rf student/temp/*")
        break
    zipFile.unlink()
