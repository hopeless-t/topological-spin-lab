from __future__ import annotations

from pathlib import Path

import numpy as np

import topological_spin_lab.experiments.exp001 as exp001
from topological_spin_lab.results import ExperimentStatus
from topological_spin_lab.spec import load_experiment_spec

ROOT = Path(__file__).resolve().parents[1]
SPEC = load_experiment_spec(ROOT / "specs" / "EXP-001.json")


def test_canonical_exp001_passes() -> None:
    result = exp001.execute_exp001(SPEC)
    assert result.status is ExperimentStatus.PASS
    assert all(check.passed for check in result.checks)


def test_exp001_is_deterministic_in_same_runtime() -> None:
    first = exp001.execute_exp001(SPEC)
    second = exp001.execute_exp001(SPEC)
    assert first == second


def test_time_reversal_relation_is_satisfied() -> None:
    result = exp001.execute_exp001(SPEC)
    assert result.metrics.max_time_reversal_residual_eV <= SPEC.acceptance.time_reversal_abs_eV


def test_broken_model_is_detected_as_fail(monkeypatch) -> None:
    original = exp001.surface_dirac_hamiltonian

    def broken(kx_Ainv: float, ky_Ainv: float, alpha_eV_A: float):
        h = original(kx_Ainv, ky_Ainv, alpha_eV_A)
        return h + np.array([[0.01, 0.0], [0.0, 0.01]], dtype=np.complex128)

    monkeypatch.setattr(exp001, "surface_dirac_hamiltonian", broken)
    result = exp001.execute_exp001(SPEC)
    assert result.status is ExperimentStatus.FAIL
    assert any(not check.passed for check in result.checks)


def test_status_is_derived_from_checks() -> None:
    result = exp001.execute_exp001(SPEC)
    assert "status" not in result.__dataclass_fields__
