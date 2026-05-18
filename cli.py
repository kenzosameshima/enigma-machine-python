"""
Compatibility wrapper.

The canonical implementation lives in enigma.cli.
This module is kept to avoid breaking older imports.
"""

from enigma.cli import *  # noqa: F403
from enigma.cli import main

if __name__ == "__main__":
    main()
