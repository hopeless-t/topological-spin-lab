from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

_SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)


def surface_dirac_hamiltonian(
    kx_Ainv: float,
    ky_Ainv: float,
    alpha_eV_A: float,
) -> NDArray[np.complex128]:
    """Return H = alpha * (kx sigma_y - ky sigma_x) in eV."""
    values = (kx_Ainv, ky_Ainv, alpha_eV_A)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("Hamiltonian inputs must be finite.")
    if alpha_eV_A <= 0.0:
        raise ValueError("alpha_eV_A must be positive.")

    return alpha_eV_A * (kx_Ainv * _SIGMA_Y - ky_Ainv * _SIGMA_X)
