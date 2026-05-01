# Changelog

## Unreleased

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
- Added compatibility wrappers for older root-level imports.

### Changed

- Refactored the project from flat modules into a package-based architecture.
- Refactored CLI flow using command classes.
- Moved engine responsibilities out of the previous monolithic processing flow.
- Updated README instructions for the new package structure and test commands.

### Fixed

- Removed engine-side printing. Core logic now returns values or raises
  exceptions.
- Eliminated duplicated machine construction between CLI and engine paths.

### Notes

- Invalid plugboard pairs now raise `ValueError` in engine code instead of
  being printed and silently discarded.

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
