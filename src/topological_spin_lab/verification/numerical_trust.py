"""Numerical-trust reference kernels.

These routines are deliberately small and transparent. They are not intended to
replace optimized BLAS libraries. Their purpose is to provide independent,
high-trust reference paths for bounded validation problems.

The CRT matrix multiply is Ozaki-Scheme-II-inspired: it demonstrates exact
integer modular products plus CRT reconstruction for micro-oracles. It is not a
performance implementation of the full published Ozaki Scheme II.

The floating-point path uses Dekker-style TwoProduct error-free transformation
(EFT) plus :func:`math.fsum`. This is a lightweight reference lane, not a claim
to implement NearSum, ExBLAS, or OzBLAS.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from typing import Sequence

import numpy as np

_SPLITTER = 134217729.0  # 2**27 + 1 for IEEE binary64.
_DEFAULT_CRT_MODULI = (127, 125, 121)
_DEFAULT_CRT_CHECK_MODULUS = 113


def two_product(a: float, b: float) -> tuple[float, float]:
    """Return ``p, e`` such that ``a*b == p+e`` inside a fail-closed domain.

    The reference implementation uses Dekker splitting.  Rather than silently
    returning an invalid error term when the rounded product is subnormal,
    underflows/overflows, or the splitter multiplication overflows, it rejects
    that case.  A stronger MPFR/FMA/native backend may then adjudicate it.

    This conservative contract intentionally rejects some cases whose product
    might happen to be exactly representable as a subnormal.  Verification is
    allowed to escalate; it is not allowed to guess outside its proven lane.
    """
    a = float(a)
    b = float(b)
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError("EFT requires finite binary64 operands")

    # Zero products are exact and need no split.  Handle them before the
    # normal-product guard so literal zeros remain cheap and supported.
    if a == 0.0 or b == 0.0:
        return a * b, 0.0

    p = a * b
    if not math.isfinite(p):
        raise ValueError("EFT product overflow: escalate to a stronger backend")
    if p == 0.0 or abs(p) < sys.float_info.min:
        raise ValueError(
            "EFT product is subnormal/underflowed: escalate to a stronger backend"
        )

    ca = _SPLITTER * a
    cb = _SPLITTER * b
    if not (math.isfinite(ca) and math.isfinite(cb)):
        raise ValueError("EFT splitter overflow: escalate to a stronger backend")

    a_big = ca - a
    a_hi = ca - a_big
    a_lo = a - a_hi

    b_big = cb - b
    b_hi = cb - b_big
    b_lo = b - b_hi

    err = ((a_hi * b_hi - p) + a_hi * b_lo + a_lo * b_hi) + a_lo * b_lo
    if not math.isfinite(err):
        raise ValueError("EFT error term became non-finite")
    return p, err


def eft_dot(x: Sequence[float], y: Sequence[float]) -> float:
    """Dot product retaining the product-rounding error before final reduction."""
    if len(x) != len(y):
        raise ValueError("dot operands must have equal length")
    terms: list[float] = []
    for a, b in zip(x, y, strict=True):
        p, e = two_product(float(a), float(b))
        terms.extend((p, e))
    return math.fsum(terms)


def exact_dot_fraction(x: Sequence[float], y: Sequence[float]) -> Fraction:
    """Exact rational dot product of the binary64 values supplied."""
    if len(x) != len(y):
        raise ValueError("dot operands must have equal length")
    total = Fraction(0, 1)
    for a, b in zip(x, y, strict=True):
        total += Fraction.from_float(float(a)) * Fraction.from_float(float(b))
    return total


def eft_complex_sum_products(
    a: Sequence[complex],
    b: Sequence[complex],
    *,
    conjugate_a: bool = False,
) -> complex:
    """Accurately reduce sum(a_i*b_i), optionally conjugating a."""
    if len(a) != len(b):
        raise ValueError("dot operands must have equal length")

    real_terms: list[float] = []
    imag_terms: list[float] = []
    for aa, bb in zip(a, b, strict=True):
        ar = float(np.real(aa))
        ai = float(np.imag(aa))
        if conjugate_a:
            ai = -ai
        br = float(np.real(bb))
        bi = float(np.imag(bb))

        p, e = two_product(ar, br)
        real_terms.extend((p, e))
        p, e = two_product(ai, bi)
        real_terms.extend((-p, -e))

        p, e = two_product(ar, bi)
        imag_terms.extend((p, e))
        p, e = two_product(ai, br)
        imag_terms.extend((p, e))

    return complex(math.fsum(real_terms), math.fsum(imag_terms))


def exact_complex_sum_products_fraction(
    a: Sequence[complex],
    b: Sequence[complex],
    *,
    conjugate_a: bool = False,
) -> tuple[Fraction, Fraction]:
    """Exact real/imaginary rational parts for the supplied binary64 values."""
    if len(a) != len(b):
        raise ValueError("dot operands must have equal length")

    real = Fraction(0, 1)
    imag = Fraction(0, 1)
    for aa, bb in zip(a, b, strict=True):
        ar = Fraction.from_float(float(np.real(aa)))
        ai = Fraction.from_float(float(np.imag(aa)))
        if conjugate_a:
            ai = -ai
        br = Fraction.from_float(float(np.real(bb)))
        bi = Fraction.from_float(float(np.imag(bb)))
        real += ar * br - ai * bi
        imag += ar * bi + ai * br
    return real, imag


def eft_complex_matvec(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """Reference complex matrix-vector multiply using EFT row reductions."""
    matrix = np.asarray(matrix, dtype=complex)
    vector = np.asarray(vector, dtype=complex)
    if matrix.ndim != 2 or vector.ndim != 1 or matrix.shape[1] != vector.shape[0]:
        raise ValueError("incompatible matrix/vector shapes")
    return np.asarray(
        [eft_complex_sum_products(row, vector) for row in matrix],
        dtype=complex,
    )


def eft_eigen_residual(
    matrix: np.ndarray,
    eigenvalue: float,
    eigenvector: np.ndarray,
) -> np.ndarray:
    """Evaluate H psi - E psi with EFT accumulation per component."""
    matrix = np.asarray(matrix, dtype=complex)
    vector = np.asarray(eigenvector, dtype=complex)
    if matrix.shape != (vector.size, vector.size):
        raise ValueError("matrix/eigenvector shape mismatch")

    residual = np.empty(vector.size, dtype=complex)
    for row_index, row in enumerate(matrix):
        terms_a = list(row) + [complex(-float(eigenvalue), 0.0)]
        terms_b = list(vector) + [vector[row_index]]
        residual[row_index] = eft_complex_sum_products(terms_a, terms_b)
    return residual


def eft_norm(vector: Sequence[complex]) -> float:
    """Euclidean norm with EFT products and accurate final reduction."""
    terms: list[float] = []
    for value in vector:
        real = float(np.real(value))
        imag = float(np.imag(value))
        p, e = two_product(real, real)
        terms.extend((p, e))
        p, e = two_product(imag, imag)
        terms.extend((p, e))
    return math.sqrt(math.fsum(terms))


def _crt_reconstruct_scalar(residues: Sequence[int], moduli: Sequence[int]) -> int:
    product = math.prod(moduli)
    value = 0
    for residue, modulus in zip(residues, moduli, strict=True):
        partial = product // modulus
        inverse = pow(partial, -1, modulus)
        value = (value + int(residue) * partial * inverse) % product
    if value > product // 2:
        value -= product
    return value


def _modular_matmul(a: np.ndarray, b: np.ndarray, modulus: int) -> np.ndarray:
    rows, inner = a.shape
    _, cols = b.shape
    out = np.empty((rows, cols), dtype=object)
    for i in range(rows):
        for j in range(cols):
            total = 0
            for k in range(inner):
                total = (
                    total
                    + (int(a[i, k]) % modulus) * (int(b[k, j]) % modulus)
                ) % modulus
            out[i, j] = total
    return out


def crt_exact_matmul(
    a: np.ndarray,
    b: np.ndarray,
    *,
    moduli: Sequence[int] = _DEFAULT_CRT_MODULI,
) -> tuple[np.ndarray, dict[str, int]]:
    """Exactly multiply bounded integer matrices through modular products + CRT.

    The signed reconstruction is unambiguous only if the conservative absolute
    product bound is strictly below half the CRT dynamic range. The routine
    fails closed when that condition is not satisfied.
    """
    a = np.asarray(a, dtype=object)
    b = np.asarray(b, dtype=object)
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError("incompatible matrix shapes")

    inner = a.shape[1]
    max_a = max((abs(int(value)) for value in a.flat), default=0)
    max_b = max((abs(int(value)) for value in b.flat), default=0)
    absolute_bound = inner * max_a * max_b
    dynamic_range = math.prod(moduli)
    if 2 * absolute_bound >= dynamic_range:
        raise ValueError(
            "CRT capacity exceeded: "
            f"2*bound={2 * absolute_bound} >= range={dynamic_range}"
        )

    residue_matrices = [_modular_matmul(a, b, modulus) for modulus in moduli]
    out = np.empty((a.shape[0], b.shape[1]), dtype=object)
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            out[i, j] = _crt_reconstruct_scalar(
                [int(matrix[i, j]) for matrix in residue_matrices],
                moduli,
            )

    return out, {
        "absolute_product_bound": int(absolute_bound),
        "crt_dynamic_range": int(dynamic_range),
    }


def verify_matmul_modulus(
    a: np.ndarray,
    b: np.ndarray,
    candidate: np.ndarray,
    *,
    check_modulus: int = _DEFAULT_CRT_CHECK_MODULUS,
) -> bool:
    """Cross-check a reconstructed integer product with an unused modulus."""
    expected = _modular_matmul(
        np.asarray(a, dtype=object),
        np.asarray(b, dtype=object),
        check_modulus,
    )
    observed = np.asarray(candidate, dtype=object)
    if observed.shape != expected.shape:
        return False
    return all(
        int(observed[index]) % check_modulus == int(expected[index])
        for index in np.ndindex(expected.shape)
    )
