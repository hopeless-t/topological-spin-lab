"""Threshold-sensitivity Monte Carlo for VAL-001.

This is engineering decision support. It varies plausible acceptance thresholds
around the frozen hard-gate region to measure how stable each regulator
variant's PASS/FAIL classification is. The probabilities are not physical
probabilities.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

DRAWS = 300_000
SEED = 20260920


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    parser.add_argument("--out", type=Path)
    return parser


def _method_key(summary: dict[str, object]) -> str:
    method = str(summary["method"])
    wilson_r = summary["wilson_r"]
    if method == "stacey":
        return "stacey"
    return f"wilson:r={float(wilson_r):g}"


def run_sensitivity(summary_payload: dict[str, object]) -> dict[str, object]:
    rng = np.random.default_rng(SEED)

    overlap_min = rng.uniform(0.97, 0.9995, DRAWS)
    finest_profile_l1_max = rng.uniform(0.005, 0.06, DRAWS)
    wall_weight_min = rng.uniform(0.97, 0.9955, DRAWS)
    energy_error_max = 10.0 ** rng.uniform(-12.5, -8.0, DRAWS)
    edge_weight_max = 10.0 ** rng.uniform(-7.5, -4.0, DRAWS)
    spin_x_error_max = 10.0 ** rng.uniform(-10.5, -6.0, DRAWS)

    probabilities: dict[str, float] = {}
    for method_summary in summary_payload["method_summaries"]:
        key = _method_key(method_summary)

        deterministic_gates = bool(
            method_summary["max_ghost_wall_modes"] == 0
            and method_summary["max_boundary_artifacts"] <= 1
            and method_summary["max_other_in_gap_modes"] == 0
            and method_summary["monotone_profile_convergence"]
        )

        dynamic = (
            (float(method_summary["min_target_overlap"]) >= overlap_min)
            & (
                float(method_summary["finest_profile_l1_error"])
                <= finest_profile_l1_max
            )
            & (
                float(method_summary["min_target_wall_weight"])
                >= wall_weight_min
            )
            & (
                float(method_summary["max_energy_error_eV"])
                <= energy_error_max
            )
            & (
                float(method_summary["max_target_edge_weight"])
                <= edge_weight_max
            )
            & (
                float(method_summary["max_spin_x_error"])
                <= spin_x_error_max
            )
        )
        probabilities[key] = float(np.mean(dynamic)) if deterministic_gates else 0.0

    best_wilson = max(
        (
            (key, probability)
            for key, probability in probabilities.items()
            if key.startswith("wilson:")
        ),
        key=lambda item: item[1],
    )

    return {
        "authority": "engineering_decision_support_only",
        "draws": DRAWS,
        "seed": SEED,
        "threshold_model": {
            "target_overlap_min": "Uniform(0.97, 0.9995)",
            "finest_profile_l1_max": "Uniform(0.005, 0.06)",
            "target_wall_weight_min": "Uniform(0.97, 0.9955)",
            "target_energy_abs_eV": "LogUniform(10^-12.5, 10^-8)",
            "target_edge_weight_max": "LogUniform(10^-7.5, 10^-4)",
            "spin_x_abs": "LogUniform(10^-10.5, 10^-6)",
        },
        "pass_probability_under_threshold_model": probabilities,
        "most_robust_wilson_variant": best_wilson[0],
    }


def main() -> int:
    args = _parser().parse_args()
    payload = json.loads(args.summary.read_text(encoding="utf-8"))
    result = run_sensitivity(payload)

    print(json.dumps(result, indent=2, sort_keys=True))
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
