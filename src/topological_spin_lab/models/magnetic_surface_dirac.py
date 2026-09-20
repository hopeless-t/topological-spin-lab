from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from .surface_dirac import surface_dirac_hamiltonian

_SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def magnetic_surface_dirac_hamiltonian(
    kx_Ainv: float,
    ky_Ainv: float,
    alpha_eV_A: float,
    mass_eV: float,
) -> NDArray[np.complex128]:
    """Return H = alpha(kx sigma_y - ky sigma_x) + mass sigma_z in eV."""
    if not math.isfinite(float(mass_eV)):
        raise ValueError("mass_eV must be finite.")

    return surface_dirac_hamiltonian(
        kx_Ainv=kx_Ainv,
        ky_Ainv=ky_Ainv,
        alpha_eV_A=alpha_eV_A,
    ) + mass_eV * _SIGMA_Z
