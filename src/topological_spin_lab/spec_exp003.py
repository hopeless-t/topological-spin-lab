from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

from .errors import SpecValidationError
from .spec import _exact_keys, _finite_number, _integer, _mapping, _positive_threshold, _string


@dataclass(frozen=True, slots=True)
class Exp003ModelSpec:
    name: str
    surface_normal: str
    alpha_eV_A: float
    mass_magnitude_eV: float
    wall_width_A: float
    orientation: str


@dataclass(frozen=True, slots=True)
class ProfileSamplingSpec:
    half_window_xi: float
    points: int


@dataclass(frozen=True, slots=True)
class DispersionSamplingSpec:
    ky_min_Ainv: float
    ky_max_Ainv: float
    points: int


@dataclass(frozen=True, slots=True)
class Exp003SamplingSpec:
    profile: ProfileSamplingSpec
    dispersion: DispersionSamplingSpec


@dataclass(frozen=True, slots=True)
class Exp003AcceptanceSpec:
    operator_residual_eV: float
    finite_window_norm_abs: float
    density_symmetry_abs_Ainv: float
    center_peak_abs_A: float
    mass_center_abs_eV: float
    dispersion_abs_eV: float
    in_gap_excess_eV: float
    spin_vector_abs: float
    reversal_dispersion_abs_eV: float
    reversal_spin_abs: float


@dataclass(frozen=True, slots=True)
class Exp003Spec:
    schema_version: str
    experiment_id: str
    title: str
    model: Exp003ModelSpec
    sampling: Exp003SamplingSpec
    acceptance: Exp003AcceptanceSpec


def parse_exp003_spec(raw: Mapping[str, Any]) -> Exp003Spec:
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
    if experiment_id != "EXP-003":
        raise SpecValidationError("experiment_id must be 'EXP-003'.")

    model_raw = _mapping(top["model"], "model")
    _exact_keys(
        model_raw,
        {
            "name",
            "surface_normal",
            "alpha_eV_A",
            "mass_magnitude_eV",
            "wall_width_A",
            "orientation",
        },
        "model",
    )
    name = _string(model_raw["name"], "model.name")
    surface_normal = _string(model_raw["surface_normal"], "model.surface_normal")
    alpha = _finite_number(model_raw["alpha_eV_A"], "model.alpha_eV_A")
    mass = _finite_number(model_raw["mass_magnitude_eV"], "model.mass_magnitude_eV")
    width = _finite_number(model_raw["wall_width_A"], "model.wall_width_A")
    orientation = _string(model_raw["orientation"], "model.orientation")

    if name != "continuum_mass_domain_wall":
        raise SpecValidationError("model.name must be 'continuum_mass_domain_wall'.")
    if surface_normal != "+z":
        raise SpecValidationError("model.surface_normal must be '+z'.")
    if alpha <= 0.0:
        raise SpecValidationError("model.alpha_eV_A must be positive.")
    if mass <= 0.0:
        raise SpecValidationError("model.mass_magnitude_eV must be positive.")
    if width <= 0.0:
        raise SpecValidationError("model.wall_width_A must be positive.")
    if orientation not in {"negative_to_positive", "positive_to_negative"}:
        raise SpecValidationError(
            "model.orientation must be 'negative_to_positive' or 'positive_to_negative'."
        )

    sampling_raw = _mapping(top["sampling"], "sampling")
    _exact_keys(sampling_raw, {"profile", "dispersion"}, "sampling")

    profile_raw = _mapping(sampling_raw["profile"], "sampling.profile")
    _exact_keys(profile_raw, {"half_window_xi", "points"}, "sampling.profile")
    half_window = _finite_number(
        profile_raw["half_window_xi"], "sampling.profile.half_window_xi"
    )
    profile_points = _integer(profile_raw["points"], "sampling.profile.points")
    if half_window <= 0.0:
        raise SpecValidationError("sampling.profile.half_window_xi must be positive.")
    if profile_points < 5 or profile_points % 2 == 0:
        raise SpecValidationError(
            "sampling.profile.points must be an odd integer >= 5 so x=0 is sampled."
        )

    dispersion_raw = _mapping(sampling_raw["dispersion"], "sampling.dispersion")
    _exact_keys(
        dispersion_raw,
        {"ky_min_Ainv", "ky_max_Ainv", "points"},
        "sampling.dispersion",
    )
    ky_min = _finite_number(
        dispersion_raw["ky_min_Ainv"], "sampling.dispersion.ky_min_Ainv"
    )
    ky_max = _finite_number(
        dispersion_raw["ky_max_Ainv"], "sampling.dispersion.ky_max_Ainv"
    )
    dispersion_points = _integer(
        dispersion_raw["points"], "sampling.dispersion.points"
    )
    if ky_min >= ky_max:
        raise SpecValidationError("sampling.dispersion.ky_min_Ainv must be < ky_max_Ainv.")
    if not (ky_min <= 0.0 <= ky_max):
        raise SpecValidationError("sampling.dispersion range must include ky = 0.")
    if dispersion_points < 3:
        raise SpecValidationError("sampling.dispersion.points must be >= 3.")
    zero_index = (-ky_min) * (dispersion_points - 1) / (ky_max - ky_min)
    if not math.isclose(zero_index, round(zero_index), rel_tol=0.0, abs_tol=1e-12):
        raise SpecValidationError("sampling.dispersion grid must include ky = 0.")

    acceptance_raw = _mapping(top["acceptance"], "acceptance")
    acceptance_keys = {
        "operator_residual_eV",
        "finite_window_norm_abs",
        "density_symmetry_abs_Ainv",
        "center_peak_abs_A",
        "mass_center_abs_eV",
        "dispersion_abs_eV",
        "in_gap_excess_eV",
        "spin_vector_abs",
        "reversal_dispersion_abs_eV",
        "reversal_spin_abs",
    }
    _exact_keys(acceptance_raw, acceptance_keys, "acceptance")
    acceptance = Exp003AcceptanceSpec(
        **{
            key: _positive_threshold(acceptance_raw[key], f"acceptance.{key}")
            for key in sorted(acceptance_keys)
        }
    )

    return Exp003Spec(
        schema_version=schema_version,
        experiment_id=experiment_id,
        title=title,
        model=Exp003ModelSpec(
            name=name,
            surface_normal=surface_normal,
            alpha_eV_A=alpha,
            mass_magnitude_eV=mass,
            wall_width_A=width,
            orientation=orientation,
        ),
        sampling=Exp003SamplingSpec(
            profile=ProfileSamplingSpec(
                half_window_xi=half_window,
                points=profile_points,
            ),
            dispersion=DispersionSamplingSpec(
                ky_min_Ainv=ky_min,
                ky_max_Ainv=ky_max,
                points=dispersion_points,
            ),
        ),
        acceptance=acceptance,
    )
