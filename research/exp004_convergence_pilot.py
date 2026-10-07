"""EXP-004 C10 independent dense-oracle convergence pilot.

Research-only convergence sweep for the Wilson r=0.5 periodic double-wall lead
introduced in EXP004-C09. This implementation intentionally does not import
Kwant: it reconstructs the finite transverse Bloch Hamiltonian directly with
NumPy, providing an independent numerical oracle.

It does not construct a finite scattering region and does not authorize
transport claims.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path

import numpy as np

ALPHA_EV_A = 1.0
M0_EV = 0.020
WALL_WIDTH_A = 50.0
XI_A = ALPHA_EV_A / M0_EV
WILSON_R = 0.5
PROBE_KY_AINV = 0.005

LATTICE_SPACINGS_A = (20.0, 12.5, 10.0, 8.0, 5.0)
WALL_SEPARATIONS_XI = (4, 6, 8, 10)

S_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
S_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
S_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def periodic_mass(x_A: float, circumference_A: float) -> float:
    scale = 2.0 * math.pi * WALL_WIDTH_A / circumference_A
    return M0_EV * math.tanh(
        math.sin(2.0 * math.pi * x_A / circumference_A) / scale
    )


def ring_distance(values: np.ndarray, center: float, circumference: float) -> np.ndarray:
    delta = np.abs(values - center) % circumference
    return np.minimum(delta, circumference - delta)


def build_hamiltonian(
    lattice_spacing_A: float,
    wall_separation_xi: float,
    ky_Ainv: float,
    wilson_r: float,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Build the transverse-ring Bloch Hamiltonian at physical ky."""
    separation_A = wall_separation_xi * XI_A
    circumference_A = 2.0 * separation_A
    nx = int(round(circumference_A / lattice_spacing_A))
    if nx < 8:
        raise ValueError("transverse ring is too small")

    # Keep the circumference exact; small rounding is absorbed into a_eff.
    a_eff_A = circumference_A / nx
    wilson_scale = wilson_r * ALPHA_EV_A / a_eff_A

    hop_x = (
        (-1.0j * ALPHA_EV_A / (2.0 * a_eff_A)) * S_Y
        - 0.5 * wilson_scale * S_Z
    )
    hop_y = (
        (+1.0j * ALPHA_EV_A / (2.0 * a_eff_A)) * S_X
        - 0.5 * wilson_scale * S_Z
    )

    phase = ky_Ainv * a_eff_A
    y_bloch = hop_y * np.exp(1.0j * phase) + hop_y.conj().T * np.exp(-1.0j * phase)

    h = np.zeros((2 * nx, 2 * nx), dtype=complex)
    x_A = np.arange(nx, dtype=float) * a_eff_A

    for ix, x in enumerate(x_A):
        onsite = (periodic_mass(float(x), circumference_A) + 2.0 * wilson_scale) * S_Z
        block = 2 * ix
        h[block : block + 2, block : block + 2] = onsite + y_bloch

        jx = (ix + 1) % nx
        other = 2 * jx
        h[block : block + 2, other : other + 2] += hop_x
        h[other : other + 2, block : block + 2] += hop_x.conj().T

    hermiticity_residual = float(np.max(np.abs(h - h.conj().T)))
    if hermiticity_residual > 1e-12:
        raise AssertionError(f"Hermiticity failure: {hermiticity_residual}")

    return h, x_A, a_eff_A, circumference_A


def state_metrics(
    vector: np.ndarray,
    x_A: np.ndarray,
    circumference_A: float,
) -> dict[str, float]:
    psi = np.asarray(vector, dtype=complex).reshape((len(x_A), 2))
    density = np.sum(np.abs(psi) ** 2, axis=1)
    density /= np.sum(density)

    def spin(pauli: np.ndarray) -> float:
        local = np.einsum("ni,ij,nj->n", psi.conj(), pauli, psi)
        return float(np.real(np.sum(local)) / np.sum(np.abs(psi) ** 2))

    radius_A = 2.0 * XI_A
    wall0 = ring_distance(x_A, 0.0, circumference_A) <= radius_A
    wall1 = ring_distance(x_A, 0.5 * circumference_A, circumference_A) <= radius_A

    return {
        "wall0_weight": float(np.sum(density[wall0])),
        "wall1_weight": float(np.sum(density[wall1])),
        "sigma_x": spin(S_X),
        "sigma_y": spin(S_Y),
        "sigma_z": spin(S_Z),
        "density_peak_x_A": float(x_A[int(np.argmax(density))]),
    }


