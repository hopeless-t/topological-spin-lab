"""Monte Carlo decision support for VAL-001.

This script encodes subjective engineering priors used to choose the next
calculation. It does not produce scientific evidence or probabilities about
physical systems.
"""

from __future__ import annotations

import numpy as np

DRAWS = 200_000
SEED = 20260920


def winner_probabilities(
    rng: np.random.Generator,
    criteria_weights: list[float],
    means: dict[str, list[float]],
    sds: dict[str, list[float]],
) -> dict[str, float]:
    weights = rng.dirichlet(np.asarray(criteria_weights) * 80.0, size=DRAWS)
    names = list(means)
    utilities = []

    for name in names:
        samples = rng.normal(
            np.asarray(means[name]),
            np.asarray(sds[name]),
            size=(DRAWS, len(criteria_weights)),
        )
        samples = np.clip(samples, 0.0, 1.0)
        utilities.append(np.sum(samples * weights, axis=1))

    stacked = np.column_stack(utilities)
    winners = np.argmax(stacked, axis=1)
    return {
        name: float(np.mean(winners == index))
        for index, name in enumerate(names)
    }


def print_rank(title: str, probabilities: dict[str, float]) -> None:
    print(title)
    for name, probability in sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"  {name:28s} {probability:0.6f}")


def main() -> None:
    rng = np.random.default_rng(SEED)

    route_weights = [0.20, 0.18, 0.18, 0.12, 0.12, 0.12, 0.08]
    route_means = {
        "staggered_grid": [0.84, 0.86, 0.90, 0.82, 0.76, 0.96, 0.88],
        "wilson_lattice": [0.91, 0.92, 0.96, 0.58, 0.91, 0.88, 0.84],
        "kwant_transport": [0.83, 0.94, 0.76, 0.52, 0.96, 0.76, 0.72],
        "afm_symmetry_model": [0.73, 0.96, 0.65, 0.36, 0.91, 0.58, 0.55],
        "paired_regulator_pilot": [0.89, 0.97, 0.99, 0.76, 0.87, 0.97, 0.92],
    }
    route_sds = {
        "staggered_grid": [0.05, 0.06, 0.05, 0.07, 0.08, 0.04, 0.05],
        "wilson_lattice": [0.04, 0.05, 0.03, 0.09, 0.05, 0.06, 0.06],
        "kwant_transport": [0.05, 0.04, 0.08, 0.10, 0.03, 0.08, 0.08],
        "afm_symmetry_model": [0.08, 0.03, 0.10, 0.10, 0.05, 0.10, 0.12],
        "paired_regulator_pilot": [0.04, 0.03, 0.02, 0.06, 0.06, 0.03, 0.04],
    }

    sampling_weights = [0.25, 0.25, 0.20, 0.18, 0.12]
    sampling_means = {
        "3_grids_x_5_ky": [0.93, 0.92, 0.90, 0.84, 0.90],
        "2_grids_x_3_ky": [0.72, 0.63, 0.70, 0.98, 0.97],
        "4_grids_x_9_ky": [0.99, 0.99, 0.99, 0.48, 0.68],
        "1_grid_x_101_ky": [0.80, 0.30, 0.99, 0.45, 0.65],
    }
    sampling_sds = {
        name: [0.04, 0.05, 0.05, 0.06, 0.05]
        for name in sampling_means
    }

    wilson_weights = [0.28, 0.22, 0.20, 0.18, 0.12]
    wilson_means = {
        "r1_only_3x5": [0.82, 0.72, 0.55, 0.94, 0.93],
        "r_sweep_3x5": [0.96, 0.94, 0.93, 0.76, 0.88],
        "r_sweep_2x3": [0.82, 0.89, 0.88, 0.92, 0.90],
        "r_sweep_4x9": [0.99, 0.97, 0.96, 0.42, 0.72],
    }
    wilson_sds = {
        name: [0.04, 0.05, 0.06, 0.05, 0.05]
        for name in wilson_means
    }

    print_rank(
        "route",
        winner_probabilities(rng, route_weights, route_means, route_sds),
    )
    print_rank(
        "sampling",
        winner_probabilities(rng, sampling_weights, sampling_means, sampling_sds),
    )
    print_rank(
        "wilson_parameter_design",
        winner_probabilities(rng, wilson_weights, wilson_means, wilson_sds),
    )


if __name__ == "__main__":
    main()
