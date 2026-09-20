from __future__ import annotations

import json
from pathlib import Path

from topological_spin_lab.evidence import write_evidence
from topological_spin_lab.experiments.exp001 import execute_exp001
from topological_spin_lab.provenance import Provenance
from topological_spin_lab.spec import load_experiment_spec

ROOT = Path(__file__).resolve().parents[1]


def test_evidence_writer_serializes_existing_result(tmp_path: Path) -> None:
    spec = load_experiment_spec(ROOT / "specs" / "EXP-001.json")
    result = execute_exp001(spec)
    provenance = Provenance(
        git_commit="deadbeef",
        python_version="test-python",
        numpy_version="test-numpy",
        platform="test-platform",
    )

    paths = write_evidence(spec, result, provenance, tmp_path)

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    metrics = json.loads(paths.metrics.read_text(encoding="utf-8"))

    assert manifest["status"] == "PASS"
    assert manifest["git_commit"] == "deadbeef"
    assert metrics["status"] == "PASS"
    assert len(metrics["checks"]) == len(result.checks)
    assert paths.spectrum.exists()
    assert paths.spin_ring.exists()
