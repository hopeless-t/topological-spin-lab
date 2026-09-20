from __future__ import annotations

import numpy as np
import pytest

from topological_spin_lab.models.surface_dirac import surface_dirac_hamiltonian
from topological_spin_lab.observables.spectrum import eigensystem
from topological_spin_lab.observables.spin import in_plane_helicity, spin_expectation


def test_upper_band_spin_for_positive_kx_is_positive_y() -> None:
    energies, states = eigensystem(surface_dirac_hamiltonian(0.1, 0.0, 1.0))
    assert energies[1] > 0
    spin = spin_expectation(states[:, 1])
    np.testing.assert_allclose(spin, [0.0, 1.0, 0.0], atol=1e-14)


def test_upper_band_spin_for_positive_ky_is_negative_x() -> None:
    energies, states = eigensystem(surface_dirac_hamiltonian(0.0, 0.1, 1.0))
    assert energies[1] > 0
    spin = spin_expectation(states[:, 1])
    np.testing.assert_allclose(spin, [-1.0, 0.0, 0.0], atol=1e-14)


def test_helicity_is_undefined_at_dirac_point() -> None:
    with pytest.raises(ValueError, match="undefined"):
        in_plane_helicity(np.array([1.0, 0.0, 0.0]), 0.0, 0.0)
