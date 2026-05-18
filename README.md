# Enigma Machine Python

## Overview

`enigma-machine-python` is a small educational simulator for the historical
Enigma machine. It supports Wehrmacht/Naval three-rotor operation and Naval M4
operation with a Greek rotor and thin reflector.

The package keeps the project split into clear layers:

```text
configuration -> construction -> machine execution -> interface
```

The root-level `engine.py`, `cli.py`, and `config.py` modules remain as
compatibility wrappers for older imports. New code should prefer imports from
the `enigma` package.

## Installation

Use Python 3.10 or newer.

Current prerelease version: `0.2.2-alpha`.

```bash
git clone <repo-url>
cd enigma-machine-python
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

For runtime-only use, the package has no mandatory third-party dependencies.

## Testing

Run tests in a minimal environment without coverage:

```bash
python3 -m pytest
```

Run the full dev dependency test command with coverage tracking:

```bash
python3 -m pytest --cov=enigma --cov-branch
```

## CLI Usage

Run the interactive CLI from the project root:

```bash
python3 -m enigma.cli
```

The compatibility entry points also work:

```bash
python3 main.py
python3 cli.py
```

Example session:

```text
=== ENIGMA MACHINE SIMULATOR (A-Z) ===
0 - Daily Key Sheet (historical simulation)
1 - Wehrmacht / 3-rotor
2 - Naval / 3-rotor
3 - M4 (4th thin rotor + thin reflector)

Select mode: 1
Enter message (max 128 chars): HELLO WORLD
Enter starting positions (e.g. ABC): ABC
Available moving rotors: I II III IV V
Enter rotor order left-to-right (e.g. I II III): I II III
Enter 3 ring settings 1-26 (e.g. 1 1 1): 1 1 1
Reflector (B/C, default B): B
Plugboard pairs (e.g. AB CD EF), blank for none: AB CD
```

## Programmatic Usage

Preferred import:

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

Factory-based usage:

```python
from enigma import EnigmaConfigBuilder, EnigmaFactory

config = (
    EnigmaConfigBuilder()
    .text("ATTACK AT DAWN")
    .mode("wehrmacht")
    .rotors("I", "II", "III")
    .rings(1, 1, 1)
    .key("ABC")
    .reflector("B")
    .plugboard([("A", "B"), ("C", "D")])
    .build()
)