def wall_mode(
    lattice_spacing_A: float,
    wall_separation_xi: float,
    ky_Ainv: float,
    wall: int,
    wilson_r: float = WILSON_R,
) -> tuple[float, dict[str, float], float, int]:
    h, x_A, a_eff_A, circumference_A = build_hamiltonian(
        lattice_spacing_A, wall_separation_xi, ky_Ainv, wilson_r
    )
    energies, vectors = np.linalg.eigh(h)
    candidates = np.argsort(np.abs(energies))[:12]

    scored = []
    for index in candidates:
        metrics = state_metrics(vectors[:, index], x_A, circumference_A)
        if wall == 0:
            score = metrics["wall0_weight"] - metrics["wall1_weight"]
        else:
            score = metrics["wall1_weight"] - metrics["wall0_weight"]
        scored.append((score, int(index), float(energies[index]), metrics))

    _, _, energy, metrics = max(scored, key=lambda item: item[0])
    return energy, metrics, a_eff_A, len(x_A)


def minimum_abs_energy(
    lattice_spacing_A: float,
    wall_separation_xi: float,
    ky_Ainv: float,
    wilson_r: float,
) -> float:
    h, _, _, _ = build_hamiltonian(
        lattice_spacing_A, wall_separation_xi, ky_Ainv, wilson_r
    )
    return float(np.min(np.abs(np.linalg.eigvalsh(h))))


def run_point(lattice_spacing_A: float, wall_separation_xi: int) -> dict:
    energy0, metrics0, a_eff_A, nx = wall_mode(
        lattice_spacing_A, wall_separation_xi, PROBE_KY_AINV, wall=0
    )
    energy1, metrics1, _, _ = wall_mode(
        lattice_spacing_A, wall_separation_xi, PROBE_KY_AINV, wall=1
    )

    dky = 1.0e-5
    e_plus, _, _, _ = wall_mode(
        lattice_spacing_A, wall_separation_xi, PROBE_KY_AINV + dky, wall=0
    )
    e_minus, _, _, _ = wall_mode(
        lattice_spacing_A, wall_separation_xi, PROBE_KY_AINV - dky, wall=0
    )
    dE_dky_eV_A = (e_plus - e_minus) / (2.0 * dky)

    # At ky=0 the residual splitting of the two nominally zero-energy wall
    # states directly diagnoses finite wall-wall hybridization.
    h0, _, _, _ = build_hamiltonian(
        lattice_spacing_A, wall_separation_xi, 0.0, WILSON_R
    )
    zero_abs = np.sort(np.abs(np.linalg.eigvalsh(h0)))[:2]
    hybridization_gap_eV = float(np.max(zero_abs))

    # Probe the y Brillouin-zone edge. The Wilson model should gap the doubler;
    # the r=0 Red Team control should retain it.
    pi_ky_Ainv = math.pi / a_eff_A
    wilson_pi_gap_eV = minimum_abs_energy(
        lattice_spacing_A, wall_separation_xi, pi_ky_Ainv, WILSON_R
    )
    naive_pi_gap_eV = minimum_abs_energy(
        lattice_spacing_A, wall_separation_xi, pi_ky_Ainv, 0.0
    )

    expected_energy_eV = ALPHA_EV_A * PROBE_KY_AINV
    energy_abs_error_eV = abs(abs(energy0) - expected_energy_eV)
    velocity_abs_error = abs(abs(dE_dky_eV_A) - ALPHA_EV_A)

    return {
        "lattice_spacing_requested_A": lattice_spacing_A,
        "lattice_spacing_effective_A": a_eff_A,
        "wall_separation_xi": wall_separation_xi,
        "nx": nx,
        "canonical_wall_energy_eV": energy0,
        "opposite_wall_energy_eV": energy1,
        "energy_abs_error_eV": energy_abs_error_eV,
        "energy_relative_error": energy_abs_error_eV / expected_energy_eV,
        "canonical_wall_sigma_x": metrics0["sigma_x"],
        "opposite_wall_sigma_x": metrics1["sigma_x"],
        "canonical_wall_weight": metrics0["wall0_weight"],
        "opposite_wall_weight": metrics1["wall1_weight"],
        "dE_dky_eV_A": dE_dky_eV_A,
        "velocity_abs_error": velocity_abs_error,
        "velocity_relative_error": velocity_abs_error / ALPHA_EV_A,
        "hybridization_gap_eV": hybridization_gap_eV,
        "wilson_pi_gap_eV": wilson_pi_gap_eV,
        "naive_pi_gap_eV": naive_pi_gap_eV,
    }


