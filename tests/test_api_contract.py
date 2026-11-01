"""Check the documented imports and stable high-level calling convention."""

import inspect
import re
from pathlib import Path

import enigma


def test_documented_public_imports_and_process_signature() -> None:
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(
        encoding="utf-8"
    )
    contract = readme.split("## Public API Contract\n", 1)[1].split("\n## ", 1)[0]
    names = re.findall(r"`enigma\.([A-Za-z_]\w*)`", contract)
    assert set(enigma.__all__) == set(names)
    assert len(enigma.__all__) == len(set(enigma.__all__))
    for name in names:
        namespace: dict[str, object] = {}
        exec(f"from enigma import {name}", namespace)
        assert callable(namespace[name])
    assert str(inspect.signature(enigma.enigma_process)) == (
        "(text: 'str', key: 'str', mode: 'str' = 'wehrmacht', "
        "plug_pairs: 'Sequence[tuple[str, str]] | None' = None, "
        "rotor_order: 'Sequence[str]' = ('I', 'II', 'III'), "
        "ring_settings: 'Sequence[int]' = (1, 1, 1), "
        "reflector_name: 'str' = 'B', greek_rotor_name: 'str' = 'BETA') -> 'str'"
    )
