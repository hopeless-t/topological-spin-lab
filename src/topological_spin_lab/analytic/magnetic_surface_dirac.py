from __future__ import annotations

import math
from typing import Literal

import numpy as np
from numpy.typing import NDArray


def analytic_magnetic_energies(
    kx_Ainv: float,
    ky_Ainv: float,
    alpha_eV_A: float,
    mass_eV: float,
) -> NDArray[np.float64]:
    values = (kx_Ainv, ky_Ainv, alpha_eV_A, mass_eV)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("Analytic inputs must be finite.")
    if alpha_eV_A <= 0.0:
        raise ValueError("alpha_eV_A must be positive.")

    radius = math.hypot(kx_Ainv, ky_Ainv)
    energy = math.sqrt((alpha_eV_A * radius) ** 2 + mass_eV**2)
    return np.array([-energy, energy], dtype=np.float64)


def analytic_magnetic_spin(
    kx_Ainv: float,
    ky_Ainv: float,
    alpha_eV_A: float,
    mass_eV: float,
    band: Literal["lower", "upper"],
) -> NDArray[np.float64]:
    if band not in {"lower", "upper"}:
        raise ValueError("band must be 'lower' or 'upper'.")

    energies = analytic_magnetic_energies(
        kx_Ainv=kx_Ainv,
        ky_Ainv=ky_Ainv,
        alpha_eV_A=alpha_eV_A,
        mass_eV=mass_eV,
    )
    energy = float(energies[1])
    if energy == 0.0:
        raise ValueError("Spin direction is undefined when k=0 and mass=0.")

    upper = np.array(
        [
            -alpha_eV_A * ky_Ainv / energy,
            alpha_eV_A * kx_Ainv / energy,
            mass_eV / energy,
        ],
        dtype=np.float64,
    )
    return upper if band == "upper" else -upper
