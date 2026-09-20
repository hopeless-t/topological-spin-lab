from __future__ import annotations

import math

import numpy as np

from ..analytic.domain_wall import (
    bound_state_energy_eV,
    bound_state_envelope,
    bound_state_envelope_derivative_per_A,
    bound_state_spin,
    bound_state_spinor,
    bulk_edge_abs_eV,
    localization_length_A,
)
from ..models.domain_wall import apply_domain_wall_hamiltonian, domain_wall_mass_eV
from ..observables.spin import spin_expectation
from ..results import (
    CheckResult,
    DomainWallDispersionPoint,
    DomainWallProfilePoint,
    Exp003Metrics,
    Exp003Result,
)
from ..spec_exp003 import Exp003Spec


def _reverse_orientation(orientation: str) -> str:
    if orientation == "negative_to_positive":
        return "positive_to_negative"
    if orientation == "positive_to_negative":
        return "negative_to_positive"
    raise ValueError("Unsupported domain-wall orientation.")


def _energy_expectation_eV(
    x_A: np.ndarray,
    states: np.ndarray,
    h_states: np.ndarray,
) -> float:
    density = np.sum(np.abs(states) ** 2, axis=1)
    denominator = float(np.trapezoid(density, x_A))
    numerator_density = np.sum(np.conj(states) * h_states, axis=1)
    numerator = np.trapezoid(numerator_density, x_A)
    if abs(float(np.imag(numerator))) > 1e-12:
        raise ValueError("Energy expectation acquired a non-negligible imaginary part.")
    return float(np.real(numerator) / denominator)


def _operator_residual_eV(
    states: np.ndarray,
    h_states: np.ndarray,
    energy_eV: float,
) -> float:
    residual = h_states - energy_eV * states
    numerator = float(np.max(np.linalg.norm(residual, axis=1)))
    scale = float(np.max(np.linalg.norm(states, axis=1)))
    if scale == 0.0:
        raise ValueError("Bound-state amplitude vanished.")
    return numerator / scale


def _hamiltonian_action_grid(
    x_A: np.ndarray,
    envelope: np.ndarray,
    derivative: np.ndarray,
    spinor: np.ndarray,
    ky_Ainv: float,
    spec: Exp003Spec,
    orientation: str,
) -> tuple[np.ndarray, np.ndarray]:
    states = envelope[:, None] * spinor[None, :]
    derivatives = derivative[:, None] * spinor[None, :]
    h_states = np.array(
        [
            apply_domain_wall_hamiltonian(
                state=state,
                derivative_per_A=dstate,
                x_A=float(x),
                ky_Ainv=ky_Ainv,
                alpha_eV_A=spec.model.alpha_eV_A,
                mass_magnitude_eV=spec.model.mass_magnitude_eV,
                wall_width_A=spec.model.wall_width_A,
                orientation=orientation,
            )
            for x, state, dstate in zip(x_A, states, derivatives, strict=True)
        ],
        dtype=np.complex128,
    )
    return states, h_states


