# Enigma Machine Python

## Overview

`enigma-machine-python` is a small educational simulator for the historical
Enigma machine. It supports Wehrmacht/Naval three-rotor operation and Naval M4
operation with a Greek rotor and thin reflector.

The package keeps the project split into clear layers:

```text
configuration -> construction -> machine execution -> interface
```

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

Or, once installed (`pip install -e .`), the console script:

```bash
enigma-machine
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

### Daily Key Sheet Mode

Option `0` simulates the historical two-stage daily key procedure instead of
encrypting a message directly:

1. **Daily settings** (shared by every message sent that day): rotor order,
   ring settings, reflector, and plugboard pairs.
2. **Ground setting**: a 3-letter starting position. The sending operator sets
   the rotors here before enciphering their chosen message key.
3. **Encrypted message key**: a 3-letter value the sending operator transmits
   ahead of the message. Starting from the ground setting, decrypting it
   recovers the plaintext message key.
4. The recovered message key becomes the starting position for the message
   itself: the plaintext is encrypted from that position, and the report
   decrypts the ciphertext back from the same position to show the round
   trip succeeds.

The command reports the daily settings, the decrypted message key, and the
plaintext/ciphertext/decrypted message, in that order.

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

Direct construction, for reusing one machine across several calls:

```python
from enigma import EnigmaConfig, EnigmaMachine

config = EnigmaConfig(
    rotor_order=("I", "II", "III"),
    ring_settings=(1, 1, 1),
    key="ABC",
    reflector_name="B",
    plugboard_pairs=[("A", "B"), ("C", "D")],
)

machine = EnigmaMachine.from_config(config)
ciphertext = machine.process_text("ATTACK AT DAWN")

machine.reset()  # rewind to the initial rotor positions
```

## Public API Contract

The supported public API is:

- `enigma.enigma_process`
- `enigma.EnigmaConfig`
- `enigma.EnigmaMachine`
- `enigma.MachineModeName`
- `enigma.ReflectorName`
- `enigma.GreekRotorName`
- `enigma.Plugboard`
- `enigma.Rotor`, `enigma.RotorSpec`, and `enigma.RotorState`

`enigma_process()` is the preferred high-level API. It builds a fresh machine for
each call, normalizes only ASCII a-z to uppercase. Every other non-A-Z character is
preserved unchanged and does not advance rotors, including Unicode letters
whose Unicode uppercase form would expand or become an ASCII letter.
`process_char()` requires exactly one character and rejects invalid input with
`ValueError` before changing rotor state.

Invalid user configuration raises `ValueError`. Expected validation failures
include unsupported modes, invalid rotor names, repeated moving rotors, ring
settings outside 1-26, incorrectly sized keys, incompatible reflectors, invalid
Greek rotors, and invalid plugboard pairs. `EnigmaConfig` validates every field
in `__post_init__`, on every construction path.

`EnigmaMachine.from_config()` returns a fresh machine built from an
already-validated `EnigmaConfig`. Construction â€” through `from_config` or by
calling `EnigmaMachine()` directly â€” always defensively clones the rotors
passed in, so separate machines never share stepping state, even when built
from the same `Rotor` objects. Call `machine.reset()` to rewind a machine to
the rotor positions it was constructed with, without building a new one.

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
rotor_order = ("I", "II", "III")
```

Supported moving rotors are `I`, `II`, `III`, `IV`, and `V`. A moving rotor
cannot be repeated in the same configuration. Only ASCII a-z input is
normalized to uppercase; see "Strict ASCII validation" below.

## Ring Settings

Ring settings are one-based integers from 1 to 26:

```python
ring_settings = (1, 14, 26)
```

Three-rotor modes require three ring settings. M4 requires four ring settings:
three for the moving rotors and one for the Greek rotor.

## Initial Positions

The `key` argument sets the starting window positions:

```python
key = "ABC"
```

Three-rotor modes require three letters. M4 requires four letters. Only ASCII a-z input is
normalized to uppercase before processing. Every other non-A-Z character is
preserved and does not advance rotors.

### Strict ASCII validation (breaking change)

Keys strip leading/trailing whitespace only, then require exactly three ASCII
letters for three-rotor modes or four for M4. ASCII a-z is normalized to A-Z;
internal whitespace, digits, separators and non-ASCII characters are rejected
with `ValueError` and the existing `Key must contain exactly N letters` message.
For example, `" abc "` is accepted as `ABC`, but `Aß`, `ıBC`, `ſBC`, `A1BC`
and `a b c` are rejected. The previous Unicode expansion and silent character
filtering behavior is no longer supported.

