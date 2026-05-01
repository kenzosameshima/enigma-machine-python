# Enigma Machine

This project is a Supervised Practical Assignment (SPA) for the Introduction
to Structured Programming course in the Computer Science program at UNIP. It
simulates the core behavior of the historical Enigma Machine using Python.

The simulator encrypts and decrypts messages with configurable rotors, ring
settings, rotor positions, reflectors, Greek rotors for M4 mode, and plugboard
pairs.

## Features

- Configurable rotors, ring settings, reflector, key positions, and plugboard
- Wehrmacht, Naval three-rotor, and M4 modes
- Symmetric encryption/decryption using the same machine settings
- Interactive CLI
- Package-based architecture with separated configuration, construction, and
  execution layers
- Compatibility wrappers for older imports such as `from engine import
  enigma_process`
- Basic automated regression tests

## Requirements

- Python 3.10+

## Installation

Clone the repository and enter the project folder:

```bash
git clone <repo-url>
cd enigma-machine-python
```

No external dependencies are required.

## Running the CLI

Classic entry point:

```bash
python3 main.py
```

Package entry point:

```bash
python3 -m enigma.cli
```

Example interactive session:

```text
=== ENIGMA MACHINE SIMULATOR (A-Z) ===
0 - Daily Key Sheet (historical simulation)
1 - Wehrmacht / 3-rotor
2 - Naval / 3-rotor
3 - M4 (4th thin rotor + thin reflector)

Select mode: 1
Enter message (max 128 chars): HELLO
Enter starting positions (e.g. ABC): ABC
Available moving rotors: I II III IV V
Enter rotor order left-to-right (e.g. I II III): I II III
Enter 3 ring settings 1-26 (e.g. 1 1 1): 1 1 1
Reflector (B/C, default B): B
Plugboard pairs (e.g. AB CD EF), blank for none: AB CD

Rotor window: [ABC]
Encrypted:  ROMUL
Decrypted:  HELLO
```

## Programmatic Usage

Preferred package import:

```python
from enigma import enigma_process

encrypted = enigma_process(
    text="HELLO WORLD",
    key="ABC",
    mode="wehrmacht",
    plug_pairs=[("A", "B"), ("C", "D")],
    rotor_order=("I", "II", "III"),
    ring_settings=(1, 1, 1),
    reflector_name="B",
)

decrypted = enigma_process(
    text=encrypted,
    key="ABC",
    mode="wehrmacht",
    plug_pairs=[("A", "B"), ("C", "D")],
    rotor_order=("I", "II", "III"),
    ring_settings=(1, 1, 1),
    reflector_name="B",
)

assert decrypted == "HELLO WORLD"
```

Older imports still work:

```python
from engine import enigma_process
```

## Running Tests

Run the automated test suite:

```bash
python3 -m unittest discover -s tests
```

Run a syntax/import check:

```bash
python3 -m compileall enigma tests cli.py config.py engine.py main.py
```

## Behavior Notes

- Input text is normalized to uppercase before processing.
- Spaces are preserved.
- Non-letter characters are passed through unchanged.
- Rotor stepping happens before each alphabetic character is encoded.
- Plugboard mappings are bidirectional.
- Invalid plugboard pairs raise `ValueError` in engine code instead of being
  printed and silently discarded.
- Decryption uses the same machine settings as encryption.

## Architecture

The current structure separates the main responsibilities:

```text
configuration -> construction -> execution -> interface
```

Project layout:

```text
enigma-machine-python/
├── enigma/
│   ├── __init__.py
│   ├── alphabet.py
│   ├── cli.py
│   ├── config.py
│   ├── data.py
│   ├── engine.py
│   ├── factory.py
│   ├── machine.py
│   ├── modes.py
│   ├── observer.py
│   ├── plugboard.py
│   └── rotors.py
├── tests/
│   └── test_engine.py
├── cli.py
├── config.py
├── engine.py
└── main.py
```

Core modules:

- `enigma.config` - `EnigmaConfig` and `EnigmaConfigBuilder`
- `enigma.factory` - `EnigmaFactory`
- `enigma.machine` - `EnigmaMachine` facade
- `enigma.modes` - mode strategies and enums
- `enigma.rotors` - rotor specs, state, and behavior
- `enigma.plugboard` - bidirectional plugboard mapping
- `enigma.data` - rotor and reflector tables
- `enigma.cli` - interactive command-line interface

The root `cli.py`, `config.py`, and `engine.py` files are compatibility
wrappers for older code and examples.
