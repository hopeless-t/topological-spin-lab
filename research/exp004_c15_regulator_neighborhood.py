"""EXP004-C15: bounded Wilson-regulator neighborhood sensitivity.

C15 does not reopen regulator optimization.  VAL-001/C12 keep r=0.5 frozen.
This experiment asks only whether the clean finite-scattering known answer is
stable under a small neighborhood around that reference while the already
established r=0 doubler remains the failed control.
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
import exp004_c14_transport_acceptance_surface as c14

WILSON_RS = (0.4, 0.5, 0.6)
ENERGIES_EV = (-0.015, -0.005, 0.005, 0.015)
NY = 5

UNITARITY_TOL = 1.0e-8
TRANSPORT_TOL = 2.0e-7
MODE_SPIN_MIN = 0.995
MODE_WALL_WEIGHT_MIN = 0.90


def row_passes(scattering: dict, wall0: dict, wall1: dict) -> bool:
    return bool(
        scattering["left_incoming_channels"] == 1
        and scattering["right_incoming_channels"] == 1
        and scattering["unitarity_residual_2norm"] <= UNITARITY_TOL
        and abs(scattering["transmission_L_to_R"] - 1.0) <= TRANSPORT_TOL
        and abs(scattering["transmission_R_to_L"] - 1.0) <= TRANSPORT_TOL
        and scattering["reflection_L_to_L"] <= TRANSPORT_TOL
        and scattering["reflection_R_to_R"] <= TRANSPORT_TOL
        and wall0["wall0_weight"] >= MODE_WALL_WEIGHT_MIN
        and wall1["wall1_weight"] >= MODE_WALL_WEIGHT_MIN
        and wall0["sigma_x"] <= -MODE_SPIN_MIN
        and wall1["sigma_x"] >= MODE_SPIN_MIN
        and wall0["velocity"] > 0.0
        and wall1["velocity"] < 0.0
    )


def run() -> dict:
    rows: list[dict] = []

    for wilson_r in WILSON_RS:
        system = c14.build_system_ny(NY, wilson_r=wilson_r)
        for energy in ENERGIES_EV:
            scattering, smatrix = c14.scattering_at(system, energy)
            modes = c14.right_lead_mode_records(system, smatrix)
            wall0, wall1 = c14.select_wall_modes(modes)
            rows.append(
                {
                    "wilson_r": float(wilson_r),
                    "energy_eV": float(energy),
                    "scattering": scattering,
                    "mode_count": len(modes),
                    "canonical_wall": wall0,
                    "opposite_wall": wall1,
                    "gate_pass": row_passes(scattering, wall0, wall1),
                }
            )

    by_r: dict[str, dict] = {}
    for wilson_r in WILSON_RS:
        subset = [row for row in rows if row["wilson_r"] == wilson_r]
        by_r[f"{wilson_r:.3f}"] = {
            "all_energies_pass": all(row["gate_pass"] for row in subset),
            "max_unitarity_residual": max(
                row["scattering"]["unitarity_residual_2norm"] for row in subset
            ),
            "max_abs_transmission_error": max(
                abs(row["scattering"]["transmission_L_to_R"] - 1.0)
                for row in subset
            ),
            "max_reflection": max(
                row["scattering"]["reflection_L_to_L"] for row in subset
            ),
            "min_canonical_wall_weight": min(
                row["canonical_wall"]["wall0_weight"] for row in subset
            ),
            "min_opposite_wall_weight": min(
                row["opposite_wall"]["wall1_weight"] for row in subset
            ),
            "min_abs_sigma_x": min(
                min(
                    abs(row["canonical_wall"]["sigma_x"]),
                    abs(row["opposite_wall"]["sigma_x"]),
                )
                for row in subset
            ),
        }

    checks = {
        "all_neighborhood_points_pass": all(row["gate_pass"] for row in rows),
        "each_regulator_value_passes_all_energies": all(
            summary["all_energies_pass"] for summary in by_r.values()
        ),
        "reference_r_remains_in_neighborhood": 0.5 in WILSON_RS,
        "no_regulator_reoptimization_performed": True,
    }

    return {
        "schema_version": "exp004-c15-regulator-neighborhood-v0.1",
        "status": "RESEARCH_PASS" if all(checks.values()) else "RESEARCH_FAIL",
        "authority": (
            "Bounded sensitivity around the already frozen Wilson r=0.5 reference. "
            "This is not regulator optimization."
        ),
        "claim_ceiling": (
            "Supports generic clean-model regulator-neighborhood stability only. "
            "No disorder, geometry, interaction, dephasing, or material claim."
        ),
        "runtime": {
            "python": platform.python_version(),
            "kwant": kwant.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": {
            "wilson_r_values": list(WILSON_RS),
            "energies_eV": list(ENERGIES_EV),
            "ny": NY,
            "lattice_spacing_A": c13.A_A,
            "wall_separation_xi": 0.5 * c13.L_A / c13.XI_A,
        },
        "rows": rows,
        "summary_by_r": by_r,
        "checks": checks,
        "known_failed_control_from_c14": {
            "wilson_r": 0.0,
            "energy_eV": 0.005,
            "incoming_channels_per_lead": 4,
            "transmission_L_to_R": 4.0000000000000036,
            "meaning": (
                "C14 directly detected transport-level fermion doubling when the "
                "Wilson regulator is removed."
            ),
        },
        "next_gate": (
            "If C15 passes, perform the explicit EXP-004 promotion council. "
            "The council may promote only the frozen generic clean known-answer "
            "transport claim; VAL-002 remains an independent unsatisfied material gate."
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