Plugboard pairs likewise accept only ASCII letters, in either case. Unicode
case aliases such as `ı` and `ſ` are rejected like `ß`, including in the CLI.
Validation messages remain unchanged.

`rotor_order`, `reflector_name`, and `greek_rotor_name` follow the same rule:
each is normalized with ASCII-only uppercasing before being checked against
its fixed set of valid names. A Unicode case alias no longer silently passes
as a different, valid name — for example, `rotor_order=("ı", "II", "III")`
previously normalized to `("I", "II", "III")` and was accepted; it now raises
`ValueError`. The three matching CLI prompts (`prompt_rotor_order`,
`prompt_reflector`, `prompt_greek_rotor`) enforce the same rule.

`enigma.alphabet.ascii_upper` provides the shared normalization rule used by
every site above: it uppercases only ASCII a-z and preserves every other
character exactly, so it can never expand a single character into several
(unlike `str.upper()`, e.g. `"ß".upper() == "SS"`). Message processing uses
it too, and still preserves non-ASCII characters without stepping rotors.

## Plugboard

Plugboard pairs are bidirectional:

```python
plug_pairs = [("A", "B"), ("C", "D")]
```

Rules:

- Maximum of 10 pairs.
- Each pair must contain two A-Z letters.
- A letter can appear in only one pair.
- Only ASCII a-z pair input is normalized to uppercase.

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

## Historical Accuracy: Ring Setting Does Not Move the Turnover Notch

Turnover notches trigger at a fixed window letter (e.g. rotor III always
turns over at `V`), regardless of ring setting. This is a common source of
bugs in Enigma simulators, including an earlier version of this one, so it's
documented here explicitly.

The confusion is understandable: the ring setting (`Ringstellung`) genuinely
does shift the *wiring* offset used during encoding (`Rotor.encode_forward`
and `encode_backward` correctly apply `position - ring`), so it's a natural
but incorrect assumption that the same offset should apply to notch
detection. It shouldn't, because of where the notch physically lives. The
alphabet ring â€” the part that both carries the turnover notch and shows the
window letter â€” can be rotated relative to the internal wiring core (that
rotation *is* the ring setting), but the notch and the window letter are
fixed to each other on that same ring. Turning the ring setting knob moves
the wiring relative to the notch; it never moves the notch relative to the
window.

An earlier version of `Rotor.at_notch()` incorrectly folded the ring setting
into the turnover check:

```python
# Incorrect: couples turnover to ring setting
return (self.position + self.ring) % 26 in self.notches
```

This meant any configuration using a non-default ring setting â€” the
historically normal case, not the exception â€” would step the wrong rotor on
the wrong keystroke, silently diverging from a real Enigma's keystream past
the first turnover. It shipped unnoticed because the only ring-setting test
vector in the suite (`ring_settings=(20, 13, 5)`, `HELLOWORLD`) happens not
to trigger a turnover in ten characters, so the bug was inert in every
existing test.

It was caught by cross-checking the mechanical explanation against an
independent implementation (`aylvisaker/python-enigma`, whose stepping check
uses raw position with no ring term) and confirming the corrected formula:

```python
# Correct: turnover depends only on the window letter
return self.position in self.notches
```

still passes the full existing suite, then adding a regression test with a
non-default ring setting chosen specifically so the old and new formulas
predict turnover on different keystrokes (`test_turnover_notch_is_independent_of_ring_setting`
in `tests/test_machine.py`), closing the coverage gap that let it ship.

## Tests

Install development tools with `python -m pip install -e ".[dev]"`.
The runtime package has no dependencies. Run the complete suite with:

```bash
python -m pytest --cov=enigma --cov-branch
python -m ruff check enigma tests
python -m ruff format --check .
python -m mypy enigma tests
```

`pyproject.toml` owns the 90% coverage threshold. Tests use strict markers,
strict configuration, warnings as errors, strict xfails, and randomized order.
The `slow` marker is registered for future expensive checks; the current full
suite runs in about five seconds on the development machine, including coverage.
Reproduce an order with `--randomly-seed=<reported-seed>`; Hypothesis also prints
reproduction information on failure.

Coverage includes all 60 ordered moving-rotor triples with both three-rotor
modes and reflectors, and all BETA/GAMMA and thin-reflector combinations.
Hypothesis varies Unicode/ASCII text, keys, rings and disjoint plugboard pairs.
Tests cover inverse permutations, reciprocity, no fixed points, exact reset and
continuation, state isolation, immutable settings, validation messages, the
public imports/signature, and CLI error-and-exit behavior (there is no re-prompt).
The full-period checks start at AAA, verify 16,900 distinct windows and 26
double-steps, and keep the Greek rotor fixed for M4. Notch checks exhaust every
ring and window; turnover sequences cover every ordered triple.

