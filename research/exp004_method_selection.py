"""Engineering decision support for the EXP-004 contract shape.

This Monte Carlo samples subjective engineering priors.  Winner shares are not
physical probabilities and must never be cited as transport evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

SEED = 20260925
DRAWS = 300_000

CRITERIA = [
    "continuity",
    "known_answer",
    "minimality",
    "transport_directness",
    "spin_clarity",
    "ci_feasibility",
    "low_impl_risk",
    "extensibility",
]

MEANS = {
    "clean_two_terminal_wilson_kwant": [0.96, 0.93, 0.82, 0.97, 0.91, 0.74, 0.80, 0.94],
    "clean_two_terminal_wilson_custom": [0.96, 0.92, 0.72, 0.97, 0.90, 0.91, 0.53, 0.88],
    "wavepacket_propagation": [0.88, 0.76, 0.64, 0.78, 0.86, 0.88, 0.66, 0.80],
    "multi_terminal_qpj": [0.73, 0.58, 0.28, 0.99, 0.82, 0.50, 0.36, 0.97],
    "kubo_response": [0.70, 0.52, 0.48, 0.62, 0.38, 0.90, 0.61, 0.74],
}

SDS = {
    name: [0.04, 0.05, 0.06, 0.03, 0.05, 0.09, 0.08, 0.05]
    for name in MEANS
}

SCENARIOS = {
    "uniform": [1.0] * 8,
    "physics_validation_heavy": [2.2, 2.2, 1.1, 1.4, 1.2, 0.8, 1.0, 0.8],
    "minimal_ci_heavy": [1.1, 1.1, 2.0, 1.0, 0.8, 2.0, 2.0, 0.7],
    "transport_future_heavy": [0.9, 0.8, 0.7, 2.3, 1.1, 0.8, 0.8, 2.0],
    "spin_clarity_heavy": [1.0, 1.0, 0.8, 1.1, 2.8, 0.8, 0.9, 0.8],
}


def run() -> dict:
    rng = np.random.default_rng(SEED)
    winner_share: dict[str, dict[str, float]] = {}

    for scenario, alpha in SCENARIOS.items():
        weights = rng.dirichlet(np.asarray(alpha) * 50.0, size=DRAWS)
        utilities = []
        names = list(MEANS)
        for name in names:
            samples = rng.normal(
                np.asarray(MEANS[name]),
                np.asarray(SDS[name]),
                size=(DRAWS, len(CRITERIA)),
            )
            samples = np.clip(samples, 0.0, 1.0)
            utilities.append(np.sum(samples * weights, axis=1))

        stacked = np.column_stack(utilities)
        winners = np.argmax(stacked, axis=1)
        winner_share[scenario] = {
            name: float(np.mean(winners == index))
            for index, name in enumerate(names)
        }

    return {
        "schema_version": "exp004-contract-selection-v0.1",
        "seed": SEED,
        "trials_per_scenario": DRAWS,
        "criteria": CRITERIA,
        "means": MEANS,
        "sds": SDS,
        "scenarios": SCENARIOS,
        "winner_share": winner_share,
        "claim_ceiling": (
            "Subjective engineering design sensitivity only; "
            "not a physical probability or scientific result."
        ),
    }


def canonical_text(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    parser.add_argument("--check")
    args = parser.parse_args()

    text = canonical_text(run())

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")

    if args.check:
        expected = Path(args.check).read_text(encoding="utf-8")
        if expected != text:
            raise SystemExit("EXP-004 decision-support evidence mismatch")

    if not args.out and not args.check:
        print(text, end="")


if __name__ == "__main__":
    main()
