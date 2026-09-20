from __future__ import annotations

import math

import numpy as np

from ..analytic.surface_dirac import analytic_energies
from ..models.surface_dirac import surface_dirac_hamiltonian
from ..observables.spectrum import eigensystem
from ..observables.spin import in_plane_helicity, spin_expectation
from ..results import (
    CheckResult,
    Exp001Metrics,
    Exp001Result,
    SpectrumPoint,
    SpinPoint,
)
from ..spec import Exp001Spec

_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)


def _max_abs(matrix: np.ndarray) -> float:
    return float(np.max(np.abs(matrix)))


def _time_reversal_residual(
    hamiltonian_k: np.ndarray,
    hamiltonian_minus_k: np.ndarray,
) -> float:
    transformed = _SIGMA_Y @ hamiltonian_k.conj() @ _SIGMA_Y
    return _max_abs(transformed - hamiltonian_minus_k)


def execute_exp001(spec: Exp001Spec) -> Exp001Result:
    """Execute EXP-001 without filesystem, network, clock, Git, or randomness."""
    alpha = spec.model.alpha_eV_A
    spectrum_spec = spec.sampling.spectrum
    ring_spec = spec.sampling.spin_ring

    spectrum_points: list[SpectrumPoint] = []
    spin_points: list[SpinPoint] = []

    max_hermiticity = 0.0
    max_analytic_error = 0.0
    max_particle_hole = 0.0
    max_time_reversal = 0.0
    dirac_point_abs = 0.0

    kx_values = np.linspace(
        spectrum_spec.min_Ainv,
        spectrum_spec.max_Ainv,
        spectrum_spec.points,
        dtype=np.float64,
    )

    for kx in kx_values:
        kx_float = float(kx)
        ky_float = spectrum_spec.fixed_ky_Ainv
        h = surface_dirac_hamiltonian(kx_float, ky_float, alpha)
        h_minus = surface_dirac_hamiltonian(-kx_float, -ky_float, alpha)

        max_hermiticity = max(max_hermiticity, _max_abs(h - h.conj().T))
        max_time_reversal = max(
            max_time_reversal,
            _time_reversal_residual(h, h_minus),
        )

        energies, _ = eigensystem(h)
        expected = analytic_energies(kx_float, ky_float, alpha)
        max_analytic_error = max(
            max_analytic_error,
            float(np.max(np.abs(energies - expected))),
        )
        max_particle_hole = max(
            max_particle_hole,
            abs(float(energies[0] + energies[1])),
        )

        if math.isclose(kx_float, 0.0, rel_tol=0.0, abs_tol=1e-15):
            dirac_point_abs = max(abs(float(energies[0])), abs(float(energies[1])))

        spectrum_points.append(
            SpectrumPoint(
                kx_Ainv=kx_float,
                ky_Ainv=ky_float,
                lower_eV=float(energies[0]),
                upper_eV=float(energies[1]),
                analytic_lower_eV=float(expected[0]),
                analytic_upper_eV=float(expected[1]),
            )
        )

    max_spin_norm_error = 0.0
    max_spin_momentum_dot = 0.0
    max_abs_spin_z = 0.0
    max_helicity_error = 0.0

    for angle in np.linspace(0.0, 2.0 * math.pi, ring_spec.angles, endpoint=False):
        angle_float = float(angle)
        kx = ring_spec.radius_Ainv * math.cos(angle_float)
        ky = ring_spec.radius_Ainv * math.sin(angle_float)

        h = surface_dirac_hamiltonian(kx, ky, alpha)
        h_minus = surface_dirac_hamiltonian(-kx, -ky, alpha)
        max_hermiticity = max(max_hermiticity, _max_abs(h - h.conj().T))
        max_time_reversal = max(
            max_time_reversal,
            _time_reversal_residual(h, h_minus),
        )

        energies, states = eigensystem(h)
        expected = analytic_energies(kx, ky, alpha)
        max_analytic_error = max(
            max_analytic_error,
            float(np.max(np.abs(energies - expected))),
        )
        max_particle_hole = max(
            max_particle_hole,
            abs(float(energies[0] + energies[1])),
        )

        radius = math.hypot(kx, ky)
        khat = np.array([kx / radius, ky / radius, 0.0], dtype=np.float64)

        for index, band, expected_helicity in (
            (0, "lower", -1.0),
            (1, "upper", 1.0),
        ):
            spin = spin_expectation(states[:, index])
            helicity = in_plane_helicity(spin, kx, ky)

            max_spin_norm_error = max(
                max_spin_norm_error,
                abs(float(np.linalg.norm(spin)) - 1.0),
            )
            max_spin_momentum_dot = max(
                max_spin_momentum_dot,
                abs(float(np.dot(spin, khat))),
            )
            max_abs_spin_z = max(max_abs_spin_z, abs(float(spin[2])))
            max_helicity_error = max(
                max_helicity_error,
                abs(helicity - expected_helicity),
            )

            spin_points.append(
                SpinPoint(
                    angle_rad=angle_float,
                    band=band,
                    kx_Ainv=kx,
                    ky_Ainv=ky,
                    sx=float(spin[0]),
                    sy=float(spin[1]),
                    sz=float(spin[2]),
                    helicity=helicity,
                )
            )

    metrics = Exp001Metrics(
        max_hermiticity_residual_eV=max_hermiticity,
        max_analytic_spectrum_error_eV=max_analytic_error,
        dirac_point_abs_eV=dirac_point_abs,
        max_particle_hole_error_eV=max_particle_hole,
        max_spin_norm_error=max_spin_norm_error,
        max_spin_momentum_dot=max_spin_momentum_dot,
        max_abs_spin_z=max_abs_spin_z,
        max_helicity_error=max_helicity_error,
        max_time_reversal_residual_eV=max_time_reversal,
    )

    acceptance = spec.acceptance
    checks = (
        CheckResult(
            "hermiticity",
            metrics.max_hermiticity_residual_eV,
            acceptance.hermiticity_abs_eV,
            "eV",
        ),
        CheckResult(
            "analytic_spectrum",
            metrics.max_analytic_spectrum_error_eV,
            acceptance.analytic_spectrum_abs_eV,
            "eV",
        ),
        CheckResult(
            "dirac_point",
            metrics.dirac_point_abs_eV,
            acceptance.dirac_point_abs_eV,
            "eV",
        ),
        CheckResult(
            "particle_hole",
            metrics.max_particle_hole_error_eV,
            acceptance.particle_hole_abs_eV,
            "eV",
        ),
        CheckResult(
            "spin_norm",
            metrics.max_spin_norm_error,
            acceptance.spin_norm_abs,
            "1",
        ),
        CheckResult(
            "spin_momentum_dot",
            metrics.max_spin_momentum_dot,
            acceptance.spin_momentum_dot_abs,
            "1",
        ),
        CheckResult(
            "spin_z",
            metrics.max_abs_spin_z,
            acceptance.spin_z_abs,
            "1",
        ),
        CheckResult(
            "helicity",
            metrics.max_helicity_error,
            acceptance.helicity_abs,
            "1",
        ),
        CheckResult(
            "time_reversal",
            metrics.max_time_reversal_residual_eV,
            acceptance.time_reversal_abs_eV,
            "eV",
        ),
    )

    return Exp001Result(
        experiment_id=spec.experiment_id,
        checks=checks,
        metrics=metrics,
        spectrum=tuple(spectrum_points),
        spin_ring=tuple(spin_points),
    )
