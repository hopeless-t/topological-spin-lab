from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from ..models.domain_wall import orientation_sign

_SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
_SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
_IDENTITY_2 = np.eye(2, dtype=np.complex128)


@dataclass(frozen=True, slots=True)
class WilsonSystem:
    x_A: NDArray[np.float64]
    hamiltonian_eV: NDArray[np.complex128]


@dataclass(frozen=True, slots=True)
class StaceySystem:
    x_A: NDArray[np.float64]
    interface_x_A: NDArray[np.float64]
    phi: NDArray[np.float64]
    hamiltonian_eV: NDArray[np.complex128]
    metric: NDArray[np.complex128]


def _mass_profile(
    x_A: NDArray[np.float64],
    mass_magnitude_eV: float,
    wall_width_A: float,
    orientation: str,
) -> NDArray[np.float64]:
    sign = orientation_sign(orientation)
    return sign * mass_magnitude_eV * np.tanh(x_A / wall_width_A)


def build_wilson_system(
    *,
    grid_points: int,
    half_window_A: float,
    ky_Ainv: float,
    alpha_eV_A: float,
    mass_magnitude_eV: float,
    wall_width_A: float,
    orientation: str,
    wilson_r: float,
) -> WilsonSystem:
    """Build the open-boundary 1D Wilson-Dirac reduction used by VAL-001.

    The Wilson correction has momentum-space form

        (r * alpha / a) * (1 - cos(k_x a)) * sigma_z.

    Ghost values outside the finite window are fixed to zero.
    """
    x_A = np.linspace(
        -half_window_A,
        half_window_A,
        grid_points,
        dtype=np.float64,
    )
    spacing_A = float(x_A[1] - x_A[0])

    derivative = np.zeros((grid_points, grid_points), dtype=np.float64)
    for index in range(grid_points - 1):
        derivative[index, index + 1] = 1.0 / (2.0 * spacing_A)
        derivative[index + 1, index] = -1.0 / (2.0 * spacing_A)

    wilson = np.eye(grid_points, dtype=np.float64) * (
        wilson_r * alpha_eV_A / spacing_A
    )
    for index in range(grid_points - 1):
        hopping = -wilson_r * alpha_eV_A / (2.0 * spacing_A)
        wilson[index, index + 1] = hopping
        wilson[index + 1, index] = hopping

    mass = np.diag(
        _mass_profile(
            x_A,
            mass_magnitude_eV,
            wall_width_A,
            orientation,
        )
    )

    hamiltonian = (
        -1.0j * alpha_eV_A * np.kron(derivative, _SIGMA_Y)
        - alpha_eV_A * ky_Ainv * np.kron(np.eye(grid_points), _SIGMA_X)
        + np.kron(mass + wilson, _SIGMA_Z)
    )

    return WilsonSystem(
        x_A=x_A,
        hamiltonian_eV=np.asarray(hamiltonian, dtype=np.complex128),
    )


def build_stacey_system(
    *,
    grid_points: int,
    half_window_A: float,
    ky_Ainv: float,
    alpha_eV_A: float,
    mass_magnitude_eV: float,
    wall_width_A: float,
    orientation: str,
) -> StaceySystem:
    """Build the 1D open-boundary Stacey/tangent generalized eigenproblem.

    This is a repository-specific 1D open-boundary reduction of the
    symmetrized Stacey construction:

        H psi = E P psi,
        P = Phi^dagger Phi.

    Phi averages neighboring amplitudes onto midpoint/interface locations and
    U differentiates them there. Ghost amplitudes immediately outside the
    finite window are fixed to zero. Multiplying the midpoint equation by
    Phi^dagger yields Hermitian H and positive-definite P for the finite grids
    used by VAL-001.
    """
    x_A = np.linspace(
        -half_window_A,
        half_window_A,
        grid_points,
        dtype=np.float64,
    )
    spacing_A = float(x_A[1] - x_A[0])

    # N closed-grid amplitudes are mapped to N+1 midpoint/interface equations,
    # including the two outer ghost-zero interfaces.
    phi = np.zeros((grid_points + 1, grid_points), dtype=np.float64)
    derivative = np.zeros((grid_points + 1, grid_points), dtype=np.float64)

    for interface in range(grid_points + 1):
        left = interface - 1
        right = interface

        if left >= 0:
            phi[interface, left] += 0.5
            derivative[interface, left] -= 1.0 / spacing_A

        if right < grid_points:
            phi[interface, right] += 0.5
            derivative[interface, right] += 1.0 / spacing_A

    interface_x_A = np.linspace(
        x_A[0] - 0.5 * spacing_A,
        x_A[-1] + 0.5 * spacing_A,
        grid_points + 1,
        dtype=np.float64,
    )

    p_spatial = phi.T @ phi
    derivative_spatial = phi.T @ derivative
    mass_values = _mass_profile(
        interface_x_A,
        mass_magnitude_eV,
        wall_width_A,
        orientation,
    )
    mass_spatial = (phi.T * mass_values) @ phi

    hamiltonian = (
        -1.0j * alpha_eV_A * np.kron(derivative_spatial, _SIGMA_Y)
        - alpha_eV_A * ky_Ainv * np.kron(p_spatial, _SIGMA_X)
        + np.kron(mass_spatial, _SIGMA_Z)
    )
    metric = np.kron(p_spatial, _IDENTITY_2)

    return StaceySystem(
        x_A=x_A,
        interface_x_A=interface_x_A,
        phi=phi,
        hamiltonian_eV=np.asarray(hamiltonian, dtype=np.complex128),
        metric=np.asarray(metric, dtype=np.complex128),
    )


def physicalize_stacey_state(
    state: NDArray[np.complex128],
    phi: NDArray[np.float64],
) -> NDArray[np.complex128]:
    """Map a closed-grid Stacey generalized eigenvector to interface amplitudes."""
    grid_points = phi.shape[1]
    spinor = np.asarray(state, dtype=np.complex128).reshape(grid_points, 2)
    physical = np.column_stack(
        (
            phi @ spinor[:, 0],
            phi @ spinor[:, 1],
        )
    )
    return np.asarray(physical, dtype=np.complex128)
