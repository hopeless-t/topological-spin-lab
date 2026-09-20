from __future__ import annotations

import math
from typing import Literal

import numpy as np
from numpy.typing import NDArray


def analytic_energies(
    kx_Ainv: float,
    ky_Ainv: float,
    alpha_eV_A: float,
) -> NDArray[np.float64]:
    """Return the ordered analytic energies [-alpha|k|, +alpha|k|]."""
    values = (kx_Ainv, ky_Ainv, alpha_eV_A)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("Analytic inputs must be finite.")
    if alpha_eV_A <= 0.0:
        raise ValueError("alpha_eV_A must be positive.")

    radius = math.hypot(kx_Ainv, ky_Ainv)
    energy = alpha_eV_A * radius
    return np.array([-energy, energy], dtype=np.float64)


def analytic_spin(
    kx_Ainv: float,
    ky_Ainv: float,
    band: Literal["lower", "upper"],
) -> NDArray[np.float64]:
    """Return the analytic spin expectation for a nonzero momentum."""
    radius = math.hypot(kx_Ainv, ky_Ainv)
    if radius == 0.0:
        raise ValueError("Spin direction is undefined at k=0.")
    if band not in {"lower", "upper"}:
        raise ValueError("band must be 'lower' or 'upper'.")

    upper = np.array(
        [-ky_Ainv / radius, kx_Ainv / radius, 0.0],
        dtype=np.float64,
    )
    return upper if band == "upper" else -upper
