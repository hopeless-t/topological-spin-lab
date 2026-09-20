from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np

import topological_spin_lab.experiments.exp003 as exp003
from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.results import ExperimentStatus
from topological_spin_lab.spec_exp003 import Exp003Spec

ROOT = Path(__file__).resolve().parents[1]
SPEC = load_any_experiment_spec(ROOT / "specs" / "EXP-003.json")
assert isinstance(SPEC, Exp003Spec)


def test_canonical_exp003_passes() -> None:
    result = exp003.execute_exp003(SPEC)
    assert result.status is ExperimentStatus.PASS
    assert all(check.passed for check in result.checks)


def test_canonical_profile_and_dispersion_sizes() -> None:
    result = exp003.execute_exp003(SPEC)
    assert len(result.profile) == 241
    assert len(result.dispersion) == 101


def test_canonical_mode_is_localized_and_chiral() -> None:
    result = exp003.execute_exp003(SPEC)
    center = min(result.profile, key=lambda point: abs(point.x_A))
    assert center.probability_density_Ainv == max(
        point.probability_density_Ainv for point in result.profile
    )
    assert result.spin[0] < 0.0

    negative_ky = result.dispersion[0]
    positive_ky = result.dispersion[-1]
    assert negative_ky.energy_eV < 0.0
    assert positive_ky.energy_eV > 0.0
    assert all(point.binding_margin_eV > 0.0 for point in result.dispersion)


def test_reversed_wall_passes_and_reverses_chirality() -> None:
    reversed_spec = replace(
        SPEC,
        model=replace(SPEC.model, orientation="positive_to_negative"),
    )
    primary = exp003.execute_exp003(SPEC)
    reversed_result = exp003.execute_exp003(reversed_spec)

    assert reversed_result.status is ExperimentStatus.PASS
    np.testing.assert_allclose(reversed_result.spin, -np.array(primary.spin), atol=1e-12)
    for left, right in zip(primary.dispersion, reversed_result.dispersion, strict=True):
        assert abs(left.energy_eV + right.energy_eV) <= SPEC.acceptance.reversal_dispersion_abs_eV


def test_constant_mass_fault_is_detected(monkeypatch) -> None:
    original = exp003.apply_domain_wall_hamiltonian

    def broken(
        state,
        derivative_per_A,
        x_A,
        ky_Ainv,
        alpha_eV_A,
        mass_magnitude_eV,
        wall_width_A,
        orientation,
    ):
        del x_A
        return original(
            state=state,
            derivative_per_A=derivative_per_A,
            x_A=1.0e9,
            ky_Ainv=ky_Ainv,
            alpha_eV_A=alpha_eV_A,
            mass_magnitude_eV=mass_magnitude_eV,
            wall_width_A=wall_width_A,
            orientation=orientation,
        )

    monkeypatch.setattr(exp003, "apply_domain_wall_hamiltonian", broken)
    result = exp003.execute_exp003(SPEC)
    assert result.status is ExperimentStatus.FAIL
    assert any(check.name == "operator_residual" and not check.passed for check in result.checks)


def test_wrong_dispersion_sign_is_detected(monkeypatch) -> None:
    original = exp003.bound_state_energy_eV

    def broken(ky_Ainv: float, alpha_eV_A: float, orientation: str) -> float:
        return abs(original(ky_Ainv, alpha_eV_A, orientation))

    monkeypatch.setattr(exp003, "bound_state_energy_eV", broken)
    result = exp003.execute_exp003(SPEC)
    assert result.status is ExperimentStatus.FAIL
    assert any(
        check.name in {"operator_residual", "dispersion"} and not check.passed
        for check in result.checks
    )