def execute_exp003(spec: Exp003Spec) -> Exp003Result:
    """Execute the continuum domain-wall known-answer experiment."""
    alpha = spec.model.alpha_eV_A
    mass = spec.model.mass_magnitude_eV
    width = spec.model.wall_width_A
    orientation = spec.model.orientation
    reversed_orientation = _reverse_orientation(orientation)

    xi = localization_length_A(alpha, mass)
    half_window_A = spec.sampling.profile.half_window_xi * xi
    x_A = np.linspace(
        -half_window_A,
        half_window_A,
        spec.sampling.profile.points,
        dtype=np.float64,
    )

    envelope = bound_state_envelope(x_A, alpha, mass, width)
    derivative = bound_state_envelope_derivative_per_A(x_A, alpha, mass, width)
    density = envelope**2

    finite_norm = float(np.trapezoid(density, x_A))
    finite_window_norm_error = abs(1.0 - finite_norm)
    density_symmetry_error = float(np.max(np.abs(density - density[::-1])))
    center_peak_position_abs_A = abs(float(x_A[int(np.argmax(density))]))
    mass_center_abs_eV = abs(
        domain_wall_mass_eV(0.0, mass, width, orientation)
    )

    profile = tuple(
        DomainWallProfilePoint(
            x_A=float(x),
            mass_eV=domain_wall_mass_eV(float(x), mass, width, orientation),
            probability_density_Ainv=float(probability),
        )
        for x, probability in zip(x_A, density, strict=True)
    )

    primary_spinor = bound_state_spinor(orientation)
    reversed_spinor = bound_state_spinor(reversed_orientation)
    primary_spin = spin_expectation(primary_spinor)
    reversed_spin = spin_expectation(reversed_spinor)
    expected_primary_spin = bound_state_spin(orientation)
    expected_reversed_spin = bound_state_spin(reversed_orientation)

    max_spin_vector_error = max(
        float(np.max(np.abs(primary_spin - expected_primary_spin))),
        float(np.max(np.abs(reversed_spin - expected_reversed_spin))),
    )
    max_reversal_spin_error = float(
        np.max(np.abs(reversed_spin + primary_spin))
    )

    ky_values = np.linspace(
        spec.sampling.dispersion.ky_min_Ainv,
        spec.sampling.dispersion.ky_max_Ainv,
        spec.sampling.dispersion.points,
        dtype=np.float64,
    )

    dispersion: list[DomainWallDispersionPoint] = []
    max_operator_residual = 0.0
    max_dispersion_error = 0.0
    max_in_gap_excess = 0.0
    max_reversal_dispersion_error = 0.0

    for ky_value in ky_values:
        ky = float(ky_value)
        analytic_energy = bound_state_energy_eV(ky, alpha, orientation)

        states, h_states = _hamiltonian_action_grid(
            x_A,
            envelope,
            derivative,
            primary_spinor,
            ky,
            spec,
            orientation,
        )
        numeric_energy = _energy_expectation_eV(x_A, states, h_states)
        max_operator_residual = max(
            max_operator_residual,
            _operator_residual_eV(states, h_states, analytic_energy),
        )
        max_dispersion_error = max(
            max_dispersion_error,
            abs(numeric_energy - analytic_energy),
        )

        bulk_edge = bulk_edge_abs_eV(ky, alpha, mass)
        binding_margin = bulk_edge - abs(numeric_energy)
        max_in_gap_excess = max(
            max_in_gap_excess,
            max(0.0, -binding_margin),
        )

        reversed_analytic = bound_state_energy_eV(
            ky,
            alpha,
            reversed_orientation,
        )
        reversed_states, reversed_h_states = _hamiltonian_action_grid(
            x_A,
            envelope,
            derivative,
            reversed_spinor,
            ky,
            spec,
            reversed_orientation,
        )
        reversed_numeric = _energy_expectation_eV(
            x_A,
            reversed_states,
            reversed_h_states,
        )
        max_operator_residual = max(
            max_operator_residual,
            _operator_residual_eV(
                reversed_states,
                reversed_h_states,
                reversed_analytic,
            ),
        )
        max_reversal_dispersion_error = max(
            max_reversal_dispersion_error,
            abs(reversed_numeric + numeric_energy),
            abs(reversed_analytic + analytic_energy),
        )

        dispersion.append(
            DomainWallDispersionPoint(
                ky_Ainv=ky,
                energy_eV=numeric_energy,
                analytic_energy_eV=analytic_energy,
                bulk_edge_abs_eV=bulk_edge,
                binding_margin_eV=binding_margin,
            )
        )

    metrics = Exp003Metrics(
        max_operator_residual_eV=max_operator_residual,
        finite_window_norm_error=finite_window_norm_error,
        max_density_symmetry_error_Ainv=density_symmetry_error,
        center_peak_position_abs_A=center_peak_position_abs_A,
        mass_center_abs_eV=mass_center_abs_eV,
        max_dispersion_error_eV=max_dispersion_error,
        max_in_gap_excess_eV=max_in_gap_excess,
        max_spin_vector_error=max_spin_vector_error,
        max_reversal_dispersion_error_eV=max_reversal_dispersion_error,
        max_reversal_spin_error=max_reversal_spin_error,
    )

    acceptance = spec.acceptance
    checks = (
        CheckResult(
            "operator_residual",
            metrics.max_operator_residual_eV,
            acceptance.operator_residual_eV,
            "eV",
        ),
        CheckResult(
            "finite_window_normalization",
            metrics.finite_window_norm_error,
            acceptance.finite_window_norm_abs,
            "1",
        ),
        CheckResult(
            "density_symmetry",
            metrics.max_density_symmetry_error_Ainv,
            acceptance.density_symmetry_abs_Ainv,
            "A^-1",
        ),
        CheckResult(
            "center_peak",
            metrics.center_peak_position_abs_A,
            acceptance.center_peak_abs_A,
            "A",
        ),
        CheckResult(
            "mass_center",
            metrics.mass_center_abs_eV,
            acceptance.mass_center_abs_eV,
            "eV",
        ),
        CheckResult(
            "dispersion",
            metrics.max_dispersion_error_eV,
            acceptance.dispersion_abs_eV,
            "eV",
        ),
        CheckResult(
            "in_gap",
            metrics.max_in_gap_excess_eV,
            acceptance.in_gap_excess_eV,
            "eV",
        ),
        CheckResult(
            "spin_vector",
            metrics.max_spin_vector_error,
            acceptance.spin_vector_abs,
            "1",
        ),
        CheckResult(
            "wall_reversal_dispersion",
            metrics.max_reversal_dispersion_error_eV,
            acceptance.reversal_dispersion_abs_eV,
            "eV",
        ),
        CheckResult(
            "wall_reversal_spin",
            metrics.max_reversal_spin_error,
            acceptance.reversal_spin_abs,
            "1",
        ),
    )

    return Exp003Result(
        experiment_id=spec.experiment_id,
        checks=checks,
        metrics=metrics,
        profile=profile,
        dispersion=tuple(dispersion),
        spin=tuple(float(value) for value in primary_spin),
        reversed_spin=tuple(float(value) for value in reversed_spin),
    )
