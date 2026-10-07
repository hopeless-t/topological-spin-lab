"""Independent numerical-trust reference helpers."""

from .numerical_trust import (
    crt_exact_matmul,
    eft_complex_matvec,
    eft_complex_sum_products,
    eft_dot,
    eft_eigen_residual,
    eft_norm,
    exact_complex_sum_products_fraction,
    exact_dot_fraction,
    two_product,
    verify_matmul_modulus,
)

__all__ = [
    "crt_exact_matmul",
    "eft_complex_matvec",
    "eft_complex_sum_products",
    "eft_dot",
    "eft_eigen_residual",
    "eft_norm",
    "exact_complex_sum_products_fraction",
    "exact_dot_fraction",
    "two_product",
    "verify_matmul_modulus",
]
