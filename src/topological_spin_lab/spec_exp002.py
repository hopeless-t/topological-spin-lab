from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

from .errors import SpecValidationError
from .spec import (
    SamplingSpec,
    SpectrumSamplingSpec,
    SpinRingSamplingSpec,
    _exact_keys,
    _finite_number,
    _integer,
    _mapping,
    _positive_threshold,
    _string,
)


@dataclass(frozen=True, slots=True)
class Exp002ModelSpec:
    name: str
    surface_normal: str
    alpha_eV_A: float
    mass_eV: float


@dataclass(frozen=True, slots=True)
class Exp002AcceptanceSpec:
    hermiticity_abs_eV: float
    analytic_spectrum_abs_eV: float
    direct_gap_abs_eV: float
    spectral_pairing_abs_eV: float
    spin_norm_abs: float
    spin_momentum_dot_abs: float
    spin_vector_abs: float
    helicity_abs: float
    center_spin_abs: float
    tr_breaking_magnitude_abs_eV: float
    tr_mass_flip_abs_eV: float


@dataclass(frozen=True, slots=True)
class Exp002Spec:
    schema_version: str
    experiment_id: str
    title: str
    model: Exp002ModelSpec
    sampling: SamplingSpec
    acceptance: Exp002AcceptanceSpec


def parse_exp002_spec(raw: Mapping[str, Any]) -> Exp002Spec:
    top = _mapping(raw, "spec")
    _exact_keys(
        top,
        {"schema_version", "experiment_id", "title", "model", "sampling", "acceptance"},
        "spec",
    )

    schema_version = _string(top["schema_version"], "schema_version")
    experiment_id = _string(top["experiment_id"], "experiment_id")
    title = _string(top["title"], "title")
    if schema_version != "0.1":
        raise SpecValidationError("Only schema_version '0.1' is supported.")
    if experiment_id != "EXP-002":
        raise SpecValidationError("experiment_id must be 'EXP-002'.")

    model_raw = _mapping(top["model"], "model")
    _exact_keys(
        model_raw,
        {"name", "surface_normal", "alpha_eV_A", "mass_eV"},
        "model",
    )
    name = _string(model_raw["name"], "model.name")
    surface_normal = _string(model_raw["surface_normal"], "model.surface_normal")
    alpha = _finite_number(model_raw["alpha_eV_A"], "model.alpha_eV_A")
    mass = _finite_number(model_raw["mass_eV"], "model.mass_eV")
    if name != "magnetic_surface_dirac":
        raise SpecValidationError("model.name must be 'magnetic_surface_dirac'.")
    if surface_normal != "+z":
        raise SpecValidationError("model.surface_normal must be '+z'.")
    if alpha <= 0.0:
        raise SpecValidationError("model.alpha_eV_A must be positive.")
    if mass == 0.0:
        raise SpecValidationError("EXP-002 requires nonzero model.mass_eV.")

    sampling_raw = _mapping(top["sampling"], "sampling")
    _exact_keys(sampling_raw, {"spectrum", "spin_ring"}, "sampling")

    spectrum_raw = _mapping(sampling_raw["spectrum"], "sampling.spectrum")
    _exact_keys(
        spectrum_raw,
        {"axis", "fixed_ky_Ainv", "min_Ainv", "max_Ainv", "points"},
        "sampling.spectrum",
    )
    axis = _string(spectrum_raw["axis"], "sampling.spectrum.axis")
    fixed_ky = _finite_number(
        spectrum_raw["fixed_ky_Ainv"], "sampling.spectrum.fixed_ky_Ainv"
    )
    minimum = _finite_number(spectrum_raw["min_Ainv"], "sampling.spectrum.min_Ainv")
    maximum = _finite_number(spectrum_raw["max_Ainv"], "sampling.spectrum.max_Ainv")
    points = _integer(spectrum_raw["points"], "sampling.spectrum.points")
    if axis != "kx":
        raise SpecValidationError("sampling.spectrum.axis must be 'kx'.")
    if fixed_ky != 0.0:
        raise SpecValidationError("EXP-002 requires sampling.spectrum.fixed_ky_Ainv = 0.")
    if minimum >= maximum:
        raise SpecValidationError("sampling.spectrum.min_Ainv must be < max_Ainv.")
    if points < 3:
        raise SpecValidationError("sampling.spectrum.points must be >= 3.")
    if not (minimum <= 0.0 <= maximum):
        raise SpecValidationError("sampling.spectrum range must include kx = 0.")

    zero_index = (-minimum) * (points - 1) / (maximum - minimum)
    if not math.isclose(zero_index, round(zero_index), rel_tol=0.0, abs_tol=1e-12):
        raise SpecValidationError("sampling.spectrum grid must include kx = 0.")

    ring_raw = _mapping(sampling_raw["spin_ring"], "sampling.spin_ring")
    _exact_keys(ring_raw, {"radius_Ainv", "angles"}, "sampling.spin_ring")
    radius = _finite_number(ring_raw["radius_Ainv"], "sampling.spin_ring.radius_Ainv")
    angles = _integer(ring_raw["angles"], "sampling.spin_ring.angles")
    if radius <= 0.0:
        raise SpecValidationError("sampling.spin_ring.radius_Ainv must be positive.")
    if angles < 4:
        raise SpecValidationError("sampling.spin_ring.angles must be >= 4.")

    acceptance_raw = _mapping(top["acceptance"], "acceptance")
    acceptance_keys = {
        "hermiticity_abs_eV",
        "analytic_spectrum_abs_eV",
        "direct_gap_abs_eV",
        "spectral_pairing_abs_eV",
        "spin_norm_abs",
        "spin_momentum_dot_abs",
        "spin_vector_abs",
        "helicity_abs",
        "center_spin_abs",
        "tr_breaking_magnitude_abs_eV",
        "tr_mass_flip_abs_eV",
    }
    _exact_keys(acceptance_raw, acceptance_keys, "acceptance")
    acceptance = Exp002AcceptanceSpec(
        **{
            key: _positive_threshold(acceptance_raw[key], f"acceptance.{key}")
            for key in sorted(acceptance_keys)
        }
    )

    return Exp002Spec(
        schema_version=schema_version,
        experiment_id=experiment_id,
        title=title,
        model=Exp002ModelSpec(
            name=name,
            surface_normal=surface_normal,
            alpha_eV_A=alpha,
            mass_eV=mass,
        ),
        sampling=SamplingSpec(
            spectrum=SpectrumSamplingSpec(
                axis=axis,
                fixed_ky_Ainv=fixed_ky,
                min_Ainv=minimum,
                max_Ainv=maximum,
                points=points,
            ),
            spin_ring=SpinRingSamplingSpec(radius_Ainv=radius, angles=angles),
        ),
        acceptance=acceptance,
    )
