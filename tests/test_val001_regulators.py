from __future__ import annotations

from pathlib import Path

import numpy as np

from topological_spin_lab.spec_val001 import load_val001_spec
from topological_spin_lab.validation.regulators import (
    build_stacey_system,
    build_wilson_system,
)
from topological_spin_lab.validation.val001 import _solve_wilson

ROOT = Path(__file__).resolve().parents[1]
SPEC = load_val001_spec(ROOT / "specs" / "VAL-001.json")


def test_wilson_matrix_is_hermitian() -> None:
    system = build_wilson_system(
        grid_points=61,
        half_window_A=600.0,
        ky_Ainv=0.02,
        alpha_eV_A=1.0,
        mass_magnitude_eV=0.02,
        wall_width_A=50.0,
        orientation="negative_to_positive",
        wilson_r=0.5,
    )
    np.testing.assert_allclose(
        system.hamiltonian_eV,
        system.hamiltonian_eV.conj().T,
        rtol=0.0,
        atol=1e-14,
    )


def test_stacey_generalized_problem_is_hermitian_and_positive() -> None:
    system = build_stacey_system(
        grid_points=61,
        half_window_A=600.0,
        ky_Ainv=0.02,
        alpha_eV_A=1.0,
        mass_magnitude_eV=0.02,
        wall_width_A=50.0,
        orientation="negative_to_positive",
    )
    np.testing.assert_allclose(
        system.hamiltonian_eV,
        system.hamiltonian_eV.conj().T,
        rtol=0.0,
        atol=1e-14,
    )
    np.testing.assert_allclose(
        system.metric,
        system.metric.conj().T,
        rtol=0.0,
        atol=1e-14,
    )
    assert float(np.min(np.linalg.eigvalsh(system.metric))) > 0.0


def test_ghost_classifier_rejects_naive_r_zero_but_accepts_wilson() -> None:
    naive = _solve_wilson(
        SPEC,
        grid_points=121,
        ky_Ainv=0.02,
        orientation="negative_to_positive",
        wilson_r=0.0,
    )
    regulated = _solve_wilson(
        SPEC,
        grid_points=121,
        ky_Ainv=0.02,
        orientation="negative_to_positive",
        wilson_r=0.5,
    )

    assert naive.ghost_wall_modes >= 1
    assert regulated.ghost_wall_modes == 0
    assert regulated.boundary_artifact_count <= 1
