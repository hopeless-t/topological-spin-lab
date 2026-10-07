"""EXP004-C14: transport acceptance surface and metamorphic controls.

C13 established a clean finite-device known answer at one energy and one device
length.  C14 asks whether that result is structural rather than a tuned point.

The experiment sweeps:

- positive and negative energies inside the magnetic gap;
- several clean device lengths while keeping identical leads;
- lead-mode wall/spin/velocity identity at each sampled energy;
- a Wilson-off r=0 transport control for fermion doubling.

The clean identical-device result should be invariant in transmission magnitude
under device-length changes; only scattering phase is allowed to change.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import kwant
import numpy as np
import scipy

import exp004_c13_clean_scattering as c13

ENERGIES_EV = (-0.015, -0.010, -0.005, 0.005, 0.010, 0.015)
DEVICE_LENGTHS = (3, 5, 9)
REFERENCE_NY = 5
DOUBLER_ENERGY_EV = 0.005

UNITARITY_TOL = 1.0e-8
TRANSPORT_TOL = 2.0e-7
TRANSMISSION_SPREAD_TOL = 5.0e-8
MODE_SPIN_MIN = 0.995
MODE_WALL_WEIGHT_MIN = 0.90


def build_system_ny(ny: int, *, wilson_r: float = c13.WILSON_R):
    if ny < 1:
        raise ValueError("ny must be positive")

    lat = kwant.lattice.square(c13.A_A, norbs=2)
    system = kwant.Builder()
    w, hop_x, hop_y = c13.lattice_terms(wilson_r)

    for iy in range(ny):
        for ix in range(c13.NX):
            x_A = ix * c13.A_A
            system[lat(ix, iy)] = (c13.periodic_mass(x_A) + 2.0 * w) * c13.SZ

    for iy in range(ny):
        for ix in range(c13.NX - 1):
            system[lat(ix, iy), lat(ix + 1, iy)] = hop_x
        system[lat(c13.NX - 1, iy), lat(0, iy)] = hop_x

    for iy in range(ny - 1):
        for ix in range(c13.NX):
            system[lat(ix, iy), lat(ix, iy + 1)] = hop_y

    plus_y = c13.make_plus_y_lead(lat, wilson_r=wilson_r)
    system.attach_lead(plus_y.reversed())
    system.attach_lead(plus_y)
    return system.finalized()


def scattering_at(system, energy_eV: float) -> tuple[dict, object]:
    smatrix = kwant.smatrix(system, energy=energy_eV)
    s = np.asarray(smatrix.data)
    identity = np.eye(s.shape[1], dtype=complex)
    row = {
        "energy_eV": float(energy_eV),
        "s_matrix_shape": [int(v) for v in s.shape],
        "unitarity_residual_2norm": float(
            np.linalg.norm(s.conj().T @ s - identity, ord=2)
        ),
        "transmission_L_to_R": float(smatrix.transmission(1, 0)),
        "reflection_L_to_L": float(smatrix.transmission(0, 0)),
        "transmission_R_to_L": float(smatrix.transmission(0, 1)),
        "reflection_R_to_R": float(smatrix.transmission(1, 1)),
        "left_incoming_channels": int(smatrix.num_propagating(0)),
        "right_incoming_channels": int(smatrix.num_propagating(1)),
    }
    return row, smatrix


def right_lead_mode_records(system, smatrix) -> list[dict]:
    lead_index = 1
    info = smatrix.lead_info[lead_index]
    lead = system.leads[lead_index]
    sites = list(lead.sites[: lead.cell_size])
    if len(sites) != c13.NX:
        raise AssertionError(f"expected {c13.NX} lead sites, got {len(sites)}")
    x_A = np.asarray([float(site.tag[0]) * c13.A_A for site in sites])

    vectors = np.asarray(info.wave_functions)
    velocities = np.asarray(info.velocities)
    momenta = np.asarray(info.momenta)
    if vectors.shape[1] != velocities.size:
        raise AssertionError("mode metadata shape mismatch")

    rows: list[dict] = []
    for index in range(velocities.size):
        rows.append(
            {
                "mode_index": int(index),
                "velocity": float(velocities[index]),
                "momentum": float(momenta[index]),
                **c13._mode_metrics(vectors[:, index], x_A),
            }
        )
    return rows


def select_wall_modes(records: list[dict]) -> tuple[dict, dict]:
    if len(records) != 2:
        raise AssertionError(f"expected two propagating mode vectors, got {len(records)}")
    wall0 = max(records, key=lambda row: row["wall0_weight"])
    wall1 = max(records, key=lambda row: row["wall1_weight"])
    if wall0["mode_index"] == wall1["mode_index"]:
        raise AssertionError("wall classification collapsed to one mode")
    return wall0, wall1


def clean_row_passes(row: dict) -> bool:
    return bool(
        row["left_incoming_channels"] == 1
        and row["right_incoming_channels"] == 1
        and row["unitarity_residual_2norm"] <= UNITARITY_TOL
        and abs(row["transmission_L_to_R"] - 1.0) <= TRANSPORT_TOL
        and abs(row["transmission_R_to_L"] - 1.0) <= TRANSPORT_TOL
        and row["reflection_L_to_L"] <= TRANSPORT_TOL
        and row["reflection_R_to_R"] <= TRANSPORT_TOL
    )


def mode_identity_passes(wall0: dict, wall1: dict) -> bool:
    return bool(
        wall0["wall0_weight"] >= MODE_WALL_WEIGHT_MIN
        and wall1["wall1_weight"] >= MODE_WALL_WEIGHT_MIN
        and wall0["sigma_x"] <= -MODE_SPIN_MIN
        and wall1["sigma_x"] >= MODE_SPIN_MIN
        and wall0["velocity"] > 0.0
        and wall1["velocity"] < 0.0
    )


def run() -> dict:
    systems = {ny: build_system_ny(ny) for ny in DEVICE_LENGTHS}

    grid: list[dict] = []
    identity_rows: list[dict] = []
    per_energy_transmissions: dict[str, list[float]] = {}

    for ny, system in systems.items():
        for energy in ENERGIES_EV:
            row, smatrix = scattering_at(system, energy)
            row["ny"] = int(ny)
            row["clean_gate_pass"] = clean_row_passes(row)
            grid.append(row)
            per_energy_transmissions.setdefault(f"{energy:.6f}", []).append(
                row["transmission_L_to_R"]
            )

            if ny == REFERENCE_NY:
                modes = right_lead_mode_records(system, smatrix)
                wall0, wall1 = select_wall_modes(modes)
                identity_rows.append(
                    {
                        "energy_eV": float(energy),
                        "mode_count": len(modes),
                        "canonical_wall": wall0,
                        "opposite_wall": wall1,
                        "identity_gate_pass": mode_identity_passes(wall0, wall1),
                    }
                )

    transmission_spreads = {
        energy: float(max(values) - min(values))
        for energy, values in per_energy_transmissions.items()
    }

    naive_system = build_system_ny(REFERENCE_NY, wilson_r=0.0)
    naive_row, naive_smatrix = scattering_at(naive_system, DOUBLER_ENERGY_EV)
    naive_total_mode_vectors = [
        int(np.asarray(info.velocities).size) for info in naive_smatrix.lead_info
    ]

    checks = {
        "all_clean_grid_points_pass": all(row["clean_gate_pass"] for row in grid),
        "all_energy_mode_identities_pass": all(
            row["identity_gate_pass"] for row in identity_rows
        ),
        "device_length_transmission_metamorphic": all(
            spread <= TRANSMISSION_SPREAD_TOL
            for spread in transmission_spreads.values()
        ),
        "wilson_off_adds_transport_channels": (
            naive_row["left_incoming_channels"] > 1
            and naive_row["right_incoming_channels"] > 1
            and all(count > 2 for count in naive_total_mode_vectors)
        ),
    }

    return {
        "schema_version": "exp004-c14-transport-acceptance-surface-v0.1",
        "status": "RESEARCH_PASS" if all(checks.values()) else "RESEARCH_FAIL",
        "authority": (
            "Research-only acceptance-surface extension of C13. "
            "No disorder/geometry/material authority."
        ),
        "claim_ceiling": (
            "Establishes only clean generic Wilson-model transport consistency "
            "over the sampled energy/length grid and the r=0 doubler control."
        ),
        "runtime": {
            "python": platform.python_version(),
            "kwant": kwant.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": {
            "energies_eV": list(ENERGIES_EV),
            "device_lengths_ny": list(DEVICE_LENGTHS),
            "reference_ny": REFERENCE_NY,
            "lattice_spacing_A": c13.A_A,
            "wall_separation_xi": 0.5 * c13.L_A / c13.XI_A,
            "wilson_r": c13.WILSON_R,
        },
        "clean_grid": grid,
        "reference_length_mode_identity": identity_rows,
        "transmission_spread_across_lengths_by_energy": transmission_spreads,
        "wilson_off_red_team": {
            "energy_eV": DOUBLER_ENERGY_EV,
            "scattering": naive_row,
            "propagating_mode_vectors_per_lead": naive_total_mode_vectors,
        },
        "checks": checks,
        "next_gate": (
            "If the surface passes, perform an explicit council review separating "
            "solver calibration from physical-model adequacy. Consider promotion of "
            "the generic clean EXP-004 result only; keep VAL-002 as the independent "
            "material-adequacy gate."
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
