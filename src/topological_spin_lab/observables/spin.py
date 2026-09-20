from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

_SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
_SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def spin_expectation(
    state: NDArray[np.complex128],
) -> NDArray[np.float64]:
    """Return <sigma_x>, <sigma_y>, <sigma_z> without normalizing the state."""
    psi = np.asarray(state, dtype=np.complex128)
    if psi.shape != (2,):
        raise ValueError("Expected a two-component state vector.")

    values = np.array(
        [
            np.vdot(psi, _SIGMA_X @ psi),
            np.vdot(psi, _SIGMA_Y @ psi),
            np.vdot(psi, _SIGMA_Z @ psi),
        ],
        dtype=np.complex128,
    )
    if float(np.max(np.abs(values.imag))) > 1e-12:
        raise ValueError("Spin expectation acquired a non-negligible imaginary part.")
    return values.real.astype(np.float64)


def in_plane_helicity(
    spin: NDArray[np.float64],
    kx_Ainv: float,
    ky_Ainv: float,
) -> float:
    """Return h = (k_hat x <sigma>)_z for nonzero in-plane momentum."""
    vector = np.asarray(spin, dtype=np.float64)
    if vector.shape != (3,):
        raise ValueError("Expected a three-component spin vector.")
    radius = math.hypot(kx_Ainv, ky_Ainv)
    if radius == 0.0:
        raise ValueError("Helicity is undefined at k=0.")

    khat_x = kx_Ainv / radius
    khat_y = ky_Ainv / radius
    return float(khat_x * vector[1] - khat_y * vector[0])
