from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

_SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
_SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def orientation_sign(orientation: str) -> float:
    if orientation == "negative_to_positive":
        return 1.0
    if orientation == "positive_to_negative":
        return -1.0
    raise ValueError("Unsupported domain-wall orientation.")


def domain_wall_mass_eV(
    x_A: float,
    mass_magnitude_eV: float,
    wall_width_A: float,
    orientation: str,
) -> float:
    if not all(
        math.isfinite(float(value))
        for value in (x_A, mass_magnitude_eV, wall_width_A)
    ):
        raise ValueError("Domain-wall inputs must be finite.")
    if mass_magnitude_eV <= 0.0:
        raise ValueError("mass_magnitude_eV must be positive.")
    if wall_width_A <= 0.0:
        raise ValueError("wall_width_A must be positive.")
    sign = orientation_sign(orientation)
    return sign * mass_magnitude_eV * math.tanh(x_A / wall_width_A)


def apply_domain_wall_hamiltonian(
    state: NDArray[np.complex128],
    derivative_per_A: NDArray[np.complex128],
    x_A: float,
    ky_Ainv: float,
    alpha_eV_A: float,
    mass_magnitude_eV: float,
    wall_width_A: float,
    orientation: str,
) -> NDArray[np.complex128]:
    """Apply H = -i alpha sigma_y d_x - alpha ky sigma_x + m(x) sigma_z."""
    psi = np.asarray(state, dtype=np.complex128)
    dpsi = np.asarray(derivative_per_A, dtype=np.complex128)
    if psi.shape != (2,) or dpsi.shape != (2,):
        raise ValueError("state and derivative_per_A must be two-component vectors.")
    if not math.isfinite(float(ky_Ainv)) or not math.isfinite(float(alpha_eV_A)):
        raise ValueError("Hamiltonian inputs must be finite.")
    if alpha_eV_A <= 0.0:
        raise ValueError("alpha_eV_A must be positive.")

    mass = domain_wall_mass_eV(
        x_A,
        mass_magnitude_eV,
        wall_width_A,
        orientation,
    )
    return (
        -1.0j * alpha_eV_A * (_SIGMA_Y @ dpsi)
        - alpha_eV_A * ky_Ainv * (_SIGMA_X @ psi)
        + mass * (_SIGMA_Z @ psi)
    )
