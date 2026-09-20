from __future__ import annotations

import math

import numpy as np

from ..analytic.magnetic_surface_dirac import (
    analytic_magnetic_energies,
    analytic_magnetic_spin,
)
from ..models.magnetic_surface_dirac import magnetic_surface_dirac_hamiltonian
from ..observables.spectrum import eigensystem
from ..observables.spin import in_plane_helicity, spin_expectation
from ..results import (
    CheckResult,
    Exp002Metrics,
    Exp002Result,
    SpectrumPoint,
    SpinPoint,
)
from ..spec_exp002 import Exp002Spec

_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)


def _max_abs(matrix: np.ndarray) -> float:
    return float(np.max(np.abs(matrix)))


def _time_reversal_transform(hamiltonian: np.ndarray) -> np.ndarray:
    return _SIGMA_Y @ hamiltonian.conj() @ _SIGMA_Y


def execute_exp002(spec: Exp002Spec) -> Exp002Result:
    """Execute EXP-002 without filesystem, network, clock, Git, or randomness."""
    alpha = spec.model.alpha_eV_A
    mass = spec.model.mass_eV
    spectrum_spec = spec.sampling.spectrum
    ring_spec = spec.sampling.spin_ring

    spectrum_points: list[SpectrumPoint] = []
    spin_points: list[SpinPoint] = []

    max_hermiticity = 0.0
    max_analytic_error = 0.0
    direct_gap_error = 0.0
    max_spectral_pairing = 0.0
    max_tr_breaking_magnitude_error = 0.0
    max_tr_mass_flip_residual = 0.0
    center_spin_error = 0.0
    center_seen = False

    expected_tr_breaking = 2.0 * abs(mass)
    expected_gap = 2.0 * abs(mass)

    kx_values = np.linspace(
        spectrum_spec.min_Ainv,
        spectrum_spec.max_Ainv,
        spectrum_spec.points,
        dtype=np.float64,
    )

    for kx in kx_values:
        kx_float = float(kx)
        ky_float = spectrum_spec.fixed_ky_Ainv

        h = magnetic_surface_dirac_hamiltonian(kx_float, ky_float, alpha, mass)
        h_minus_same = magnetic_surface_dirac_hamiltonian(
            -kx_float, -ky_float, alpha, mass
        )
        h_minus_flipped = magnetic_surface_dirac_hamiltonian(
            -kx_float, -ky_float, alpha, -mass
        )

        max_hermiticity = max(max_hermiticity, _max_abs(h - h.conj().T))

        transformed = _time_reversal_transform(h)
        same_mass_residual = _max_abs(transformed - h_minus_same)
        max_tr_breaking_magnitude_error = max(
            max_tr_breaking_magnitude_error,
            abs(same_mass_residual - expected_tr_breaking),
        )
        max_tr_mass_flip_residual = max(
            max_tr_mass_flip_residual,
            _max_abs(transformed - h_minus_flipped),
        )

        energies, states = eigensystem(h)
        expected = analytic_magnetic_energies(kx_float, ky_float, alpha, mass)
        max_analytic_error = max(
            max_analytic_error,
            float(np.max(np.abs(energies - expected))),
        )
        max_spectral_pairing = max(
            max_spectral_pairing,
            abs(float(energies[0] + energies[1])),
        )

        if math.isclose(kx_float, 0.0, rel_tol=0.0, abs_tol=1e-15):
            center_seen = True
            direct_gap_error = abs(float(energies[1] - energies[0]) - expected_gap)
            for index, band in ((0, "lower"), (1, "upper")):
                spin = spin_expectation(states[:, index])
                expected_spin = analytic_magnetic_spin(
                    0.0, 0.0, alpha, mass, band
                )
                center_spin_error = max(
                    center_spin_error,
                    float(np.max(np.abs(spin - expected_spin))),
                )

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

    if not center_seen:
        raise RuntimeError("EXP-002 spectrum grid did not include k=0.")

    max_spin_norm_error = 0.0
    max_spin_momentum_dot = 0.0
    max_spin_vector_error = 0.0
    max_helicity_error = 0.0

    for angle in np.linspace(0.0, 2.0 * math.pi, ring_spec.angles, endpoint=False):
        angle_float = float(angle)
        kx = ring_spec.radius_Ainv * math.cos(angle_float)
        ky = ring_spec.radius_Ainv * math.sin(angle_float)

        h = magnetic_surface_dirac_hamiltonian(kx, ky, alpha, mass)
        h_minus_same = magnetic_surface_dirac_hamiltonian(-kx, -ky, alpha, mass)
        h_minus_flipped = magnetic_surface_dirac_hamiltonian(-kx, -ky, alpha, -mass)

        max_hermiticity = max(max_hermiticity, _max_abs(h - h.conj().T))

        transformed = _time_reversal_transform(h)
        same_mass_residual = _max_abs(transformed - h_minus_same)
        max_tr_breaking_magnitude_error = max(
            max_tr_breaking_magnitude_error,
            abs(same_mass_residual - expected_tr_breaking),
        )
        max_tr_mass_flip_residual = max(
            max_tr_mass_flip_residual,
            _max_abs(transformed - h_minus_flipped),
        )

        energies, states = eigensystem(h)
        expected_energies = analytic_magnetic_energies(kx, ky, alpha, mass)
        max_analytic_error = max(
            max_analytic_error,
            float(np.max(np.abs(energies - expected_energies))),
        )
        max_spectral_pairing = max(
            max_spectral_pairing,
            abs(float(energies[0] + energies[1])),
        )

        radius = math.hypot(kx, ky)
        khat = np.array([kx / radius, ky / radius, 0.0], dtype=np.float64)

        for index, band in ((0, "lower"), (1, "upper")):
            spin = spin_expectation(states[:, index])
            expected_spin = analytic_magnetic_spin(kx, ky, alpha, mass, band)
            helicity = in_plane_helicity(spin, kx, ky)
            expected_helicity = (
                (kx / radius) * expected_spin[1]
                - (ky / radius) * expected_spin[0]
            )

            max_spin_norm_error = max(
                max_spin_norm_error,
                abs(float(np.linalg.norm(spin)) - 1.0),
            )
            max_spin_momentum_dot = max(
                max_spin_momentum_dot,
                abs(float(np.dot(spin, khat))),
            )
            max_spin_vector_error = max(
                max_spin_vector_error,
                float(np.max(np.abs(spin - expected_spin))),
            )
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

    metrics = Exp002Metrics(
        max_hermiticity_residual_eV=max_hermiticity,
        max_analytic_spectrum_error_eV=max_analytic_error,
        direct_gap_error_eV=direct_gap_error,
        max_spectral_pairing_error_eV=max_spectral_pairing,
        max_spin_norm_error=max_spin_norm_error,
        max_spin_momentum_dot=max_spin_momentum_dot,
        max_spin_vector_error=max_spin_vector_error,
        max_helicity_error=max_helicity_error,
        center_spin_error=center_spin_error,
        max_tr_breaking_magnitude_error_eV=max_tr_breaking_magnitude_error,
        max_tr_mass_flip_residual_eV=max_tr_mass_flip_residual,
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
            "direct_gap",
            metrics.direct_gap_error_eV,
            acceptance.direct_gap_abs_eV,
            "eV",
        ),
        CheckResult(
            "spectral_pairing",
            metrics.max_spectral_pairing_error_eV,
            acceptance.spectral_pairing_abs_eV,
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
            "spin_vector",
            metrics.max_spin_vector_error,
            acceptance.spin_vector_abs,
            "1",
        ),
        CheckResult(
            "helicity",
            metrics.max_helicity_error,
            acceptance.helicity_abs,
            "1",
        ),
        CheckResult(
            "center_spin",
            metrics.center_spin_error,
            acceptance.center_spin_abs,
            "1",
        ),
        CheckResult(
            "time_reversal_breaking_magnitude",
            metrics.max_tr_breaking_magnitude_error_eV,
            acceptance.tr_breaking_magnitude_abs_eV,
            "eV",
        ),
        CheckResult(
            "time_reversal_mass_flip",
            metrics.max_tr_mass_flip_residual_eV,
            acceptance.tr_mass_flip_abs_eV,
            "eV",
        ),
    )

    return Exp002Result(
        experiment_id=spec.experiment_id,
        checks=checks,
        metrics=metrics,
        spectrum=tuple(spectrum_points),
        spin_ring=tuple(spin_points),
    )