machine = EnigmaFactory().create(config)
ciphertext = machine.process_text(config.text)
```

Older imports are still supported:

```python
from engine import enigma_process
```

## Public API Contract

The supported public API is:

- `enigma.enigma_process`
- `enigma.EnigmaConfig`
- `enigma.EnigmaConfigBuilder`
- `enigma.EnigmaFactory`
- `enigma.MachineModeName`
- `enigma.ReflectorName`
- `enigma.Plugboard`
- `enigma.Rotor`, `enigma.RotorSpec`, and `enigma.RotorState`

Root-level `engine.py`, `cli.py`, and `config.py` are compatibility wrappers for
legacy imports. They remain supported, but new code should import from
`enigma`.

`enigma_process()` is the preferred high-level API. It builds a fresh machine for
each call, normalizes input text to uppercase, preserves spaces, punctuation, and
numbers, and advances rotors only for A-Z characters.

Invalid user configuration raises `ValueError`. Expected validation failures
include unsupported modes, invalid rotor names, repeated moving rotors, ring
settings outside 1-26, incorrectly sized keys, incompatible reflectors, invalid
Greek rotors, and invalid plugboard pairs.

`EnigmaFactory.create()` returns a fresh `EnigmaMachine` with isolated rotor
state. Directly constructed `EnigmaMachine` instances defensively copy rotor
objects by default. This prevents accidental state sharing between machines.
Compatibility helpers that historically mutate external rotor objects preserve
their previous behavior.

## Supported Modes

Three-rotor modes:

- `wehrmacht`
- `naval`
- Uses exactly three moving rotors.
- Supports reflectors `B` and `C`.

M4 mode:

- `m4`
- Uses three moving rotors plus one fixed Greek rotor.
- Supports Greek rotors `BETA` and `GAMMA`.
- Supports thin reflectors `B_THIN` and `C_THIN`.

## Rotor Configuration

Moving rotors are selected left-to-right:

```python
rotor_order=("I", "II", "III")
```

Supported moving rotors are `I`, `II`, `III`, `IV`, and `V`. A moving rotor
cannot be repeated in the same configuration.

## Ring Settings

Ring settings are one-based integers from 1 to 26:

```python
ring_settings=(1, 14, 26)
```

Three-rotor modes require three ring settings. M4 requires four ring settings:
three for the moving rotors and one for the Greek rotor.

## Initial Positions

The `key` argument sets the starting window positions:

```python
key="ABC"
```

Three-rotor modes require three letters. M4 requires four letters. Input text is
normalized to uppercase before processing. Spaces, punctuation, and numbers are
preserved and do not advance rotors.

## Plugboard

Plugboard pairs are bidirectional:

```python
plug_pairs=[("A", "B"), ("C", "D")]
```

Rules:

- Maximum of 10 pairs.
- Each pair must contain two A-Z letters.
- A letter can appear in only one pair.
- Pair input is normalized to uppercase.

## Reflectors

Three-rotor modes use:

- `B`
- `C`

M4 mode uses thin reflectors:

- `B_THIN`
- `C_THIN`

The mode validator rejects incompatible reflector combinations.

## M4 And Double-Step

M4 adds a fixed Greek rotor between the moving rotor stack and the thin
reflector. The Greek rotor does not step.

The three moving rotors follow the classic stepping behavior:

- The right rotor steps before every alphabetic character.
- If the right rotor is at its turnover notch, the middle rotor steps.
- If the middle rotor is at its turnover notch, both the middle and left rotors
  step. This is the classic double-step behavior.
- Non-alphabetic characters pass through unchanged and do not step any rotor.

## Tests

Run the test suite:

```bash
python3 -m pytest
```

Run tests with coverage:

```bash
python3 -m pytest --cov=enigma --cov-report=term-missing --cov-fail-under=80
```

Coverage threshold is initially set to 80% and will be increased gradually as
CLI coverage improves. The target is 90% after extracting and testing CLI
command logic without relying on brittle interactive I/O tests.

The suite covers round trips, plugboard validation, M4 validation, key sizing,
rotor stepping, turnover, double-step behavior, mutable machine state, and the
Daily Key Sheet CLI command. It also includes Enigma I reference vectors from
<https://kerryb.github.io/enigma/>.

## Linting And Formatting

Recommended development checks:

```bash
python3 -m pytest
python3 -m ruff check enigma tests
python3 -m ruff format .
```

Optional type checking:

```bash
python3 -m mypy enigma
```

GitHub Actions runs tests with coverage, Ruff, and mypy on Python 3.10, 3.11,
3.12, and 3.13.

## Release Preparation

Before tagging a release:

```bash
git status
python3 -m pytest
python3 -m ruff check enigma tests
python3 -m mypy enigma
```

Review `CHANGELOG.md`, confirm the version in `pyproject.toml`, create an
annotated tag, and attach a release description summarizing compatibility,
validation, and test coverage changes. Do not publish to PyPI unless package
distribution is an explicit goal for that release.

## Limitations

- Does not simulate mechanical wear.
- Does not simulate electromechanical latency.
- Does not implement the Uhr switch box.
- Does not implement an expanded plugboard beyond standard pair swapping.
- Does not implement full naval indicator procedures.
- Does not model operator mistakes or message-key traffic analysis workflows.
- Does not provide modern cryptographic security and should not be used to
  protect real data.

## Roadmap

- Add more historical known-answer vectors.
- Add richer examples for M4 key-sheet workflows.
- Expand type coverage where it improves readability.
- Keep the public API stable while tightening validation around invalid input.
- Raise coverage threshold from 80% to 90% after extracting and testing CLI
  command logic.
- Preserve the small, explicit architecture for educational use.
