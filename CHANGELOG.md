# Changelog

## Unreleased

### Test suite hardening

- Expand the suite from 79 to 845 tests; reach 99.49% combined coverage.
  Raw mutation score improves from 408/500 (81.60%) to 445/509 (87.43%).
  Remaining mutants are 55 deferred annotations, eight accepted equivalents,
  and one intentionally unpinned internal signature; all are documented.

- Remove redundant plugboard length checks; A-Z membership already rejects
  empty and multi-character values with the same message. Pin existing Unicode
  configuration normalization without changing its behavior, and verify that
  every rotor has exactly 26 forward and inverse contacts.
- Normalize only ASCII a-z in message processing; preserve all other non-A-Z
  characters unchanged without stepping. Reject empty, multi-character and
  non-string `process_char` input before advancing any rotor.
- Add exhaustive rotor/reflector combinations, generated cipher properties,
  all-ring inverse/notch checks, and 16,900-step period checks with exactly
  26 double-steps. Cover immutable settings, independent machine state,
  validation branches/messages, public imports/signature and CLI error exits.
- Add an independent contact-pair reference model based on published wiring
  for differential M4 and non-default-ring turnover checks; retain the
  historical-vector/characterization distinction.
- Type-check tests as well as the package. Changes to the characterization
  vectors are annotation-only, with all 225 string/number literals verified
  unchanged mechanically.
- Enforce strict pytest settings, warnings as errors, randomized order and
  pytest lint rules. Raise coverage to 90% with pyproject.toml as the only
  threshold source. Add development-only Hypothesis and Cosmic Ray tooling,
  including mutation execution in a separate copy outside the checkout.


The construction-model refactor simplifies the implementation in the spirit of
PEP 20. Its cipher outputs remain pinned by `tests/test_known_answers.py` across
wehrmacht, naval, and M4 configurations. The character-handling fix above
intentionally changes non-ASCII normalization.

### Breaking changes

- Removed `EnigmaConfigBuilder` and `EnigmaFactory`. Build settings directly
  with `EnigmaConfig(...)` and construct a machine with
  `EnigmaMachine.from_config(config)`.
- Removed `text` from `EnigmaConfig`. Pass text to `machine.process_text(text)`
  or `enigma_process(text=...)` instead; `enigma_process`'s signature is
  unchanged.
- Renamed `EnigmaConfig.positions` to `key` and `EnigmaConfig.greek_rotor` to
  `greek_rotor_name`, matching `enigma_process`'s own parameter names.
- `RotorState` is now an immutable (frozen) dataclass; construct a new
  instance instead of mutating `ring`/`position` in place.
- Removed the `copy_rotors` parameter from `EnigmaMachine.__init__`.
  Construction always defensively clones the rotors passed in.
- An invalid `greek_rotor_name` now raises `ValueError` in every mode, not
  only M4. Three-rotor mode previously accepted any name in `ROTOR_SPECS`
  (including non-Greek rotors) for a field it never uses.
- Removed `MachineMode`, `ThreeRotorMode`, `M4Mode`, and `mode_strategy_for`
  from `enigma.modes`, replaced by data-driven `ModeSpec`/`MODE_SPECS` and a
  `validate_mode()` function.
- Removed `enigma.engine.step_rotors` (pure backward-compatibility wrapper,
  no remaining callers).
- Moved `normalize_pairs` from `enigma.engine` to `enigma.plugboard`.

### Added

- `EnigmaMachine.from_config(config)` as the machine construction entry
  point.
- `Rotor.clone()`, `Rotor.snapshot()`, and `Rotor.restore()`, replacing
  `machine.py`'s module-level `_clone_rotor`/`_snapshot_*`/`_restore_*`
  helpers.
- `tests/test_known_answers.py`, pinning ciphertext across non-default ring
  settings, plugboards, multi-turnover and double-step message lengths, and
  non-letter characters.

### Changed

- `EnigmaMachine` folds the Greek rotor into its rotor list (physical order,
  Greek first) instead of tracking it separately; `encode_signal` and
  `reset` loop over it uniformly with no `is not None` branching.
- The CLI builds one `EnigmaConfig` and one machine per command, encrypting
  then calling `machine.reset()` before decrypting, instead of building a
  second config and machine from scratch for the decrypt pass.

## 0.2.2-alpha

### Added

- Added the `enigma/` package with separated modules for configuration,
  construction, execution, modes, rotors, plugboard, observer hooks, and CLI.
- Added `EnigmaConfig` and `EnigmaConfigBuilder` for centralized
  configuration and validation.
- Added `EnigmaMachine` as the execution facade.
- Added `EnigmaFactory` to centralize machine construction.
- Added mode strategy classes for three-rotor and M4 machines.
- Added `Plugboard` with bidirectional mapping validation.
- Added `RotorSpec` and `RotorState` to separate immutable rotor definitions
  from mutable rotor state.
- Added automated regression tests under `tests/`.
- Added GitHub Actions CI for Python 3.10, 3.11, 3.12, and 3.13.
- Added coverage tooling with an initial 80% threshold.
- Added Enigma I reference-vector tests.

### Changed

- Refactored the project from flat modules into a package-based architecture.
- Refactored CLI flow using command classes.
- Moved engine responsibilities out of the previous monolithic processing flow.
- Updated README instructions for the new package structure and test commands.
- Directly constructed `EnigmaMachine` instances now defensively copy rotor
  objects by default. Compatibility helpers that historically mutate external
  rotor objects preserve their previous behavior.
- Centralized alphabet letter/index conversion helpers to avoid scattered
  string-index conversion logic.
- Clarified public API contracts, docstrings, and validation error messages for
  predictable `ValueError` failures on invalid configuration.
- Split tests by responsibility across engine, machine, config, rotors,
  plugboard, CLI, and compatibility modules.

### Fixed

- Removed engine-side printing. Core logic now returns values or raises
  exceptions.
- Eliminated duplicated machine construction between CLI and engine paths.
- Made the turnover notch independent of ring setting, so turnover happens at
  a fixed window letter as on a real Enigma machine.
- Ordered the Greek rotor last in `EnigmaMachine.window()` so its output
  matches `EnigmaConfig.positions`/`.key()` and round-trips correctly for M4.
- Made `EnigmaConfig` validate and normalize fields identically whether
  constructed directly or through `EnigmaConfigBuilder`.

### Notes

- Invalid plugboard pairs now raise `ValueError` in engine code instead of
  being printed and silently discarded.
- Coverage threshold starts at 80% and should be raised toward 90% after CLI
  command logic is extracted and tested without brittle interactive I/O tests.

## v1.0.0

Initial stable release of the Enigma Machine simulator.

### Features
- Interactive CLI interface
- Support for multiple Enigma modes (Wehrmacht, Naval, M4)
- Configurable rotors, ring settings, and reflector
- Symmetric encryption/decryption
- Modular engine for programmatic use

### Changes
- Complete rewrite from prototype implementation
- Replaced pseudo-random rotor/reflector system with structured configuration
- Improved code organization and usability
