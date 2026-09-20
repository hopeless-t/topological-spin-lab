from __future__ import annotations

import json
from pathlib import Path

from topological_spin_lab.__main__ import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_runs_exp003_and_writes_evidence(tmp_path: Path) -> None:
    output = tmp_path / "exp003"
    code = main(
        [
            "run",
            str(ROOT / "specs" / "EXP-003.json"),
            "--out",
            str(output),
        ]
    )

    assert code == 0
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["experiment_id"] == "EXP-003"
    assert manifest["status"] == "PASS"
    assert (output / "profile.csv").exists()
    assert (output / "dispersion.csv").exists()
    assert (output / "figures" / "domain_wall_profile.png").exists()
    assert (output / "figures" / "domain_wall_dispersion.png").exists()
