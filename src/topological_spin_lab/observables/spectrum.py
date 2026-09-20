from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def eigensystem(
    hamiltonian: NDArray[np.complex128],
) -> tuple[NDArray[np.float64], NDArray[np.complex128]]:
    """Return ascending eigenvalues and column eigenvectors without modifying H."""
    matrix = np.asarray(hamiltonian, dtype=np.complex128)
    if matrix.shape != (2, 2):
        raise ValueError("Expected a 2x2 Hamiltonian.")

    energies, eigenvectors = np.linalg.eigh(matrix)
    return energies.astype(np.float64), eigenvectors.astype(np.complex128)
