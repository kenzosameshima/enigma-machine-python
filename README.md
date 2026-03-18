# Enigma Machine

This project is a Supervised Practical Assignment (SPA) for the Introduction to Structured Programming course in the Computer Science program at UNIP. It simulates the basic functionality of the historical Enigma Machine using Python.

The program allows users to input a message, which is then encrypted and decrypted using configurable rotors, ring settings, plugboard pairs, and a reflector, emulating the core logic of the original cipher device.

## Features

- Configurable rotors, ring settings, reflector, and plugboard
- Symmetric encryption/decryption (same settings for both)
- Interactive CLI with multiple machine modes
- Modular engine for programmatic use and testing

## Requirements

- Python 3.8+

## Installation

Clone the repository:

```bash
git clone <repo-url>
cd <repo-name>
```

## Run

From this folder:

```bash
python main.py
```

## CLI Example

Example interactive session (abridged):

```bash
$ python main.py
=== ENIGMA MACHINE SIMULATOR (A-Z) ===
0 - Daily Key Sheet (historical simulation)
1 - Wehrmacht / 3-rotor
2 - Naval / 3-rotor
3 - M4 (4th thin rotor + thin reflector)

Select mode: 1
Enter message (max 128 chars): HELLO WORLD
Enter starting positions (e.g. ABC or ABCD for M4): ABC
...
Encrypted:  ILBDA AMTAZ
Decrypted:  HELLO WORLD
```

## Behavior Notes

- Input text is normalized to uppercase before processing.
- Spaces are preserved.
- Non-letter characters (digits, punctuation, symbols) are passed through unchanged.
- Decryption uses the same machine settings as encryption.

## Example Test Usage (Engine Only)

```python
from engine import enigma_process

cipher = enigma_process(
    "HELLO WORLD",
    key="ABC",
    mode="wehrmacht",
    rotor_order=("I", "II", "III"),
    ring_settings=(1, 1, 1),
    reflector_name="B",
)

plain = enigma_process(
    cipher,
    key="ABC",
    mode="wehrmacht",
    rotor_order=("I", "II", "III"),
    ring_settings=(1, 1, 1),
    reflector_name="B",
)

assert plain == "HELLO WORLD"
```

## How It Works

1. `main.py` starts the CLI.
2. `cli.py` collects user settings (mode, key, rotors, rings, plugboard).
3. `engine.py` processes text using Enigma stepping and wiring rules.
4. `config.py` provides static rotor/reflector definitions.

## Project Layout

- `main.py` - entry point
- `cli.py` - interactive command-line interface
- `engine.py` - core encryption/decryption logic
- `config.py` - rotor and reflector data
