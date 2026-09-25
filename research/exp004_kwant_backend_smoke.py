"""Kwant backend qualification smoke test for EXP-004.

This is a backend/reproducibility test, not EXP-004 physics evidence.
It uses a clean one-dimensional two-orbital chain with a single propagating
spin-up channel at E=0.  The known answer is T=1, R=0, unitary S, and
<sigma_z>=+1 for the propagating scattering state.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import kwant
import numpy as np
import scipy

ENERGY = 0.0
N_SITES = 7
SPIN_DOWN_OFFSET = 5.0
ATOL = 1e-9

SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
IDENTITY_2 = np.eye(2, dtype=complex)


def build_system():
    lat = kwant.lattice.chain(norbs=2)
    onsite = np.diag([0.0, SPIN_DOWN_OFFSET]).astype(complex)
    hopping = -IDENTITY_2

    system = kwant.Builder()
    for i in range(N_SITES):
        system[lat(i)] = onsite
    for i in range(N_SITES - 1):
        system[lat(i), lat(i + 1)] = hopping

    left = kwant.Builder(kwant.TranslationalSymmetry((-1,)))
    left[lat(0)] = onsite
    left[lat(0), lat(-1)] = hopping

    system.attach_lead(left)
    system.attach_lead(left.reversed())
    return system.finalized()


def spin_z_of_first_incoming_state(system) -> float:
    states = kwant.wave_function(system, energy=ENERGY)(0)
    if states.shape[0] != 1:
        raise AssertionError(f"expected one incoming mode, got {states.shape[0]}")
    psi = states[0].reshape((-1, 2))
    norm = float(np.sum(np.abs(psi) ** 2))
    if norm <= 0:
        raise AssertionError("wave-function norm is zero")
    numerator = 0.0 + 0.0j
    for spinor in psi:
        numerator += np.vdot(spinor, SIGMA_Z @ spinor)
    return float((numerator / norm).real)


def run() -> dict:
    system = build_system()
    smatrix = kwant.smatrix(system, energy=ENERGY)
    s = np.asarray(smatrix.data)

    unitarity_residual = float(
        np.linalg.norm(s.conj().T @ s - np.eye(s.shape[1]), ord=2)
    )
    transmission_lr = float(smatrix.transmission(1, 0))
    reflection_ll = float(smatrix.transmission(0, 0))
    spin_z = spin_z_of_first_incoming_state(system)
    n_left = int(smatrix.num_propagating(0))
    n_right = int(smatrix.num_propagating(1))

    checks = {
        "kwant_version_is_1_5_0": kwant.__version__ == "1.5.0",
        "one_left_propagating_mode": n_left == 1,
        "one_right_propagating_mode": n_right == 1,
        "unitarity": unitarity_residual <= ATOL,
        "perfect_transmission": abs(transmission_lr - 1.0) <= ATOL,
        "zero_reflection": abs(reflection_ll) <= ATOL,
        "spin_up_polarization": abs(spin_z - 1.0) <= ATOL,
    }

    return {
        "schema_version": "exp004-kwant-backend-smoke-v0.1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_ceiling": (
            "Backend qualification only. This does not validate the Wilson "
            "domain-wall Hamiltonian or authorize EXP-004 transport."
        ),
        "runtime": {
            "python": platform.python_version(),
            "kwant": kwant.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "known_answer": {
            "energy": ENERGY,
            "sites": N_SITES,
            "spin_down_onsite_offset": SPIN_DOWN_OFFSET,
        },
        "observed": {
            "left_propagating_modes": n_left,
            "right_propagating_modes": n_right,
            "transmission_L_to_R": transmission_lr,
            "reflection_L_to_L": reflection_ll,
            "s_matrix_unitarity_residual_2norm": unitarity_residual,
            "incoming_state_sigma_z": spin_z,
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
