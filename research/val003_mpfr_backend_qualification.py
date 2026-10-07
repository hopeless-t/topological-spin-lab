"""VAL-003 C02 — independent MPFR/MPC backend qualification.

The lightweight EFT lane from C01 is fast and dependency-light but deliberately
has a bounded validity domain.  C02 qualifies gmpy2/MPFR/MPC as an independent
high-precision adjudicator, widens the exponent Red Team, and post-checks the
C12 margin candidate at 256-bit precision.

This script does not replace NumPy's eigensolver.  It independently recomputes
critical reductions/residuals from the binary64 matrix/eigenpair returned by the
production path.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import platform
import random
from pathlib import Path

import gmpy2
import numpy as np

from topological_spin_lab.verification.numerical_trust import (
    eft_complex_sum_products,
    eft_dot,
    eft_eigen_residual,
    eft_norm,
    two_product,
)

PRECISION_BITS = 256
SAFE_CASES = 512
WIDE_CASES = 512


def mpfr_from_float(value: float):
    return gmpy2.mpfr(float(value))


def mpc_from_complex(value: complex):
    return gmpy2.mpc(
        mpfr_from_float(float(np.real(value))),
        mpfr_from_float(float(np.imag(value))),
    )


def mpfr_dot(x: np.ndarray, y: np.ndarray):
    total = gmpy2.mpfr(0)
    for a, b in zip(x, y, strict=True):
        total += mpfr_from_float(float(a)) * mpfr_from_float(float(b))
    return total


def mpc_sum_products(a: np.ndarray, b: np.ndarray, *, conjugate_a: bool = False):
    total = gmpy2.mpc(0)
    for aa, bb in zip(a, b, strict=True):
        left = mpc_from_complex(complex(aa))
        if conjugate_a:
            left = left.conjugate()
        total += left * mpc_from_complex(complex(bb))
    return total


def mpfr_residual(matrix: np.ndarray, eigenvalue: float, eigenvector: np.ndarray):
    residual = []
    eval_mp = mpfr_from_float(eigenvalue)
    for row_index, row in enumerate(matrix):
        total = mpc_sum_products(row, eigenvector)
        total -= eval_mp * mpc_from_complex(complex(eigenvector[row_index]))
        residual.append(total)
    return residual


def mpfr_complex_norm(values):
    total = gmpy2.mpfr(0)
    for value in values:
        total += value.real * value.real + value.imag * value.imag
    return gmpy2.sqrt(total)


def real_cancellation_kitten(rng: random.Random, length: int, exp_low: int, exp_high: int):
    x: list[float] = []
    y: list[float] = []
    for _ in range(length // 2):
        exponent = rng.randint(exp_low, exp_high)
        magnitude = math.ldexp(rng.uniform(0.5, 1.0), exponent)
        inverse = math.ldexp(rng.uniform(0.5, 1.0), -exponent)
        x.extend((magnitude, magnitude))
        y.extend((inverse, -inverse))

    # Break one exact cancellation by a single representable step.
    index = rng.randrange(length)
    direction = math.inf if y[index] >= 0.0 else -math.inf
    y[index] = math.nextafter(y[index], direction)
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def run_safe_kittens(cases: int, exp_low: int, exp_high: int, seed: int) -> dict:
    rng = random.Random(seed)
    eft_matches = 0
    numpy_matches = 0
    max_eft_vs_mpfr_abs = 0.0
    max_numpy_vs_mpfr_abs = 0.0
    rejected = 0

    for _ in range(cases):
        x, y = real_cancellation_kitten(rng, 64, exp_low, exp_high)
        reference_mp = mpfr_dot(x, y)
        reference = float(reference_mp)
        numpy_value = float(np.dot(x, y))
        try:
            eft_value = eft_dot(x, y)
        except ValueError:
            rejected += 1
            continue

        eft_matches += int(eft_value == reference)
        numpy_matches += int(numpy_value == reference)
        max_eft_vs_mpfr_abs = max(max_eft_vs_mpfr_abs, abs(eft_value - reference))
        max_numpy_vs_mpfr_abs = max(max_numpy_vs_mpfr_abs, abs(numpy_value - reference))

    return {
        "cases": cases,
        "exponent_range": [exp_low, exp_high],
        "eft_rejected": rejected,
        "eft_correctly_rounded_matches_to_mpfr": eft_matches,
        "numpy_matches_to_mpfr": numpy_matches,
        "max_eft_vs_mpfr_abs": max_eft_vs_mpfr_abs,
        "max_numpy_vs_mpfr_abs": max_numpy_vs_mpfr_abs,
    }


def run_boundary_red_team() -> dict:
    cases = {
        "underflow_to_zero": (2.0**-800, 2.0**-300),
        "subnormal_product": (2.0**-1022, 0.5),
        "splitter_overflow": (2.0**1000, 2.0**-1000),
        "ordinary_product_overflow": (2.0**900, 2.0**200),
    }
    out = {}
    for name, (a, b) in cases.items():
        rejected = False
        message = None
        try:
            two_product(a, b)
        except ValueError as exc:
            rejected = True
            message = str(exc)
        mp_value = mpfr_from_float(a) * mpfr_from_float(b)
        out[name] = {
            "a_hex": float(a).hex(),
            "b_hex": float(b).hex(),
            "eft_rejected": rejected,
            "eft_message": message,
            "mpfr_finite": bool(gmpy2.is_finite(mp_value)),
            "mpfr_zero": bool(gmpy2.is_zero(mp_value)),
            "mpfr_value": format(mp_value, ".30e"),
        }
    return out


def load_c12_module():
    path = Path(__file__).with_name("exp004_c12_cost_qualification.py")
    spec = importlib.util.spec_from_file_location("_exp004_c12_for_val003", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load C12 module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_margin_postcheck() -> dict:
    c12 = load_c12_module()
    h, x_A, _, circumference_A = c12.build_hamiltonian(
        8.0,
        c12.PROBE_KY_AINV,
        c12.WILSON_R,
    )
    energy, vector, _ = c12.select_wall_mode(h, x_A, circumference_A, wall=0)

    eft_r = eft_eigen_residual(h, energy, vector)
    eft_r_norm = eft_norm(eft_r)
    mp_r = mpfr_residual(h, energy, vector)
    mp_r_norm = mpfr_complex_norm(mp_r)

    psi = vector.reshape((-1, 2))
    sx_psi = psi[:, ::-1].reshape(-1)
    eft_num = eft_complex_sum_products(vector, sx_psi, conjugate_a=True)
    eft_den = eft_complex_sum_products(vector, vector, conjugate_a=True)
    eft_spin = eft_num / eft_den

    mp_num = mpc_sum_products(vector, sx_psi, conjugate_a=True)
    mp_den = mpc_sum_products(vector, vector, conjugate_a=True)
    mp_spin = mp_num / mp_den

    residual_float = float(mp_r_norm)
    mp_spin_complex = complex(float(mp_spin.real), float(mp_spin.imag))

    return {
        "matrix_dimension": int(h.shape[0]),
        "energy_eV": energy,
        "eft_residual_norm": eft_r_norm,
        "mpfr_residual_norm": residual_float,
        "mpfr_residual_norm_decimal": format(mp_r_norm, ".40e"),
        "residual_norm_abs_delta": abs(eft_r_norm - residual_float),
        "eft_sigma_x_real": float(eft_spin.real),
        "eft_sigma_x_imag": float(eft_spin.imag),
        "mpfr_sigma_x_real": float(mp_spin.real),
        "mpfr_sigma_x_imag": float(mp_spin.imag),
        "sigma_x_abs_delta": abs(eft_spin - mp_spin_complex),
    }


def run() -> dict:
    with gmpy2.context(precision=PRECISION_BITS, round=gmpy2.RoundToNearest):
        normal = run_safe_kittens(SAFE_CASES, -20, 20, 0xC02A)
        wide = run_safe_kittens(WIDE_CASES, -400, 400, 0xC02B)
        boundary = run_boundary_red_team()
        margin = run_margin_postcheck()

    boundary_all_rejected = all(row["eft_rejected"] for row in boundary.values())
    boundary_mpfr_all_finite = all(row["mpfr_finite"] for row in boundary.values())

    checks = {
        "normal_eft_matches_mpfr_all": (
            normal["eft_rejected"] == 0
            and normal["eft_correctly_rounded_matches_to_mpfr"] == normal["cases"]
        ),
        "wide_eft_matches_mpfr_all": (
            wide["eft_rejected"] == 0
            and wide["eft_correctly_rounded_matches_to_mpfr"] == wide["cases"]
        ),
        "dangerous_eft_cases_fail_closed": boundary_all_rejected,
        "dangerous_cases_mpfr_adjudicable": boundary_mpfr_all_finite,
        "margin_mpfr_residual_small": margin["mpfr_residual_norm"] <= 2.0e-15,
        "margin_eft_mpfr_residual_agree": margin["residual_norm_abs_delta"] <= 1.0e-17,
        "margin_eft_mpfr_spin_agree": margin["sigma_x_abs_delta"] <= 5.0e-16,
    }

    return {
        "schema_version": "val003-mpfr-backend-qualification-v0.1",
        "status": "QUALIFICATION_PASS" if all(checks.values()) else "QUALIFICATION_FAIL",
        "authority": (
            "Independent 256-bit MPFR/MPC numerical comparator qualification. "
            "It post-checks binary64 inputs/results; it is not a high-precision eigensolver."
        ),
        "claim_ceiling": (
            "Qualifies MPFR/MPC as an escalation/adjudication backend for the tested "
            "operations and ranges only. It does not certify the physical model or finite-device transport."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "gmpy2": gmpy2.version(),
            "mpfr_version": gmpy2.mpfr_version(),
            "mpc_version": gmpy2.mpc_version(),
            "precision_bits": PRECISION_BITS,
        },
        "checks": checks,
        "normal_exponent_kittens": normal,
        "wide_exponent_kittens": wide,
        "boundary_red_team": boundary,
        "margin_candidate_postcheck": margin,
        "decision": (
            "Use fail-closed EFT as the cheap lane. Escalate rejected/out-of-domain "
            "products and authority-boundary disagreements to the qualified MPFR/MPC lane."
        ),
        "next_gate": (
            "Keep ExBLAS/OzBLAS as optional performance/reproducibility differentials; "
            "do not block the minimal clean EXP-004 implementation on them."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(text, end="")
    if result["status"] != "QUALIFICATION_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
