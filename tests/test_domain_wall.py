from __future__ import annotations

import math

import numpy as np

from topological_spin_lab.analytic.domain_wall import (
    bound_state_energy_eV,
    bound_state_envelope,
    bound_state_spin,
    localization_length_A,
)
from topological_spin_lab.models.domain_wall import domain_wall_mass_eV


def test_canonical_localization_length_is_50_angstrom() -> None:
    assert localization_length_A(1.0, 0.02) == 50.0


def test_mass_changes_sign_across_wall() -> None:
    left = domain_wall_mass_eV(-500.0, 0.02, 50.0, "negative_to_positive")
    center = domain_wall_mass_eV(0.0, 0.02, 50.0, "negative_to_positive")
    right = domain_wall_mass_eV(500.0, 0.02, 50.0, "negative_to_positive")
    assert left < 0.0
    assert center == 0.0
    assert right > 0.0


def test_wall_reversal_flips_spin_and_dispersion() -> None:
    primary_spin = bound_state_spin("negative_to_positive")
    reversed_spin = bound_state_spin("positive_to_negative")
    np.testing.assert_allclose(reversed_spin, -primary_spin, atol=0.0, rtol=0.0)

    primary_energy = bound_state_energy_eV(0.03, 1.0, "negative_to_positive")
    reversed_energy = bound_state_energy_eV(0.03, 1.0, "positive_to_negative")
    assert reversed_energy == -primary_energy


def test_canonical_infinite_normalization_is_captured_by_design_window() -> None:
    xi = localization_length_A(1.0, 0.02)
    x = np.linspace(-12.0 * xi, 12.0 * xi, 241)
    envelope = bound_state_envelope(x, 1.0, 0.02, 50.0)
    norm = float(np.trapezoid(envelope**2, x))
    assert math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=1e-8)
