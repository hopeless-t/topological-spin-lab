from __future__ import annotations

import csv
import json
from pathlib import Path

from topological_spin_lab.evidence import write_exp003_evidence
from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.experiments.exp003 import execute_exp003
from topological_spin_lab.provenance import Provenance
from topological_spin_lab.spec_exp003 import Exp003Spec

ROOT = Path(__file__).resolve().parents[1]


def test_exp003_evidence_writer_serializes_existing_result(tmp_path: Path) -> None:
    spec = load_any_experiment_spec(ROOT / "specs" / "EXP-003.json")
    assert isinstance(spec, Exp003Spec)
    result = execute_exp003(spec)
    provenance = Provenance(
        git_commit="deadbeef",
        python_version="test-python",
        numpy_version="test-numpy",
        platform="test-platform",
    )

    paths = write_exp003_evidence(spec, result, provenance, tmp_path)

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    metrics = json.loads(paths.metrics.read_text(encoding="utf-8"))
    with paths.profile.open(encoding="utf-8", newline="") as handle:
        profile = list(csv.DictReader(handle))
    with paths.dispersion.open(encoding="utf-8", newline="") as handle:
        dispersion = list(csv.DictReader(handle))

    assert manifest["experiment_id"] == "EXP-003"
    assert manifest["status"] == "PASS"
    assert metrics["status"] == "PASS"
    assert len(metrics["checks"]) == 10
    assert len(profile) == 241
    assert len(dispersion) == 101
