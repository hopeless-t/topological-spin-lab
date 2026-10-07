"""EXP-004 C12 economy-versus-margin cost qualification.

Compare only the two candidates carried forward by C11:

- economy: a = 10 A, separation = 8 xi
- margin:  a =  8 A, separation = 8 xi

The physical transverse circumference is held fixed.  This script measures
structural cost proxies and same-process dense-eigensolver timing, and then
applies the VAL-003 EFT post-check to the selected wall eigenpair.

Research/engineering decision support only.  It does not build a finite
scattering device and does not authorize a transport claim by itself.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import time
from pathlib import Path

import numpy as np

from topological_spin_lab.verification.numerical_trust import (
    eft_complex_sum_products,
    eft_eigen_residual,
    eft_norm,
)

ALPHA_EV_A = 1.0
M0_EV = 0.020
WALL_WIDTH_A = 50.0
XI_A = ALPHA_EV_A / M0_EV
WILSON_R = 0.5
WALL_SEPARATION_XI = 8
PROBE_KY_AINV = 0.005

S_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
S_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
S_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)

CANDIDATES = {
    "economy": 10.0,
    "margin": 8.0,
}

# C11 strict convergence family. Identity/regulator checks remain separate.
STRICT = {
    "hybridization_gap_max_eV": 7.5e-6,
    "energy_relative_error_max": 5.0e-4,
    "velocity_relative_error_max": 1.0e-3,
    "abs_sigma_x_min": 0.9999,
    "wall_weight_min": 0.95,
    "wilson_pi_gap_min_eV": 0.075,
    "naive_pi_gap_max_eV": 1.0e-10,
}

NOMINAL = {
    "hybridization_gap_max_eV": 1.0e-5,
    "energy_relative_error_max": 1.0e-3,
    "velocity_relative_error_max": 2.0e-3,
    "abs_sigma_x_min": 0.999,
    "wall_weight_min": 0.95,
    "wilson_pi_gap_min_eV": 0.05,
    "naive_pi_gap_max_eV": 1.0e-10,
}


def periodic_mass(x_A: float, circumference_A: float) -> float:
    scale = 2.0 * math.pi * WALL_WIDTH_A / circumference_A
    return M0_EV * math.tanh(
        math.sin(2.0 * math.pi * x_A / circumference_A) / scale
    )


def ring_distance(values: np.ndarray, center: float, circumference: float) -> np.ndarray:
    delta = np.abs(values - center) % circumference
    return np.minimum(delta, circumference - delta)


def build_hamiltonian(a_requested_A: float, ky_Ainv: float, wilson_r: float) -> tuple[np.ndarray, np.ndarray, float, float]:
    separation_A = WALL_SEPARATION_XI * XI_A
    circumference_A = 2.0 * separation_A
    nx = int(round(circumference_A / a_requested_A))
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
    for ix, x_value in enumerate(x_A):
        onsite = (
            periodic_mass(float(x_value), circumference_A) + 2.0 * wilson_scale
        ) * S_Z
        block = 2 * ix
        h[block : block + 2, block : block + 2] = onsite + y_bloch
        other = 2 * ((ix + 1) % nx)
        h[block : block + 2, other : other + 2] += hop_x
        h[other : other + 2, block : block + 2] += hop_x.conj().T

    return h, x_A, a_eff_A, circumference_A


def state_metrics(vector: np.ndarray, x_A: np.ndarray, circumference_A: float) -> dict[str, float]:
    psi = np.asarray(vector, dtype=complex).reshape((len(x_A), 2))
    density = np.sum(np.abs(psi) ** 2, axis=1)
    density /= np.sum(density)

    wall0 = ring_distance(x_A, 0.0, circumference_A) <= 2.0 * XI_A
    wall1 = ring_distance(x_A, 0.5 * circumference_A, circumference_A) <= 2.0 * XI_A

    sx_psi = psi[:, ::-1].reshape(-1)
    numerator = eft_complex_sum_products(vector, sx_psi, conjugate_a=True)
    denominator = eft_complex_sum_products(vector, vector, conjugate_a=True)
    sigma_x = numerator / denominator

    return {
        "wall0_weight": float(np.sum(density[wall0])),
        "wall1_weight": float(np.sum(density[wall1])),
        "sigma_x_eft_real": float(sigma_x.real),
        "sigma_x_eft_imag": float(sigma_x.imag),
    }


def select_wall_mode(h: np.ndarray, x_A: np.ndarray, circumference_A: float, wall: int) -> tuple[float, np.ndarray, dict[str, float]]:
    energies, vectors = np.linalg.eigh(h)
    scored = []
    for index in np.argsort(np.abs(energies))[:12]:
        metrics = state_metrics(vectors[:, index], x_A, circumference_A)
        if wall == 0:
            score = metrics["wall0_weight"] - metrics["wall1_weight"]
        else:
            score = metrics["wall1_weight"] - metrics["wall0_weight"]
        scored.append((score, int(index), float(energies[index]), vectors[:, index], metrics))
    _, _, energy, vector, metrics = max(scored, key=lambda row: row[0])
    return energy, np.asarray(vector, dtype=complex), metrics


def min_abs_energy(a_A: float, ky_Ainv: float, r: float) -> float:
    h, _, _, _ = build_hamiltonian(a_A, ky_Ainv, r)
    return float(np.min(np.abs(np.linalg.eigvalsh(h))))


def evaluate_candidate(name: str, a_A: float, *, timing_repeats: int) -> dict:
    h, x_A, a_eff_A, circumference_A = build_hamiltonian(a_A, PROBE_KY_AINV, WILSON_R)
    energy, vector, metrics = select_wall_mode(h, x_A, circumference_A, wall=0)
    opposite_energy, _, opposite_metrics = select_wall_mode(h, x_A, circumference_A, wall=1)

    dky = 1.0e-5
    h_plus, xp, _, cp = build_hamiltonian(a_A, PROBE_KY_AINV + dky, WILSON_R)
    h_minus, xm, _, cm = build_hamiltonian(a_A, PROBE_KY_AINV - dky, WILSON_R)
    e_plus, _, _ = select_wall_mode(h_plus, xp, cp, wall=0)
    e_minus, _, _ = select_wall_mode(h_minus, xm, cm, wall=0)
    velocity = (e_plus - e_minus) / (2.0 * dky)

    h0, _, _, _ = build_hamiltonian(a_A, 0.0, WILSON_R)
    hybridization = float(np.max(np.sort(np.abs(np.linalg.eigvalsh(h0)))[:2]))

    pi_ky = math.pi / a_eff_A
    wilson_pi_gap = min_abs_energy(a_A, pi_ky, WILSON_R)
    naive_pi_gap = min_abs_energy(a_A, pi_ky, 0.0)

    expected_energy = ALPHA_EV_A * PROBE_KY_AINV
    energy_rel_error = abs(abs(energy) - expected_energy) / expected_energy
    velocity_rel_error = abs(abs(velocity) - ALPHA_EV_A) / ALPHA_EV_A

    residual = eft_eigen_residual(h, energy, vector)
    residual_norm = eft_norm(residual)

    # Warm up the same solver path before timing. Timings are descriptive; exact
    # dimension/storage/flop proxies remain the deterministic cost authority.
    np.linalg.eigh(h)
    samples = []
    for _ in range(timing_repeats):
        start = time.perf_counter_ns()
        np.linalg.eigh(h)
        samples.append((time.perf_counter_ns() - start) / 1.0e6)

    dimension = int(h.shape[0])
    nx = int(len(x_A))
    matrix_elements = dimension * dimension
    matrix_bytes_complex128 = matrix_elements * np.dtype(np.complex128).itemsize
    dense_cubic_proxy = dimension**3

    observed = {
        "name": name,
        "lattice_spacing_requested_A": a_A,
        "lattice_spacing_effective_A": a_eff_A,
        "wall_separation_xi": WALL_SEPARATION_XI,
        "circumference_A": circumference_A,
        "nx": nx,
        "matrix_dimension": dimension,
        "canonical_wall_energy_eV": energy,
        "opposite_wall_energy_eV": opposite_energy,
        "energy_relative_error": energy_rel_error,
        "velocity_eV_A": velocity,
        "velocity_relative_error": velocity_rel_error,
        "canonical_sigma_x_eft": metrics["sigma_x_eft_real"],
        "opposite_sigma_x_eft": opposite_metrics["sigma_x_eft_real"],
        "canonical_wall_weight": metrics["wall0_weight"],
        "opposite_wall_weight": opposite_metrics["wall1_weight"],
        "hybridization_gap_eV": hybridization,
        "wilson_pi_gap_eV": wilson_pi_gap,
        "naive_pi_gap_eV": naive_pi_gap,
        "eft_residual_norm": residual_norm,
        "cost": {
            "matrix_elements": matrix_elements,
            "matrix_bytes_complex128": matrix_bytes_complex128,
            "dense_cubic_proxy": dense_cubic_proxy,
            "eigh_timing_repeats": timing_repeats,
            "eigh_ms_median": statistics.median(samples),
            "eigh_ms_min": min(samples),
            "eigh_ms_max": max(samples),
        },
    }
    observed["strict_pass"] = gate_pass(observed, STRICT)
    observed["nominal_pass"] = gate_pass(observed, NOMINAL)
    return observed


def gate_pass(row: dict, gate: dict) -> bool:
    return bool(
        row["hybridization_gap_eV"] <= gate["hybridization_gap_max_eV"]
        and row["energy_relative_error"] <= gate["energy_relative_error_max"]
        and row["velocity_relative_error"] <= gate["velocity_relative_error_max"]
        and abs(row["canonical_sigma_x_eft"]) >= gate["abs_sigma_x_min"]
        and row["canonical_wall_weight"] >= gate["wall_weight_min"]
        and row["wilson_pi_gap_eV"] >= gate["wilson_pi_gap_min_eV"]
        and row["naive_pi_gap_eV"] <= gate["naive_pi_gap_max_eV"]
    )


def run(*, timing_repeats: int) -> dict:
    rows = {
        name: evaluate_candidate(name, a_A, timing_repeats=timing_repeats)
        for name, a_A in CANDIDATES.items()
    }
    economy = rows["economy"]
    margin = rows["margin"]

    ratios = {
        "margin_over_economy_nx": margin["nx"] / economy["nx"],
        "margin_over_economy_matrix_elements": (
            margin["cost"]["matrix_elements"] / economy["cost"]["matrix_elements"]
        ),
        "margin_over_economy_dense_cubic_proxy": (
            margin["cost"]["dense_cubic_proxy"] / economy["cost"]["dense_cubic_proxy"]
        ),
        "margin_over_economy_timed_eigh_median": (
            margin["cost"]["eigh_ms_median"] / economy["cost"]["eigh_ms_median"]
        ),
        # If both transverse and longitudinal spacings are refined at fixed
        # physical 2D extent, site count grows as 1/a^2.
        "same_extent_2d_site_count_proxy": (economy["lattice_spacing_effective_A"] / margin["lattice_spacing_effective_A"]) ** 2,
    }

    # C11 already established that the margin candidate survives the strict
    # threshold family while economy does not. C12 freezes the margin candidate
    # only if that remains true and the EFT post-check is numerically healthy.
    selected = "margin" if (
        margin["strict_pass"]
        and economy["nominal_pass"]
        and not economy["strict_pass"]
        and margin["eft_residual_norm"] <= 2.0e-15
        and economy["eft_residual_norm"] <= 2.0e-15
    ) else None

    checks = {
        "economy_nominal_pass": economy["nominal_pass"],
        "economy_strict_fail": not economy["strict_pass"],
        "margin_strict_pass": margin["strict_pass"],
        "economy_eft_residual_small": economy["eft_residual_norm"] <= 2.0e-15,
        "margin_eft_residual_small": margin["eft_residual_norm"] <= 2.0e-15,
        "margin_cost_increase_bounded_by_2x_dense_proxy": ratios["margin_over_economy_dense_cubic_proxy"] <= 2.0,
    }

    return {
        "schema_version": "exp004-c12-cost-qualification-v0.1",
        "status": "RESEARCH_PASS" if all(checks.values()) and selected else "RESEARCH_FAIL",
        "authority": (
            "Engineering selection under the C11 candidate gates plus VAL-003 "
            "post-check. Timings are descriptive; structural cost ratios are deterministic."
        ),
        "claim_ceiling": (
            "Discretization/cost selection only. No finite scattering device, "
            "transmission, conductance, robustness, or material-specific claim."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "thresholds": {
            "strict": STRICT,
            "nominal": NOMINAL,
        },
        "checks": checks,
        "candidates": rows,
        "cost_ratios": ratios,
        "selected_candidate": selected,
        "selection_reason": (
            "Select 8 A / 8 xi: it retains the C11 strict-margin PASS and VAL-003 "
            "residual check while increasing the deterministic dense n^3 proxy by "
            "less than 2x relative to 10 A / 8 xi."
            if selected == "margin"
            else "Selection gate did not converge."
        ),
        "next_gate": (
            "If reproduced on CI, freeze 8 A / 8 xi as the generic EXP-004 "
            "discretization candidate and review authorization of the minimal clean "
            "finite scattering calibration."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--timing-repeats", type=int, default=7)
    args = parser.parse_args()

    result = run(timing_repeats=args.timing_repeats)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(text, end="")
    if result["status"] != "RESEARCH_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
