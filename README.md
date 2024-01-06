# LC3-auto-evaluate

Automatically evaluate lc3 codes, designed for ICS @ USTC.

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
  --compile, -c         Compile testcases. Used when you have modified your testcases.
  --timeout TIMEOUT     Timeout for each testcase.
  --ignore-privilege    Ignore privileged mode.
  --store-output        Store output of given programs in log.
```

## Testcases

Testcases are stored in json files. You can find some examples in `tests/`.

```jsonc
{
    "$before": "std::cout << \"\\nHello!\" << std::endl;", // Code to be executed before each testcase.
    "$after": "std::cout << \"\\nMem[0x3101]=\" << sim.readMem(0x3101) << std::endl;", // Code to be executed after each testcase.
    "$PC": "0x3000", // Initial PC, default 0x3000.
    "case1": {
        "points": 2, // Points for this testcase. (REQUIRED)
        "mem_init": { // Initial memory.
            "0x3100": "0xABCD"
        },
        "mem_expected": { // Expected memory after execution.
            "0x3102": "sim.readMem(0x3101) + 13" // You can use API provided by lc3tools.
        },
        // OPTIONAL
        "input": "qwertyQWERTY", // Keyboard input for this testcase.
        "delay": 50, // Delay of each character, in terms of instructions.
        "output": "Hello!\nMem[0x3101]=65", // Expected output. (Not implemented yet)
    },
    // ...
}
```
