"""EXP004-C13: minimal clean finite scattering calibration.

Research-only finite-device implementation authorized by EXP004-C12.

The system is a Wilson-regularized surface-Dirac strip with periodic transverse
x and finite transport direction y.  The clean device and both leads share the
same Hamiltonian and periodic double-domain-wall mass texture.

C13 is a calibration, not a material prediction.  It measures scattering
unitarity, T/R, propagating channel count, transverse mode identity, and mode
spin polarization.  It also includes two mandatory negative controls:

1. a deliberately mismatched device mass texture, which must produce
   detectable reflection relative to the clean baseline;
2. an explicitly corrupted scattering matrix, which must fail the unitarity
   gate.

The selected discretization is inherited from C12:

    a = 8 A, wall separation = 8 xi, Wilson r = 0.5.
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
A_A = 8.0
WILSON_R = 0.5
NX = 100
L_A = NX * A_A
NY = 5
ENERGY_EV = 0.005

# A half-period mass shift swaps the two wall orientations while retaining the
# same wall coordinates.  It is deliberately non-canonical and is used only as
# a lead/device mismatch Red Team.
MISMATCH_SHIFT_A = 0.5 * L_A

UNITARITY_TOL = 1.0e-8
TRANSPORT_TOL = 2.0e-7
MODE_SPIN_MIN = 0.995
MODE_WALL_WEIGHT_MIN = 0.90
MISMATCH_REFLECTION_MIN = 1.0e-5
CORRUPTION_AMPLITUDE = 1.0e-3

S0 = np.eye(2, dtype=complex)
SX = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SY = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SZ = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def periodic_mass(x_A: float, *, shift_A: float = 0.0) -> float:
    """Periodic two-wall profile with local tanh behavior around each zero."""
    x = x_A - shift_A
    scale = 2.0 * math.pi * WALL_WIDTH_A / L_A
    return M0_EV * math.tanh(math.sin(2.0 * math.pi * x / L_A) / scale)


def ring_distance(x_A: float, center_A: float) -> float:
    delta = abs(x_A - center_A) % L_A
    return min(delta, L_A - delta)


def lattice_terms(wilson_r: float = WILSON_R):
    w = wilson_r * ALPHA_EV_A / A_A
    hop_x = (-1.0j * ALPHA_EV_A / (2.0 * A_A)) * SY - 0.5 * w * SZ
    hop_y = (+1.0j * ALPHA_EV_A / (2.0 * A_A)) * SX - 0.5 * w * SZ
    return w, hop_x, hop_y


def make_plus_y_lead(lat, *, wilson_r: float = WILSON_R):
    """Lead whose translation vector points along global +y."""
    lead = kwant.Builder(kwant.TranslationalSymmetry((0.0, A_A)))
    w, hop_x, hop_y = lattice_terms(wilson_r)

    for ix in range(NX):
        x_A = ix * A_A
        lead[lat(ix, 0)] = (periodic_mass(x_A) + 2.0 * w) * SZ

    for ix in range(NX - 1):
        lead[lat(ix, 0), lat(ix + 1, 0)] = hop_x
    lead[lat(NX - 1, 0), lat(0, 0)] = hop_x

    for ix in range(NX):
        lead[lat(ix, 0), lat(ix, 1)] = hop_y

    return lead


def build_system(*, device_mass_shift_A: float = 0.0, wilson_r: float = WILSON_R):
    lat = kwant.lattice.square(A_A, norbs=2)
    system = kwant.Builder()
    w, hop_x, hop_y = lattice_terms(wilson_r)

    for iy in range(NY):
        for ix in range(NX):
            x_A = ix * A_A
            system[lat(ix, iy)] = (
                periodic_mass(x_A, shift_A=device_mass_shift_A) + 2.0 * w
            ) * SZ

    for iy in range(NY):
        for ix in range(NX - 1):
            system[lat(ix, iy), lat(ix + 1, iy)] = hop_x
        system[lat(NX - 1, iy), lat(0, iy)] = hop_x

    for iy in range(NY - 1):
        for ix in range(NX):
            system[lat(ix, iy), lat(ix, iy + 1)] = hop_y

    plus_y = make_plus_y_lead(lat, wilson_r=wilson_r)
    system.attach_lead(plus_y.reversed())
    system.attach_lead(plus_y)
    return system.finalized()


def _mode_metrics(vector: np.ndarray, x_A: np.ndarray) -> dict:
    psi = np.asarray(vector, dtype=complex).reshape((NX, 2))
    density = np.sum(np.abs(psi) ** 2, axis=1)
    total = float(np.sum(density))
    if total <= 0.0:
        raise AssertionError("mode norm is zero")
    density = density / total

    def spin(pauli: np.ndarray) -> float:
        local = np.einsum("ni,ij,nj->n", psi.conj(), pauli, psi)
        return float(np.real(np.sum(local)) / total)

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


def propagating_mode_records(system, lead_index: int) -> list[dict]:
    smatrix = kwant.smatrix(system, energy=ENERGY_EV)
    info = smatrix.lead_info[lead_index]
    lead = system.leads[lead_index]
    sites = list(lead.sites[: lead.cell_size])
    if len(sites) != NX:
        raise AssertionError(f"expected {NX} lead cell sites, got {len(sites)}")
    x_A = np.asarray([float(site.tag[0]) * A_A for site in sites])

    wave_functions = np.asarray(info.wave_functions)
    velocities = np.asarray(info.velocities)
    momenta = np.asarray(info.momenta)
    if wave_functions.shape[1] != velocities.size:
        raise AssertionError("Kwant mode metadata shape mismatch")

    records: list[dict] = []
    for index in range(velocities.size):
        records.append(
            {
                "mode_index": int(index),
                "velocity": float(velocities[index]),
                "momentum": float(momenta[index]),
                **_mode_metrics(wave_functions[:, index], x_A),
            }
        )
    return records


def select_wall_modes(records: list[dict]) -> tuple[dict, dict]:
    if len(records) != 2:
        raise AssertionError(f"expected exactly two propagating mode vectors, got {len(records)}")
    wall0 = max(records, key=lambda row: row["wall0_weight"])
    wall1 = max(records, key=lambda row: row["wall1_weight"])
    if wall0["mode_index"] == wall1["mode_index"]:
        raise AssertionError("both walls mapped to the same propagating mode")
    return wall0, wall1


def scattering_observables(system) -> dict:
    smatrix = kwant.smatrix(system, energy=ENERGY_EV)
    s = np.asarray(smatrix.data)
    identity = np.eye(s.shape[1], dtype=complex)
    unitarity = float(np.linalg.norm(s.conj().T @ s - identity, ord=2))
    return {
        "s_matrix_shape": [int(value) for value in s.shape],
        "unitarity_residual_2norm": unitarity,
        "transmission_L_to_R": float(smatrix.transmission(1, 0)),
        "reflection_L_to_L": float(smatrix.transmission(0, 0)),
        "transmission_R_to_L": float(smatrix.transmission(0, 1)),
        "reflection_R_to_R": float(smatrix.transmission(1, 1)),
        "left_incoming_channels": int(smatrix.num_propagating(0)),
        "right_incoming_channels": int(smatrix.num_propagating(1)),
        "s_matrix": s,
    }


def corrupted_unitarity_residual(s_matrix: np.ndarray) -> float:
    corrupted = np.asarray(s_matrix, dtype=complex).copy()
    corrupted[0, 0] += CORRUPTION_AMPLITUDE
    identity = np.eye(corrupted.shape[1], dtype=complex)
    return float(np.linalg.norm(corrupted.conj().T @ corrupted - identity, ord=2))


def run() -> dict:
    clean_system = build_system()
    clean = scattering_observables(clean_system)

    # Use the +y-oriented right lead for global propagation-direction checks.
    right_records = propagating_mode_records(clean_system, 1)
    right_wall0, right_wall1 = select_wall_modes(right_records)

    mismatch_system = build_system(device_mass_shift_A=MISMATCH_SHIFT_A)
    mismatch = scattering_observables(mismatch_system)

    corrupted_residual = corrupted_unitarity_residual(clean["s_matrix"])

    checks = {
        "clean_one_incoming_channel_left": clean["left_incoming_channels"] == 1,
        "clean_one_incoming_channel_right": clean["right_incoming_channels"] == 1,
        "clean_smatrix_unitary": clean["unitarity_residual_2norm"] <= UNITARITY_TOL,
        "clean_left_to_right_transmission": (
            abs(clean["transmission_L_to_R"] - 1.0) <= TRANSPORT_TOL
        ),
        "clean_left_reflection_zero": clean["reflection_L_to_L"] <= TRANSPORT_TOL,
        "clean_right_to_left_transmission": (
            abs(clean["transmission_R_to_L"] - 1.0) <= TRANSPORT_TOL
        ),
        "clean_right_reflection_zero": clean["reflection_R_to_R"] <= TRANSPORT_TOL,
        "right_lead_exactly_two_mode_vectors": len(right_records) == 2,
        "canonical_wall_mode_localized": right_wall0["wall0_weight"] >= MODE_WALL_WEIGHT_MIN,
        "opposite_wall_mode_localized": right_wall1["wall1_weight"] >= MODE_WALL_WEIGHT_MIN,
        "canonical_wall_spin_negative_x": right_wall0["sigma_x"] <= -MODE_SPIN_MIN,
        "opposite_wall_spin_positive_x": right_wall1["sigma_x"] >= MODE_SPIN_MIN,
        "canonical_wall_positive_global_velocity": right_wall0["velocity"] > 0.0,
        "opposite_wall_negative_global_velocity": right_wall1["velocity"] < 0.0,
        "mismatch_red_team_reflects": (
            mismatch["reflection_L_to_L"] >= MISMATCH_REFLECTION_MIN
            and mismatch["reflection_L_to_L"] > clean["reflection_L_to_L"] + MISMATCH_REFLECTION_MIN
        ),
        "corrupted_smatrix_red_team_detected": corrupted_residual > UNITARITY_TOL,
    }

    clean_json = {key: value for key, value in clean.items() if key != "s_matrix"}
    mismatch_json = {key: value for key, value in mismatch.items() if key != "s_matrix"}

    return {
        "schema_version": "exp004-c13-clean-scattering-v0.1",
        "status": "RESEARCH_PASS" if all(checks.values()) else "RESEARCH_FAIL",
        "authority": (
            "Minimal clean finite scattering calibration authorized by C12. "
            "Research-only until review; no robustness or material-specific authority."
        ),
        "claim_ceiling": (
            "Generic clean Wilson-domain-wall calibration only. No NdBi claim, "
            "no disorder/geometry robustness, and no conserved-spin-current claim."
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
            "ny": NY,
            "circumference_A": L_A,
            "wall_separation_A": 0.5 * L_A,
            "wall_separation_xi": 0.5 * L_A / XI_A,
            "wilson_r": WILSON_R,
            "energy_eV": ENERGY_EV,
        },
        "clean": clean_json,
        "right_lead_modes": right_records,
        "selected_mode_identity": {
            "canonical_wall": right_wall0,
            "opposite_wall": right_wall1,
        },
        "red_team": {
            "device_mass_shift_A": MISMATCH_SHIFT_A,
            "mismatch": mismatch_json,
            "corrupted_smatrix_amplitude": CORRUPTION_AMPLITUDE,
            "corrupted_smatrix_unitarity_residual_2norm": corrupted_residual,
        },
        "checks": checks,
        "next_gate": (
            "If reproduced on the authority-crossing Kwant CI lane, review C13 evidence. "
            "Do not promote to canonical EXP-004 scientific PASS until the negative controls, "
            "mode identity, and numerical-trust boundary have been reviewed together."
        ),
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
    if result["status"] != "RESEARCH_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