Published Enigma I examples come from <https://kerryb.github.io/enigma/>.
The same I-V/B examples also exercise the compatible naval three-rotor mode.
For M4 BETA/GAMMA and non-default-ring turnover cases, `tests/reference_enigma.py`
implements an independent contact-pair model from the published wiring at
<https://www.cryptomuseum.com/crypto/enigma/wiring.htm>, without importing
`enigma`. These are explicitly differential tests, not claimed historical
message vectors. Published examples anchor the reference model separately.
`tests/test_known_answers.py` remains the pre-refactor characterization set;
its 225 string/number literals are unchanged.

### Mutation testing (local development only)

Cosmic Ray 8.7.0 is isolated in the optional `mutation` extra. Install it with
`python -m pip install -e ".[dev,mutation]"`. CI installs only `dev`, so it
neither installs nor runs Cosmic Ray.
The runner copies the source and tests into a new directory outside the
checkout so mutations cannot edit the working tree:

```bash
python tools/mutation.py /absolute/path/to/new-mutation-run
```

On Windows, use an absolute Windows path for that argument. The output contains
`mutation.toml`, source hashes, `session.sqlite` and complete `results.json`,
including survivor diffs. The targets are `rotors`, `machine`, `plugboard`, `config`, `modes`, and now
`alphabet` so the shared ASCII normalizer is also mutated. The complete suite
runs with fixed random/Hypothesis seeds.
The timeout is 30 seconds per mutant. Preserve each run for before/after comparison.
Annotation-only and equivalent-in-domain mutants must be reported separately;
never change an expected ciphertext to kill or accommodate a mutant.

### Recorded mutation results (2026-11-01)

| Snapshot | Mutants | Killed | Survived | Raw score |
| --- | ---: | ---: | ---: | ---: |
| Baseline `bc80ac6`, 79 tests | 500 | 408 | 92 | 81.60% |
| Character fixes and stricter tests, before plugboard cleanup | 525 | 455 | 70 | 86.67% |
| Before strict ASCII validation, 845 tests | 509 | 445 | 64 | 87.43% |

All use Cosmic Ray 8.7.0's standard operators on the five core modules.
The denominator changes because character validation adds mutation sites and
removing redundant plugboard conditions removes sites. Counts are raw: no
survivors are subtracted to inflate the score. The final run completed without
incompetent mutants, worker errors or timeouts. All 22 originally actionable
survivors were killed in the intermediate run; the final run additionally
kills the incorrectly sized inverse-table mutant. The five redundant-length
survivors disappeared with their production conditions.

The final 64 survivors comprise 55 changes solely to deferred annotations,
eight accepted equivalents listed below, and one intentionally unpinned
internal `validate_mode` keyword/positional signature. Annotation changes are
not claimed equivalent under introspection; they are outside the runtime
cipher-test target. All survivor diffs remain in the runner's `results.json`.

| Accepted equivalent | Reason within the supported domain |
| --- | --- |
| Key length `!=` to `is not` | CPython shares integer counts 3 and 4. |
| Construction `zip(strict=False)` | Validated sequences have matching lengths. |
| Reset `zip(strict=False)` | Rotor/snapshot counts match absent external structural edits. |
| Window rotor count `== 4` to `>= 4` | Supported construction has only 3 or 4 rotors. |
| Mode moving-rotor count `!=` to `is not` | CPython shares integer count 3. |
| Mode ring count `!=` to `is not` | CPython shares integer counts 3 and 4. |
| Inverse-table initial value 0 to 1 | Valid permutations overwrite every entry. |
| Inverse-table initial value 0 to -1 | Valid permutations overwrite every entry. |

Coverage after strict ASCII validation is 99.49% (469/470 statements,
116/118 branches). Remaining
coverage gaps are the CLI module-entry invocation and the always-true
right-rotor stepping decision. These are retained in the coverage denominator.

## Linting And Formatting

Recommended development checks:

```bash
python3 -m pytest
python3 -m ruff check enigma tests
python3 -m ruff format .
```

Type checking (strict):

```bash
python3 -m mypy enigma tests
```

GitHub Actions runs tests with coverage, Ruff (lint and format check), and
mypy on Python 3.10, 3.11, 3.12, and 3.13.

To catch Ruff's checks before committing, install the pinned pre-commit hooks
once per clone:

```bash
pip install pre-commit
pre-commit install
```

## Release Preparation

Before tagging a release:

```bash
git status
python3 -m pytest
python3 -m ruff check enigma tests
python3 -m ruff format .
python3 -m mypy enigma tests
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
- Preserve the small, explicit architecture for educational use.
