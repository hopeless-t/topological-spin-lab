from fractions import Fraction

import numpy as np
import pytest

from topological_spin_lab.verification.numerical_trust import (
    crt_exact_matmul,
    eft_complex_sum_products,
    eft_dot,
    exact_complex_sum_products_fraction,
    exact_dot_fraction,
    two_product,
    verify_matmul_modulus,
)


def test_two_product_recovers_binary64_product_error():
    samples = [
        (1.1, 3.7),
        (2.0**20 + 0.5, 2.0**-12 + 2.0**-40),
        (-12345.6789, 0.000976562500000111),
    ]
    for a, b in samples:
        product, error = two_product(a, b)
        exact = Fraction.from_float(a) * Fraction.from_float(b)
        recovered = Fraction.from_float(product) + Fraction.from_float(error)
        assert recovered == exact


def test_eft_dot_matches_exact_fraction_oracle_on_cancellation():
    x = np.asarray([2.0**20, 2.0**20, 1.0, 1.0], dtype=float)
    y = np.asarray([1.0, -1.0, 1.0, -np.nextafter(1.0, np.inf)], dtype=float)
    reference = float(exact_dot_fraction(x, y))
    assert eft_dot(x, y) == reference


def test_complex_eft_matches_exact_fraction_oracle():
    a = np.asarray([1.1 + 2.2j, -(2.0**10) + 0.25j, 3.5 - 7.0j])
    b = np.asarray([4.4 - 5.5j, 2.0**-10 - 0.125j, -2.0 + 0.75j])
    real, imag = exact_complex_sum_products_fraction(a, b)
    assert eft_complex_sum_products(a, b) == complex(float(real), float(imag))


def test_crt_micro_gemm_matches_integer_oracle_and_check_modulus():
    a = np.asarray([[3, -7, 2], [5, 11, -4]], dtype=object)
    b = np.asarray([[9, 1], [-2, 6], [8, -5]], dtype=object)
    observed, metadata = crt_exact_matmul(a, b)
    assert np.array_equal(observed, a @ b)
    assert metadata["crt_dynamic_range"] == 127 * 125 * 121
    assert verify_matmul_modulus(a, b, observed)


def test_crt_micro_gemm_fails_closed_outside_dynamic_range():
    a = np.full((2, 8), 1000, dtype=object)
    b = np.full((8, 2), 1000, dtype=object)
    with pytest.raises(ValueError, match="CRT capacity exceeded"):
        crt_exact_matmul(a, b)
