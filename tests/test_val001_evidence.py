from __future__ import annotations

import csv
import json
from pathlib import Path

from topological_spin_lab.provenance import Provenance
from topological_spin_lab.results import ExperimentStatus
from topological_spin_lab.spec_val001 import load_val001_spec
from topological_spin_lab.validation.evidence import write_val001_evidence
from topological_spin_lab.validation.val001 import (
    Val001MethodSummary,
    Val001Observation,
    Val001Result,
    ValidationGate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_val001_evidence_writer_serializes_existing_result(tmp_path: Path) -> None:
    spec = load_val001_spec(ROOT / "specs" / "VAL-001.json")
    observation = Val001Observation(
        method="stacey",
        grid_points=61,
        dx_over_xi=0.4,
        ky_Ainv=0.02,
        orientation="negative_to_positive",
        wilson_r=None,
        target_energy_eV=0.02,
        analytic_energy_eV=0.02,
        energy_error_eV=0.0,
        target_overlap=1.0,
        profile_l1_error=0.01,
        target_wall_weight=0.99,
        target_edge_weight=0.0,
        target_spin_x=-1.0,
        spin_x_error=0.0,
        in_gap_count=2,
        wall_localized_count=1,
        boundary_artifact_count=1,
        other_in_gap_count=0,
        ghost_wall_modes=0,
        matrix_hermiticity_residual_eV=0.0,
        p_hermiticity_residual=0.0,
        p_min_eigenvalue=0.01,
        p_condition_number=100.0,
        solver_seconds=0.1,
    )
    summary = Val001MethodSummary(
        method="stacey",
        wilson_r=None,
        hard_pass=True,
        failed_gates=(),
        max_energy_error_eV=0.0,
        min_target_overlap=1.0,
        max_profile_l1_error=0.01,
        finest_profile_l1_error=0.001,
        min_target_wall_weight=0.99,
        max_target_edge_weight=0.0,
        max_spin_x_error=0.0,
        max_ghost_wall_modes=0,
        max_boundary_artifacts=1,
        max_other_in_gap_modes=0,
        max_matrix_hermiticity_residual_eV=0.0,
        max_p_hermiticity_residual=0.0,
        min_p_eigenvalue=0.01,
        max_p_condition_number=100.0,
        monotone_profile_convergence=True,
        profile_l1_by_grid=((61, 0.01), (121, 0.003), (241, 0.001)),
        total_solver_seconds=0.1,
    )
    result = Val001Result(
        validation_id="VAL-001",
        gates=(
            ValidationGate(
                name="synthetic",
                passed=True,
                observed="PASS",
                requirement="test",
            ),
        ),
        observations=(observation,),
        method_summaries=(summary,),
        spectral_validator="stacey",
        best_wilson_r=0.5,
        transport_candidate="wilson:r=0.5",
        transport_authorized=False,
        total_solver_seconds=0.1,
    )
    assert result.status is ExperimentStatus.PASS

    paths = write_val001_evidence(
        spec,
        result,
        Provenance(
            git_commit="deadbeef",
            python_version="test-python",
            numpy_version="test-numpy",
            platform="test-platform",
        ),
        tmp_path,
    )

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    summary_json = json.loads(paths.summary.read_text(encoding="utf-8"))
    with paths.observations.open(encoding="utf-8", newline="") as handle:
        observations = list(csv.DictReader(handle))

    assert manifest["validation_id"] == "VAL-001"
    assert manifest["git_commit"] == "deadbeef"
    assert summary_json["status"] == "PASS"
    assert len(observations) == 1
    assert paths.method_summary.exists()
    assert paths.performance.exists()
