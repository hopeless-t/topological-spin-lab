"""Engineering decision support for selecting the EXP-004 Kwant lane.

The Monte Carlo winner shares are sensitivity to subjective engineering priors.
They are not scientific probabilities and do not qualify a transport result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

SEED = 20260925
DRAWS = 300_000

CRITERIA = [
    "release_stability",
    "numpy2_alignment",
    "reproducibility",
    "maintenance",
    "ci_cost",
    "tooling_maturity",
    "future_support",
    "low_isolation_complexity",
]

MEANS = {
    "stable_isolated_numpy1": [0.96, 0.42, 0.95, 0.66, 0.58, 0.96, 0.55, 0.48],
    "pinned_dev_numpy2": [0.62, 0.99, 0.93, 0.84, 0.72, 0.96, 0.93, 0.90],
    "custom_solver_numpy2": [0.88, 1.00, 0.91, 0.35, 0.92, 0.42, 0.78, 1.00],
}

SDS = {
    name: [0.03, 0.06, 0.04, 0.07, 0.08, 0.03, 0.07, 0.08]
    for name in MEANS
}

SCENARIOS = {
    "uniform": [1.0] * 8,
    "stability_heavy": [2.5, 0.7, 1.7, 1.5, 0.8, 1.2, 0.7, 0.8],
    "stack_alignment_heavy": [0.8, 2.8, 1.3, 1.0, 0.9, 1.0, 1.5, 1.5],
    "maintenance_heavy": [1.2, 1.0, 1.3, 2.7, 1.6, 1.0, 1.5, 2.0],
    "reproducibility_heavy": [1.3, 1.0, 3.0, 1.5, 0.8, 1.4, 1.0, 1.0],
    "release_hardline": [6.0, 0.4, 1.5, 1.2, 0.8, 1.0, 0.5, 0.6],
}


def run() -> dict:
    rng = np.random.default_rng(SEED)
    shares: dict[str, dict[str, float]] = {}

    for scenario, alpha in SCENARIOS.items():
        weights = rng.dirichlet(np.asarray(alpha) * 50.0, size=DRAWS)
        names = list(MEANS)
        utilities = []
        for name in names:
            samples = rng.normal(
                np.asarray(MEANS[name]),
                np.asarray(SDS[name]),
                size=(DRAWS, len(CRITERIA)),
            )
            samples = np.clip(samples, 0.0, 1.0)
            utilities.append(np.sum(samples * weights, axis=1))
        winners = np.argmax(np.column_stack(utilities), axis=1)
        shares[scenario] = {
            name: float(np.mean(winners == index))
            for index, name in enumerate(names)
        }

    return {
        "schema_version": "exp004-kwant-lane-selection-v0.1",
        "seed": SEED,
        "trials_per_scenario": DRAWS,
        "criteria": CRITERIA,
        "means": MEANS,
        "sds": SDS,
        "scenarios": SCENARIOS,
        "winner_share": shares,
        "claim_ceiling": (
            "Subjective engineering sensitivity only. "
            "Not a scientific probability and not a transport result."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    parser.add_argument("--check")
    args = parser.parse_args()

    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")

    if args.check:
        expected = json.loads(Path(args.check).read_text(encoding="utf-8"))
        if expected != result:
            raise SystemExit("EXP-004 Kwant-lane evidence mismatch")

    if not args.out and not args.check:
        print(text, end="")


if __name__ == "__main__":
    main()
