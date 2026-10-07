"""EXP-004 Wilson lead-mode smoke on the pinned NumPy-2 Kwant lane.

Research-only bridge from VAL-001/EXP-003 into a translationally invariant lead.
No finite scattering device is constructed here.

The model is the isotropic square-lattice Wilson extension

    H(k) = alpha/a [sin(kx a) sigma_y - sin(ky a) sigma_x]
         + {m(x) + r alpha/a [(1-cos(kx a)) + (1-cos(ky a))]} sigma_z

with a periodic transverse ring containing two smooth, oppositely oriented
mass domain walls.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path

import kwant
import numpy as np
import scipy

ALPHA_EV_A = 1.0
M0_EV = 0.020
WALL_WIDTH_A = 50.0
XI_A = ALPHA_EV_A / M0_EV
A_A = 10.0
NX = 80
L_A = NX * A_A
WILSON_R = 0.5
K_SMOKE = 0.05
LOW_ENERGY_WINDOW_EV = 0.015

S0 = np.eye(2, dtype=complex)
SX = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SY = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SZ = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def periodic_mass(x_A: float) -> float:
    """Periodic two-wall profile with local tanh(x/w) behavior near each zero."""
    scale = 2.0 * math.pi * WALL_WIDTH_A / L_A
    return M0_EV * math.tanh(math.sin(2.0 * math.pi * x_A / L_A) / scale)


def ring_distance(x_A: float, center_A: float) -> float:
    delta = abs(x_A - center_A) % L_A
    return min(delta, L_A - delta)


def build_lead(wilson_r: float):
    lat = kwant.lattice.square(A_A, norbs=2)
    lead = kwant.Builder(kwant.TranslationalSymmetry((0.0, A_A)))

    w = wilson_r * ALPHA_EV_A / A_A
    hop_x = (-1.0j * ALPHA_EV_A / (2.0 * A_A)) * SY - 0.5 * w * SZ
    # Real-space discretization of -alpha k_y sigma_x = + i alpha d_y sigma_x.
    hop_y = (+1.0j * ALPHA_EV_A / (2.0 * A_A)) * SX - 0.5 * w * SZ

    for ix in range(NX):
        x_A = ix * A_A
        lead[lat(ix, 0)] = (periodic_mass(x_A) + 2.0 * w) * SZ

    for ix in range(NX - 1):
        lead[lat(ix, 0), lat(ix + 1, 0)] = hop_x
    lead[lat(NX - 1, 0), lat(0, 0)] = hop_x

    for ix in range(NX):
        lead[lat(ix, 0), lat(ix, 1)] = hop_y

    return lead.finalized()


def site_x_coordinates(lead) -> np.ndarray:
    sites = list(lead.sites[: lead.cell_size])
    if len(sites) != NX:
        raise AssertionError(f"expected {NX} cell sites, got {len(sites)}")
    return np.asarray([float(site.tag[0]) * A_A for site in sites])


def state_metrics(vector: np.ndarray, x_A: np.ndarray) -> dict:
    psi = np.asarray(vector, dtype=complex).reshape((NX, 2))
    density = np.sum(np.abs(psi) ** 2, axis=1)
    density = density / np.sum(density)

    def spin(pauli):
        local = np.einsum("ni,ij,nj->n", psi.conj(), pauli, psi)
        return float(np.real(np.sum(local)) / np.sum(np.abs(psi) ** 2))

    radius = 2.0 * XI_A
    wall0 = np.asarray([ring_distance(x, 0.0) <= radius for x in x_A])
    wall1 = np.asarray([ring_distance(x, 0.5 * L_A) <= radius for x in x_A])

    return {
        "wall0_weight": float(np.sum(density[wall0])),
        "wall1_weight": float(np.sum(density[wall1])),
        "sigma_x": spin(SX),
        "sigma_y": spin(SY),
        "sigma_z": spin(SZ),
        "density_peak_x_A": float(x_A[int(np.argmax(density))]),
    }


def low_energy_modes(lead, k: float) -> list[dict]:
    bands = kwant.physics.Bands(lead)
    energies, velocities, vectors = bands(
        k,
        derivative_order=1,
        return_eigenvectors=True,
    )
    x_A = site_x_coordinates(lead)
    indices = np.flatnonzero(np.abs(energies) < LOW_ENERGY_WINDOW_EV)
    out = []
    for index in indices:
        metrics = state_metrics(vectors[:, int(index)], x_A)
        out.append(
            {
                "band_index": int(index),
                "energy_eV": float(energies[index]),
                "dE_dkphase_eV": float(velocities[index]),
                **metrics,
            }
        )
    return out


def select_wall_modes(modes: list[dict]) -> tuple[dict, dict]:
    if len(modes) != 2:
        raise AssertionError(f"expected exactly two low-energy modes, got {len(modes)}")
    wall0 = max(modes, key=lambda m: m["wall0_weight"])
    wall1 = max(modes, key=lambda m: m["wall1_weight"])
    if wall0["band_index"] == wall1["band_index"]:
        raise AssertionError("both walls mapped to the same low-energy band")
    return wall0, wall1


def minimum_abs_energy(lead, k: float) -> float:
    energies = kwant.physics.Bands(lead)(k)
    return float(np.min(np.abs(energies)))


def dense_oracle_residual(lead, k: float) -> float:
    """Cross-check Bands against its documented Bloch construction."""
    bands = kwant.physics.Bands(lead)
    mat = bands.hop * complex(math.cos(k), -math.sin(k))
    h_k = bands.ham + mat + mat.conj().T
    direct = np.linalg.eigvalsh(h_k)
    observed = bands(k)
    return float(np.max(np.abs(direct - observed)))


def run() -> dict:
    wilson = build_lead(WILSON_R)
    naive = build_lead(0.0)

    modes_plus = low_energy_modes(wilson, +K_SMOKE)
    modes_minus = low_energy_modes(wilson, -K_SMOKE)
    wall0_plus, wall1_plus = select_wall_modes(modes_plus)
    wall0_minus, wall1_minus = select_wall_modes(modes_minus)

    expected_abs_energy = ALPHA_EV_A * abs(math.sin(K_SMOKE)) / A_A
    expected_abs_slope = ALPHA_EV_A * math.cos(K_SMOKE) / A_A

    pi_gap_wilson = minimum_abs_energy(wilson, math.pi)
    pi_gap_naive = minimum_abs_energy(naive, math.pi)

    checks = {
        "two_low_energy_modes_at_plus_k": len(modes_plus) == 2,
        "two_low_energy_modes_at_minus_k": len(modes_minus) == 2,
        "canonical_wall_localized_plus_k": wall0_plus["wall0_weight"] >= 0.80,
        "opposite_wall_localized_plus_k": wall1_plus["wall1_weight"] >= 0.80,
        "canonical_wall_spin_x": wall0_plus["sigma_x"] <= -0.90,
        "opposite_wall_spin_x": wall1_plus["sigma_x"] >= +0.90,
        "canonical_wall_positive_dispersion": (
            wall0_plus["energy_eV"] > 0.0
            and wall0_plus["dE_dkphase_eV"] > 0.0
        ),
        "opposite_wall_negative_dispersion": (
            wall1_plus["energy_eV"] < 0.0
            and wall1_plus["dE_dkphase_eV"] < 0.0
        ),
        "orientation_reversal_energy": (
            wall0_minus["energy_eV"] < 0.0
            and wall1_minus["energy_eV"] > 0.0
        ),
        "low_k_energy_close_to_exp003": (
            abs(abs(wall0_plus["energy_eV"]) - expected_abs_energy) <= 7.5e-4
            and abs(abs(wall1_plus["energy_eV"]) - expected_abs_energy) <= 7.5e-4
        ),
        "low_k_slope_close_to_exp003": (
            abs(abs(wall0_plus["dE_dkphase_eV"]) - expected_abs_slope) <= 7.5e-3
            and abs(abs(wall1_plus["dE_dkphase_eV"]) - expected_abs_slope) <= 7.5e-3
        ),
        "wilson_gaps_y_doubler": pi_gap_wilson >= 0.05,
        "naive_y_doubler_control_present": pi_gap_naive <= 0.01,
        "bands_dense_oracle_plus": dense_oracle_residual(wilson, +K_SMOKE) <= 1e-12,
        "bands_dense_oracle_pi": dense_oracle_residual(wilson, math.pi) <= 1e-12,
    }

    return {
        "schema_version": "exp004-wilson-lead-smoke-v0.1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_ceiling": (
            "Lead-mode bridge only. No finite-device scattering, conductance, "
            "disorder robustness, or material-specific claim is authorized."
        ),
        "runtime": {
            "python": platform.python_version(),
            "kwant": kwant.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": {
            "alpha_eV_A": ALPHA_EV_A,
            "mass_magnitude_eV": M0_EV,
            "wall_width_A": WALL_WIDTH_A,
            "xi_A": XI_A,
            "lattice_spacing_A": A_A,
            "nx": NX,
            "circumference_A": L_A,
            "wall_separation_A": 0.5 * L_A,
            "wall_separation_xi": 0.5 * L_A / XI_A,
            "wilson_r": WILSON_R,
            "k_phase_smoke": K_SMOKE,
            "low_energy_window_eV": LOW_ENERGY_WINDOW_EV,
        },
        "expected": {
            "abs_energy_eV_at_k_smoke": expected_abs_energy,
            "abs_dE_dkphase_eV_at_k_smoke": expected_abs_slope,
            "canonical_wall_sigma_x": -1.0,
            "opposite_wall_sigma_x": +1.0,
        },
        "observed": {
            "plus_k_modes": modes_plus,
            "minus_k_modes": modes_minus,
            "wilson_min_abs_energy_at_pi_eV": pi_gap_wilson,
            "naive_min_abs_energy_at_pi_eV": pi_gap_naive,
            "bands_dense_oracle_residual_plus_eV": dense_oracle_residual(wilson, +K_SMOKE),
            "bands_dense_oracle_residual_pi_eV": dense_oracle_residual(wilson, math.pi),
        },
        "checks": checks,
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
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
