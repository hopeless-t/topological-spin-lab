from __future__ import annotations

import json
from pathlib import Path

from topological_spin_lab.evidence import write_evidence
from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.experiments.exp002 import execute_exp002
from topological_spin_lab.provenance import Provenance
from topological_spin_lab.spec_exp002 import Exp002Spec

ROOT = Path(__file__).resolve().parents[1]


def test_exp002_evidence_writer_serializes_existing_result(tmp_path: Path) -> None:
    spec = load_any_experiment_spec(ROOT / "specs" / "EXP-002.json")
    assert isinstance(spec, Exp002Spec)
    result = execute_exp002(spec)
    provenance = Provenance(
        git_commit="deadbeef",
        python_version="test-python",
        numpy_version="test-numpy",
        platform="test-platform",
    )

    paths = write_evidence(spec, result, provenance, tmp_path)

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    metrics = json.loads(paths.metrics.read_text(encoding="utf-8"))

    assert manifest["experiment_id"] == "EXP-002"
    assert manifest["status"] == "PASS"
    assert manifest["git_commit"] == "deadbeef"
    assert metrics["status"] == "PASS"
    assert len(metrics["checks"]) == 11
    assert paths.spectrum.exists()
    assert paths.spin_ring.exists()