def run() -> dict:
    rows = [
        run_point(a_A, sep_xi)
        for a_A in LATTICE_SPACINGS_A
        for sep_xi in WALL_SEPARATIONS_XI
    ]

    canonical = next(
        row
        for row in rows
        if abs(row["lattice_spacing_effective_A"] - 10.0) < 1e-12
        and row["wall_separation_xi"] == 8
    )

    candidate_gate = {
        "canonical_lattice_spacing_A": 10.0,
        "minimum_wall_separation_xi": 8,
        "hybridization_gap_max_eV": 1.0e-5,
        "continuum_group_velocity_relative_error_max": 2.0e-3,
        "continuum_energy_relative_error_max": 1.0e-3,
        "abs_sigma_x_min": 0.999,
        "wall_weight_min": 0.95,
        "wilson_pi_gap_min_eV": 0.05,
        "naive_pi_gap_max_eV": 1.0e-10,
    }

    checks = {
        "hybridization_gap": (
            canonical["hybridization_gap_eV"]
            <= candidate_gate["hybridization_gap_max_eV"]
        ),
        "velocity_relative_error": (
            canonical["velocity_relative_error"]
            <= candidate_gate["continuum_group_velocity_relative_error_max"]
        ),
        "energy_relative_error": (
            canonical["energy_relative_error"]
            <= candidate_gate["continuum_energy_relative_error_max"]
        ),
        "spin": (
            abs(canonical["canonical_wall_sigma_x"])
            >= candidate_gate["abs_sigma_x_min"]
        ),
        "wall_weight": (
            canonical["canonical_wall_weight"] >= candidate_gate["wall_weight_min"]
        ),
        "wilson_pi_gap": (
            canonical["wilson_pi_gap_eV"] >= candidate_gate["wilson_pi_gap_min_eV"]
        ),
        "naive_pi_gap": (
            canonical["naive_pi_gap_eV"] <= candidate_gate["naive_pi_gap_max_eV"]
        ),
    }

    return {
        "schema_version": "exp004-convergence-pilot-v0.1",
        "status": "EXPLORATORY_PASS" if all(checks.values()) else "EXPLORATORY_FAIL",
        "authority": (
            "Research-only independent dense-oracle pilot. Candidate thresholds "
            "are not frozen and this is not canonical scientific evidence."
        ),
        "claim_ceiling": (
            "Lead-mode convergence only. No finite-device scattering, conductance, "
            "disorder robustness, or material-specific claim is authorized."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "parameters": {
            "alpha_eV_A": ALPHA_EV_A,
            "mass_magnitude_eV": M0_EV,
            "wall_width_A": WALL_WIDTH_A,
            "xi_A": XI_A,
            "wilson_r": WILSON_R,
            "probe_ky_Ainv": PROBE_KY_AINV,
            "lattice_spacings_A": list(LATTICE_SPACINGS_A),
            "wall_separations_xi": list(WALL_SEPARATIONS_XI),
        },
        "candidate_gate": candidate_gate,
        "canonical_candidate_gate_checks": checks,
        "canonical_observation": canonical,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
