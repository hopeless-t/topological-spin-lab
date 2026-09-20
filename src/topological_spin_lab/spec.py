from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from .errors import SpecValidationError


@dataclass(frozen=True, slots=True)
class ModelSpec:
    name: str
    surface_normal: str
    alpha_eV_A: float


@dataclass(frozen=True, slots=True)
class SpectrumSamplingSpec:
    axis: str
    fixed_ky_Ainv: float
    min_Ainv: float
    max_Ainv: float
    points: int


@dataclass(frozen=True, slots=True)
class SpinRingSamplingSpec:
    radius_Ainv: float
    angles: int


@dataclass(frozen=True, slots=True)
class SamplingSpec:
    spectrum: SpectrumSamplingSpec
    spin_ring: SpinRingSamplingSpec


@dataclass(frozen=True, slots=True)
class AcceptanceSpec:
    hermiticity_abs_eV: float
    analytic_spectrum_abs_eV: float
    dirac_point_abs_eV: float
    particle_hole_abs_eV: float
    spin_norm_abs: float
    spin_momentum_dot_abs: float
    spin_z_abs: float
    helicity_abs: float
    time_reversal_abs_eV: float


@dataclass(frozen=True, slots=True)
class Exp001Spec:
    schema_version: str
    experiment_id: str
    title: str
    model: ModelSpec
    sampling: SamplingSpec
    acceptance: AcceptanceSpec


def _mapping(value: Any, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SpecValidationError(f"{context} must be an object.")
    return value


def _exact_keys(mapping: Mapping[str, Any], expected: set[str], context: str) -> None:
    actual = set(mapping)
    unknown = sorted(actual - expected)
    missing = sorted(expected - actual)
    if unknown:
        raise SpecValidationError(f"{context} has unknown field(s): {', '.join(unknown)}")
    if missing:
        raise SpecValidationError(f"{context} is missing field(s): {', '.join(missing)}")


def _string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise SpecValidationError(f"{context} must be a non-empty string.")
    return value


def _finite_number(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SpecValidationError(f"{context} must be a number.")
    result = float(value)
    if not math.isfinite(result):
        raise SpecValidationError(f"{context} must be finite.")
    return result


def _integer(value: Any, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SpecValidationError(f"{context} must be an integer.")
    return value


def _positive_threshold(value: Any, context: str) -> float:
    result = _finite_number(value, context)
    if result <= 0.0:
        raise SpecValidationError(f"{context} must be positive.")
    return result


def parse_experiment_spec(raw: Mapping[str, Any]) -> Exp001Spec:
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
    if experiment_id != "EXP-001":
        raise SpecValidationError("Only experiment_id 'EXP-001' is supported.")

    model_raw = _mapping(top["model"], "model")
    _exact_keys(model_raw, {"name", "surface_normal", "alpha_eV_A"}, "model")
    name = _string(model_raw["name"], "model.name")
    surface_normal = _string(model_raw["surface_normal"], "model.surface_normal")
    alpha = _finite_number(model_raw["alpha_eV_A"], "model.alpha_eV_A")
    if name != "surface_dirac":
        raise SpecValidationError("model.name must be 'surface_dirac'.")
    if surface_normal != "+z":
        raise SpecValidationError("model.surface_normal must be '+z'.")
    if alpha <= 0.0:
        raise SpecValidationError("model.alpha_eV_A must be positive.")

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
        raise SpecValidationError("EXP-001 requires sampling.spectrum.fixed_ky_Ainv = 0.")
    if minimum >= maximum:
        raise SpecValidationError("sampling.spectrum.min_Ainv must be < max_Ainv.")
    if points < 3:
        raise SpecValidationError("sampling.spectrum.points must be >= 3.")

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
        "dirac_point_abs_eV",
        "particle_hole_abs_eV",
        "spin_norm_abs",
        "spin_momentum_dot_abs",
        "spin_z_abs",
        "helicity_abs",
        "time_reversal_abs_eV",
    }
    _exact_keys(acceptance_raw, acceptance_keys, "acceptance")
    acceptance = AcceptanceSpec(
        **{
            key: _positive_threshold(acceptance_raw[key], f"acceptance.{key}")
            for key in sorted(acceptance_keys)
        }
    )

    return Exp001Spec(
        schema_version=schema_version,
        experiment_id=experiment_id,
        title=title,
        model=ModelSpec(name=name, surface_normal=surface_normal, alpha_eV_A=alpha),
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


def load_experiment_spec(path: Path) -> Exp001Spec:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecValidationError(f"Could not load JSON spec: {exc}") from exc
    return parse_experiment_spec(_mapping(raw, "spec"))


def canonical_spec_json(spec: Exp001Spec) -> str:
    return json.dumps(asdict(spec), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def spec_sha256(spec: Exp001Spec) -> str:
    return hashlib.sha256(canonical_spec_json(spec).encode("utf-8")).hexdigest()
