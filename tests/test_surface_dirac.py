from __future__ import annotations

import numpy as np

from topological_spin_lab.models.surface_dirac import surface_dirac_hamiltonian


def test_known_matrix_for_positive_kx() -> None:
    h = surface_dirac_hamiltonian(0.25, 0.0, 2.0)
    expected = np.array(
        [[0.0, -0.5j], [0.5j, 0.0]],
        dtype=np.complex128,
    )
    np.testing.assert_allclose(h, expected, atol=0.0, rtol=0.0)


def test_hamiltonian_is_hermitian() -> None:
    h = surface_dirac_hamiltonian(0.03, -0.07, 1.2)
    np.testing.assert_allclose(h, h.conj().T, atol=0.0, rtol=0.0)
