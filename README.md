# LC3-auto-evaluate
Automatically evaluate lc3 codes

## Setup

> You need to have `python3`, `git`, `cmake` and `make` installed.

1. Compile CLI tools of [lc3tools](https://github.com/chiragsakhuja/lc3tools/)
    1. `git clone https://github.com/chiragsakhuja/lc3tools.git`
    2. ```bash
        # Create build directory
        mkdir build && cd build
        # Set up build directory (run twice)
        cmake -DCMAKE_BUILD_TYPE=Release ..
        cmake -DCMAKE_BUILD_TYPE=Release ..
        # Build
        make
        ```
    3. `cd ..`
2. `chmod +x lc3tools/build/bin/*`
3. Clone this repo and cd into it
4. Modify `evaluate.py`, Line 7, to set the path to `lc3tools`

## Usage

```
usage: evaluate.py [-h] --data DATA [--target TARGET]

Batch evaluate LC3 codes.

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Path to your json of testcases (e.g. ./tests/lab1.json).
  --target TARGET, -t TARGET
                        Path to codes you'd like to evaluate (default ./student/).
```
