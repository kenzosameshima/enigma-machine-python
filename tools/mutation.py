"""Run development-only mutations on a disposable copy, never on the checkout."""

import argparse
import hashlib
import json
import shlex
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

CORE = ("rotors", "machine", "plugboard", "config", "modes", "alphabet")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", type=Path, help="new directory outside the repository"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output == root or root in output.parents:
        parser.error("output must be outside the repository")
    output.mkdir(parents=True, exist_ok=False)
    for name in ("enigma", "tests"):
        shutil.copytree(
            root / name,
            output / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for name in ("README.md", "pyproject.toml"):
        shutil.copy2(root / name, output / name)
    command = [
        Path(sys.executable).as_posix(),
        "-X",
        "utf8",
        "-m",
        "pytest",
        "-x",
        "--randomly-seed=20261101",
        "--hypothesis-seed=20261101",
    ]
    test_command = shlex.join(command)
    modules = [f"enigma/{name}.py" for name in CORE]
    config = (
        "[cosmic-ray]\n"
        + f"module-path = {json.dumps(modules)}\n"
        + "timeout = 30.0\nexcluded-modules = []\n"
        + f"test-command = {json.dumps(test_command)}\n"
        + '[cosmic-ray.distributor]\nname = "local"\n'
    )
    (output / "mutation.toml").write_text(config, encoding="utf-8")
    hashes = {
        str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
        for directory in ("enigma", "tests")
        for path in (output / directory).glob("*.py")
    }
    (output / "source-hashes.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8"
    )
    subprocess.run(command, cwd=output, check=True)
    entrypoint = [sys.executable, "-c", "from cosmic_ray.cli import main; main()"]
    for arguments in (
        ("init", "mutation.toml", "session.sqlite"),
        ("baseline", "mutation.toml"),
        ("exec", "mutation.toml", "session.sqlite"),
    ):
        subprocess.run([*entrypoint, *arguments], cwd=output, check=True)
    with sqlite3.connect(output / "session.sqlite") as connection:
        connection.row_factory = sqlite3.Row
        results = [
            dict(row)
            for row in connection.execute(
                "SELECT m.*, r.worker_outcome, r.test_outcome, r.diff "
                "FROM mutation_specs m JOIN work_results r USING(job_id) "
                "ORDER BY module_path, start_pos_row, operator_name, occurrence"
            )
        ]
    (output / "results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    counts = Counter(row["test_outcome"] for row in results)
    print(counts)
    print(f"Full results: {output / 'results.json'}")
    if counts["INCOMPETENT"] or any(
        row["worker_outcome"] != "NORMAL" for row in results
    ):
        raise SystemExit(
            "Infrastructure or incompetent mutants require inspection; see results."
        )


if __name__ == "__main__":
    main()
