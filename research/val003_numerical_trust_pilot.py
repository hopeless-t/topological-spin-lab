"""VAL-003 C01 numerical-trust pilot.

This pilot combines four independent trust mechanisms:

1. Ozaki-Scheme-II-inspired CRT exact integer GEMM micro-oracle.
2. Dekker TwoProduct EFT + accurate reduction for floating-point dot products.
3. Deterministic "numerical kitten" adversarial cases with exact Fraction oracles.
4. Metamorphic and residual checks on the current Wilson-domain-wall Hamiltonian.

Research-only. This does not promote EXP-004 transport or constitute a native
ExBLAS/OzBLAS implementation.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
from pathlib import Path

import numpy as np

from topological_spin_lab.verification.numerical_trust import (
    crt_exact_matmul,
    eft_complex_sum_products,
    eft_dot,
    eft_eigen_residual,
    eft_norm,
    exact_complex_sum_products_fraction,
    exact_dot_fraction,
    verify_matmul_modulus,
)

ALPHA_EV_A = 1.0
M0_EV = 0.020
WALL_WIDTH_A = 50.0
XI_A = ALPHA_EV_A / M0_EV
WILSON_R = 0.5
A_A = 10.0
WALL_SEPARATION_XI = 8
PROBE_KY_AINV = 0.005

S_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
S_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
S_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def _ulp_error(value: float, reference: float) -> float:
    if value == reference:
        return 0.0
    scale = math.ulp(reference if reference != 0.0 else 1.0)
    return abs(value - reference) / scale


def _real_kitten(rng: random.Random, length: int) -> tuple[np.ndarray, np.ndarray]:
    """Cancellation-heavy dot product with a tiny representable residual."""
    x: list[float] = []
    y: list[float] = []
    for _ in range(length // 2):
        exponent = rng.randint(-20, 20)
        magnitude = math.ldexp(rng.uniform(0.5, 1.0), exponent)
        x.extend((magnitude, magnitude))
        y.extend((1.0, -1.0))

    index = rng.randrange(length)
    direction = math.inf if y[index] > 0.0 else -math.inf
    y[index] = math.nextafter(y[index], direction)
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def run_real_dot_kittens(cases: int, length: int = 64) -> dict:
    rng = random.Random(0xC47)
    correct = {"numpy": 0, "fsum_products": 0, "eft": 0}
    max_ulp = {"numpy": 0.0, "fsum_products": 0.0, "eft": 0.0}
    permutation_failures = 0
    power_of_two_scale_failures = 0

    for _ in range(cases):
        x, y = _real_kitten(rng, length)
        exact = exact_dot_fraction(x, y)
        reference = float(exact)

        observed = {
            "numpy": float(np.dot(x, y)),
            "fsum_products": math.fsum(
                float(a) * float(b) for a, b in zip(x, y, strict=True)
            ),
            "eft": eft_dot(x, y),
        }
        for name, value in observed.items():
            if value == reference:
                correct[name] += 1
            max_ulp[name] = max(max_ulp[name], _ulp_error(value, reference))

        order = list(range(length))
        rng.shuffle(order)
        if eft_dot(x[order], y[order]) != reference:
            permutation_failures += 1

        exponent = rng.randint(-20, 20)
        x_scaled = np.ldexp(x, exponent)
        y_scaled = np.ldexp(y, -exponent)
        if eft_dot(x_scaled, y_scaled) != reference:
            power_of_two_scale_failures += 1

    return {
        "cases": cases,
        "length": length,
        "correctly_rounded_matches": correct,
        "max_ulp_error": max_ulp,
        "metamorphic": {
            "permutation_failures_eft": permutation_failures,
            "power_of_two_rescale_failures_eft": power_of_two_scale_failures,
        },
    }


def run_complex_dot_kittens(cases: int, length: int = 32) -> dict:
    rng = random.Random(0xC0FFEE)
    eft_correct = 0
    numpy_correct = 0
    max_numpy_abs_error = 0.0

    for _ in range(cases):
        a: list[complex] = []
        b: list[complex] = []
        for _ in range(length):
            values = [
                math.ldexp(rng.uniform(-1.0, 1.0), rng.randint(-20, 20))
                for _ in range(4)
            ]
            a.append(complex(values[0], values[1]))
            b.append(complex(values[2], values[3]))

        exact_real, exact_imag = exact_complex_sum_products_fraction(a, b)
        reference = complex(float(exact_real), float(exact_imag))
        eft_value = eft_complex_sum_products(a, b)
        numpy_value = complex(np.dot(np.asarray(a), np.asarray(b)))

        eft_correct += int(eft_value == reference)
        numpy_correct += int(numpy_value == reference)
        max_numpy_abs_error = max(max_numpy_abs_error, abs(numpy_value - reference))

    return {
        "cases": cases,
        "length": length,
        "correctly_rounded_matches": {
            "numpy": numpy_correct,
            "eft": eft_correct,
        },
        "max_numpy_abs_error": max_numpy_abs_error,
    }


def run_crt_micro_oracle(cases: int) -> dict:
    rng = random.Random(0x0A2A)
    passes = 0
    max_bound = 0
    dynamic_range = None

    for _ in range(cases):
        rows = rng.randint(2, 6)
        inner = rng.randint(2, 6)
        cols = rng.randint(2, 6)
        a = np.asarray(
            [[rng.randint(-100, 100) for _ in range(inner)] for _ in range(rows)],
            dtype=object,
        )
        b = np.asarray(
            [[rng.randint(-100, 100) for _ in range(cols)] for _ in range(inner)],
            dtype=object,
        )

        observed, metadata = crt_exact_matmul(a, b)
        expected = a @ b
        max_bound = max(max_bound, metadata["absolute_product_bound"])
        dynamic_range = metadata["crt_dynamic_range"]
        if np.array_equal(observed, expected) and verify_matmul_modulus(a, b, observed):
            passes += 1

    overflow_rejected = False
    too_large_a = np.full((2, 8), 1000, dtype=object)
    too_large_b = np.full((8, 2), 1000, dtype=object)
    try:
        crt_exact_matmul(too_large_a, too_large_b)
    except ValueError:
        overflow_rejected = True

    control_a = np.asarray([[3, -7, 2], [5, 11, -4]], dtype=object)
    control_b = np.asarray([[9, 1], [-2, 6], [8, -5]], dtype=object)
    control_c, _ = crt_exact_matmul(control_a, control_b)
    corrupted = control_c.copy()
    corrupted[0, 0] = int(corrupted[0, 0]) + 1
    corruption_detected = not verify_matmul_modulus(control_a, control_b, corrupted)

    return {
        "cases": cases,
        "exact_matches": passes,
        "primary_moduli": [127, 125, 121],
        "independent_check_modulus": 113,
        "crt_dynamic_range": dynamic_range,
        "maximum_tested_absolute_product_bound": max_bound,
        "red_team": {
            "capacity_overflow_rejected": overflow_rejected,
            "corrupted_reconstruction_detected": corruption_detected,
        },
    }


def periodic_mass(x_A: float, circumference_A: float) -> float:
    scale = 2.0 * math.pi * WALL_WIDTH_A / circumference_A
    return M0_EV * math.tanh(
        math.sin(2.0 * math.pi * x_A / circumference_A) / scale
    )


def build_reference_hamiltonian() -> tuple[np.ndarray, np.ndarray, float]:
    """Independently reconstruct the C10 10 A / 8 xi lead Hamiltonian."""
    separation_A = WALL_SEPARATION_XI * XI_A
    circumference_A = 2.0 * separation_A
    nx = int(round(circumference_A / A_A))
    a_eff_A = circumference_A / nx
    wilson_scale = WILSON_R * ALPHA_EV_A / a_eff_A

    hop_x = (
        (-1.0j * ALPHA_EV_A / (2.0 * a_eff_A)) * S_Y
        - 0.5 * wilson_scale * S_Z
    )
    hop_y = (
        (+1.0j * ALPHA_EV_A / (2.0 * a_eff_A)) * S_X
        - 0.5 * wilson_scale * S_Z
    )
    phase = PROBE_KY_AINV * a_eff_A
    y_bloch = hop_y * np.exp(1.0j * phase) + hop_y.conj().T * np.exp(-1.0j * phase)

    h = np.zeros((2 * nx, 2 * nx), dtype=complex)
    x_A = np.arange(nx, dtype=float) * a_eff_A
    for ix, x_value in enumerate(x_A):
        onsite = (
            periodic_mass(float(x_value), circumference_A) + 2.0 * wilson_scale
        ) * S_Z
        block = 2 * ix
        h[block : block + 2, block : block + 2] = onsite + y_bloch
        other = 2 * ((ix + 1) % nx)
        h[block : block + 2, other : other + 2] += hop_x
        h[other : other + 2, block : block + 2] += hop_x.conj().T

    return h, x_A, circumference_A


def _ring_distance(values: np.ndarray, center: float, circumference: float) -> np.ndarray:
    delta = np.abs(values - center) % circumference
    return np.minimum(delta, circumference - delta)


def select_canonical_wall_mode(
    h: np.ndarray,
    x_A: np.ndarray,
    circumference_A: float,
) -> tuple[float, np.ndarray]:
    energies, vectors = np.linalg.eigh(h)
    wall0 = _ring_distance(x_A, 0.0, circumference_A) <= 2.0 * XI_A
    wall1 = (
        _ring_distance(x_A, 0.5 * circumference_A, circumference_A)
        <= 2.0 * XI_A
    )

    best = None
    for index in np.argsort(np.abs(energies))[:12]:
        psi = vectors[:, index].reshape((len(x_A), 2))
        density = np.sum(np.abs(psi) ** 2, axis=1)
        density /= np.sum(density)
        score = float(np.sum(density[wall0]) - np.sum(density[wall1]))
        candidate = (score, float(energies[index]), vectors[:, index])
        if best is None or candidate[0] > best[0]:
            best = candidate

    assert best is not None
    return best[1], np.asarray(best[2], dtype=complex)


def spin_x_eft(vector: np.ndarray) -> complex:
    psi = np.asarray(vector, dtype=complex).reshape((-1, 2))
    sx_psi = psi[:, ::-1].reshape(-1)
    numerator = eft_complex_sum_products(vector, sx_psi, conjugate_a=True)
    denominator = eft_complex_sum_products(vector, vector, conjugate_a=True)
    return numerator / denominator


def run_domain_wall_postcheck() -> dict:
    h, x_A, circumference_A = build_reference_hamiltonian()
    energy, vector = select_canonical_wall_mode(h, x_A, circumference_A)

    ordinary_residual = h @ vector - energy * vector
    eft_residual = eft_eigen_residual(h, energy, vector)
    ordinary_norm = float(np.linalg.norm(ordinary_residual))
    eft_residual_norm = eft_norm(eft_residual)
    spin = spin_x_eft(vector)

    phase_values = []
    for step in range(32):
        theta = 2.0 * math.pi * step / 32.0
        phase = complex(math.cos(theta), math.sin(theta))
        phase_values.append(spin_x_eft(vector * phase))
    phase_max_deviation = max(abs(value - spin) for value in phase_values)

    return {
        "matrix_dimension": int(h.shape[0]),
        "energy_eV": energy,
        "ordinary_residual_norm": ordinary_norm,
        "eft_residual_norm": eft_residual_norm,
        "ordinary_vs_eft_residual_vector_max_abs_delta": float(
            np.max(np.abs(ordinary_residual - eft_residual))
        ),
        "sigma_x_eft_real": float(spin.real),
        "sigma_x_eft_imag": float(spin.imag),
        "metamorphic": {
            "global_phase_trials": len(phase_values),
            "sigma_x_max_abs_deviation": float(phase_max_deviation),
        },
    }


def run(*, real_kittens: int, complex_kittens: int, crt_cases: int) -> dict:
    crt = run_crt_micro_oracle(crt_cases)
    real_dot = run_real_dot_kittens(real_kittens)
    complex_dot = run_complex_dot_kittens(complex_kittens)
    domain_wall = run_domain_wall_postcheck()

    checks = {
        "crt_exact_all_cases": crt["exact_matches"] == crt["cases"],
        "crt_capacity_red_team": crt["red_team"]["capacity_overflow_rejected"],
        "crt_corruption_red_team": crt["red_team"]["corrupted_reconstruction_detected"],
        "real_eft_matches_exact_all_cases": (
            real_dot["correctly_rounded_matches"]["eft"] == real_dot["cases"]
        ),
        "real_eft_permutation_invariant": (
            real_dot["metamorphic"]["permutation_failures_eft"] == 0
        ),
        "real_eft_power_of_two_scale_invariant": (
            real_dot["metamorphic"]["power_of_two_rescale_failures_eft"] == 0
        ),
        "complex_eft_matches_exact_all_cases": (
            complex_dot["correctly_rounded_matches"]["eft"] == complex_dot["cases"]
        ),
        "domain_wall_eft_residual_small": domain_wall["eft_residual_norm"] <= 2.0e-15,
        "domain_wall_spin_real": abs(domain_wall["sigma_x_eft_imag"]) <= 1.0e-15,
        "domain_wall_global_phase_invariant": (
            domain_wall["metamorphic"]["sigma_x_max_abs_deviation"] <= 5.0e-15
        ),
    }

    return {
        "schema_version": "val003-numerical-trust-pilot-v0.1",
        "status": "EXPLORATORY_PASS" if all(checks.values()) else "EXPLORATORY_FAIL",
        "authority": (
            "Research-only numerical-trust pilot. The CRT path is an "
            "Ozaki-Scheme-II-inspired micro-oracle, not a full high-performance "
            "Ozaki Scheme II implementation. The EFT path uses Dekker TwoProduct "
            "+ math.fsum and is not a native NearSum/ExBLAS/OzBLAS implementation."
        ),
        "claim_ceiling": (
            "Demonstrates bounded exact/accurate verification mechanisms only. "
            "It does not certify all floating-point operations, the eigensolver, "
            "EXP-004 transport, or any material-specific NdBi prediction."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "checks": checks,
        "crt_micro_oracle": crt,
        "real_dot_kittens": real_dot,
        "complex_dot_kittens": complex_dot,
        "domain_wall_postcheck": domain_wall,
        "next_gate": (
            "VAL003-C02: add an independent high-precision/native backend lane "
            "(MPFR/ExBLAS/OzBLAS candidate), widen exponent-range Red Teams, and "
            "cross-check the C12 economy/margin candidates before any authority promotion."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--real-kittens", type=int, default=1024)
    parser.add_argument("--complex-kittens", type=int, default=256)
    parser.add_argument("--crt-cases", type=int, default=256)
    args = parser.parse_args()

    result = run(
        real_kittens=args.real_kittens,
        complex_kittens=args.complex_kittens,
        crt_cases=args.crt_cases,
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(text, end="")
    if result["status"] != "EXPLORATORY_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
