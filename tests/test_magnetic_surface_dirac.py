from __future__ import annotations

import numpy as np

from topological_spin_lab.models.magnetic_surface_dirac import (
    magnetic_surface_dirac_hamiltonian,
)
from topological_spin_lab.models.surface_dirac import surface_dirac_hamiltonian


def test_known_magnetic_matrix() -> None:
    h = magnetic_surface_dirac_hamiltonian(0.25, 0.0, 2.0, 0.1)
    expected = np.array(
        [[0.1, -0.5j], [0.5j, -0.1]],
        dtype=np.complex128,
    )
    np.testing.assert_allclose(h, expected, atol=0.0, rtol=0.0)


def test_magnetic_hamiltonian_is_hermitian() -> None:
    h = magnetic_surface_dirac_hamiltonian(0.03, -0.07, 1.2, -0.04)
    np.testing.assert_allclose(h, h.conj().T, atol=0.0, rtol=0.0)


def test_zero_mass_reduces_to_massless_model() -> None:
    massive = magnetic_surface_dirac_hamiltonian(0.03, -0.07, 1.2, 0.0)
    massless = surface_dirac_hamiltonian(0.03, -0.07, 1.2)
    np.testing.assert_allclose(massive, massless, atol=0.0, rtol=0.0)
