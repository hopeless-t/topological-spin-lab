from __future__ import annotations

import json
from pathlib import Path

from topological_spin_lab.__main__ import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_runs_exp002_and_writes_evidence(tmp_path: Path) -> None:
    output = tmp_path / "exp002"
    code = main(
        [
            "run",
            str(ROOT / "specs" / "EXP-002.json"),
            "--out",
            str(output),
        ]
    )

    assert code == 0
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["experiment_id"] == "EXP-002"
    assert manifest["status"] == "PASS"
    assert (output / "figures" / "magnetic_dirac_spectrum.png").exists()
    assert (output / "figures" / "spin_z.png").exists()
