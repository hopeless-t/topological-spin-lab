from __future__ import annotations

import math
from pathlib import Path

import numpy as np

import topological_spin_lab.experiments.exp002 as exp002
from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.results import ExperimentStatus
from topological_spin_lab.spec_exp002 import Exp002Spec

ROOT = Path(__file__).resolve().parents[1]
SPEC = load_any_experiment_spec(ROOT / "specs" / "EXP-002.json")
assert isinstance(SPEC, Exp002Spec)


def test_canonical_exp002_passes() -> None:
    result = exp002.execute_exp002(SPEC)
    assert result.status is ExperimentStatus.PASS
    assert all(check.passed for check in result.checks)


def test_canonical_gap_is_two_abs_mass() -> None:
    result = exp002.execute_exp002(SPEC)
    zero = min(result.spectrum, key=lambda point: abs(point.kx_Ainv))
    observed_gap = zero.upper_eV - zero.lower_eV
    assert math.isclose(
        observed_gap,
        2.0 * abs(SPEC.model.mass_eV),
        rel_tol=0.0,
        abs_tol=SPEC.acceptance.direct_gap_abs_eV,
    )


def test_upper_band_spin_tilts_out_of_plane() -> None:
    result = exp002.execute_exp002(SPEC)
    upper = next(point for point in result.spin_ring if point.band == "upper")
    radius = SPEC.sampling.spin_ring.radius_Ainv
    expected_sz = SPEC.model.mass_eV / math.sqrt(
        (SPEC.model.alpha_eV_A * radius) ** 2 + SPEC.model.mass_eV**2
    )
    assert math.isclose(
        upper.sz,
        expected_sz,
        rel_tol=0.0,
        abs_tol=SPEC.acceptance.spin_vector_abs,
    )


def test_time_reversal_breaking_and_mass_flip_contract() -> None:
    result = exp002.execute_exp002(SPEC)
    assert (
        result.metrics.max_tr_breaking_magnitude_error_eV
        <= SPEC.acceptance.tr_breaking_magnitude_abs_eV
    )
    assert (
        result.metrics.max_tr_mass_flip_residual_eV
        <= SPEC.acceptance.tr_mass_flip_abs_eV
    )


def test_exp002_is_deterministic_in_same_runtime() -> None:
    first = exp002.execute_exp002(SPEC)
    second = exp002.execute_exp002(SPEC)
    assert first == second


def test_broken_identity_shift_is_detected_as_fail(monkeypatch) -> None:
    original = exp002.magnetic_surface_dirac_hamiltonian

    def broken(
        kx_Ainv: float,
        ky_Ainv: float,
        alpha_eV_A: float,
        mass_eV: float,
    ):
        h = original(kx_Ainv, ky_Ainv, alpha_eV_A, mass_eV)
        return h + np.eye(2, dtype=np.complex128) * 0.01

    monkeypatch.setattr(exp002, "magnetic_surface_dirac_hamiltonian", broken)
    result = exp002.execute_exp002(SPEC)
    assert result.status is ExperimentStatus.FAIL
    assert any(not check.passed for check in result.checks)


def test_missing_mass_term_is_detected_as_fail(monkeypatch) -> None:
    def broken(
        kx_Ainv: float,
        ky_Ainv: float,
        alpha_eV_A: float,
        mass_eV: float,
    ):
        del mass_eV
        return exp002.np.array(
            [
                [0.0, -alpha_eV_A * (ky_Ainv + 1j * kx_Ainv)],
                [-alpha_eV_A * (ky_Ainv - 1j * kx_Ainv), 0.0],
            ],
            dtype=np.complex128,
        )

    monkeypatch.setattr(exp002, "magnetic_surface_dirac_hamiltonian", broken)
    result = exp002.execute_exp002(SPEC)
    assert result.status is ExperimentStatus.FAIL
    assert any(check.name == "direct_gap" and not check.passed for check in result.checks)
