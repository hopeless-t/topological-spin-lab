from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from ..models.domain_wall import orientation_sign


def localization_length_A(alpha_eV_A: float, mass_magnitude_eV: float) -> float:
    if not all(math.isfinite(float(v)) for v in (alpha_eV_A, mass_magnitude_eV)):
        raise ValueError("Inputs must be finite.")
    if alpha_eV_A <= 0.0 or mass_magnitude_eV <= 0.0:
        raise ValueError("alpha_eV_A and mass_magnitude_eV must be positive.")
    return alpha_eV_A / mass_magnitude_eV


def bound_state_spinor(orientation: str) -> NDArray[np.complex128]:
    sign = orientation_sign(orientation)
    # sigma_x eigenvalue = -sign
    return np.array([1.0, -sign], dtype=np.complex128) / math.sqrt(2.0)


def bound_state_spin(orientation: str) -> NDArray[np.float64]:
    sign = orientation_sign(orientation)
    return np.array([-sign, 0.0, 0.0], dtype=np.float64)


def bound_state_energy_eV(
    ky_Ainv: float,
    alpha_eV_A: float,
    orientation: str,
) -> float:
    if not all(math.isfinite(float(v)) for v in (ky_Ainv, alpha_eV_A)):
        raise ValueError("Inputs must be finite.")
    if alpha_eV_A <= 0.0:
        raise ValueError("alpha_eV_A must be positive.")
    return orientation_sign(orientation) * alpha_eV_A * ky_Ainv


def _beta_function(a: float, b: float) -> float:
    return math.gamma(a) * math.gamma(b) / math.gamma(a + b)


def bound_state_envelope(
    x_A: NDArray[np.float64],
    alpha_eV_A: float,
    mass_magnitude_eV: float,
    wall_width_A: float,
) -> NDArray[np.float64]:
    x = np.asarray(x_A, dtype=np.float64)
    if alpha_eV_A <= 0.0 or mass_magnitude_eV <= 0.0 or wall_width_A <= 0.0:
        raise ValueError("alpha, mass magnitude, and wall width must be positive.")

    beta = mass_magnitude_eV * wall_width_A / alpha_eV_A
    normalization = 1.0 / math.sqrt(
        wall_width_A * _beta_function(0.5, beta)
    )
    z = x / wall_width_A
    log_cosh = np.logaddexp(z, -z) - math.log(2.0)
    return normalization * np.exp(-beta * log_cosh)


def bound_state_envelope_derivative_per_A(
    x_A: NDArray[np.float64],
    alpha_eV_A: float,
    mass_magnitude_eV: float,
    wall_width_A: float,
) -> NDArray[np.float64]:
    x = np.asarray(x_A, dtype=np.float64)
    envelope = bound_state_envelope(
        x,
        alpha_eV_A,
        mass_magnitude_eV,
        wall_width_A,
    )
    return (
        -(mass_magnitude_eV / alpha_eV_A)
        * np.tanh(x / wall_width_A)
        * envelope
    )


def bulk_edge_abs_eV(
    ky_Ainv: float,
    alpha_eV_A: float,
    mass_magnitude_eV: float,
) -> float:
    return math.sqrt((alpha_eV_A * ky_Ainv) ** 2 + mass_magnitude_eV**2)
