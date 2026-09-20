from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .errors import SpecValidationError
from .spec import _exact_keys, _finite_number, _integer, _mapping, _positive_threshold, _string


@dataclass(frozen=True, slots=True)
class Val001ReferenceSpec:
    alpha_eV_A: float
    mass_magnitude_eV: float
    wall_width_A: float
    half_window_xi: float


@dataclass(frozen=True, slots=True)
class Val001SamplingSpec:
    grid_points: tuple[int, ...]
    ky_Ainv: tuple[float, ...]
    orientations: tuple[str, ...]
    wilson_r: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class Val001ClassificationSpec:
    wall_half_width_xi: float
    edge_start_xi: float
    zero_subspace_eV: float
    in_gap_margin_eV: float
    wall_localization_min: float
    edge_localization_min: float


@dataclass(frozen=True, slots=True)
class Val001AcceptanceSpec:
    matrix_hermiticity_abs_eV: float
    p_hermiticity_abs: float
    p_min_eigenvalue_min: float
    target_energy_abs_eV: float
    target_overlap_min: float
    target_wall_weight_min: float
    target_edge_weight_max: float
    spin_x_abs: float
    finest_profile_l1_max: float
    max_ghost_wall_modes: int
    max_boundary_artifacts: int
    max_other_in_gap_modes: int
    require_monotone_profile_convergence: bool


@dataclass(frozen=True, slots=True)
class Val001Spec:
    schema_version: str
    validation_id: str
    title: str
    reference: Val001ReferenceSpec
    sampling: Val001SamplingSpec
    classification: Val001ClassificationSpec
    acceptance: Val001AcceptanceSpec


def _number_list(value: Any, context: str) -> tuple[float, ...]:
    if not isinstance(value, list) or not value:
        raise SpecValidationError(f"{context} must be a non-empty array.")
    return tuple(_finite_number(item, f"{context}[]") for item in value)


def _integer_list(value: Any, context: str) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise SpecValidationError(f"{context} must be a non-empty array.")
    return tuple(_integer(item, f"{context}[]") for item in value)


def _string_list(value: Any, context: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise SpecValidationError(f"{context} must be a non-empty array.")
    return tuple(_string(item, f"{context}[]") for item in value)


def _unit_interval(value: Any, context: str) -> float:
    result = _finite_number(value, context)
    if not 0.0 <= result <= 1.0:
        raise SpecValidationError(f"{context} must be between 0 and 1.")
    return result


def _nonnegative_integer(value: Any, context: str) -> int:
    result = _integer(value, context)
    if result < 0:
        raise SpecValidationError(f"{context} must be nonnegative.")
    return result


def parse_val001_spec(raw: Mapping[str, Any]) -> Val001Spec:
    top = _mapping(raw, "spec")
    _exact_keys(
        top,
        {
            "schema_version",
            "validation_id",
            "title",
            "reference",
            "sampling",
            "classification",
            "acceptance",
        },
        "spec",
    )

    schema_version = _string(top["schema_version"], "schema_version")
    validation_id = _string(top["validation_id"], "validation_id")
    title = _string(top["title"], "title")
    if schema_version != "0.1":
        raise SpecValidationError("Only schema_version '0.1' is supported.")
    if validation_id != "VAL-001":
        raise SpecValidationError("validation_id must be 'VAL-001'.")

    reference_raw = _mapping(top["reference"], "reference")
    _exact_keys(
        reference_raw,
        {"alpha_eV_A", "mass_magnitude_eV", "wall_width_A", "half_window_xi"},
        "reference",
    )
    alpha = _finite_number(reference_raw["alpha_eV_A"], "reference.alpha_eV_A")
    mass = _finite_number(
        reference_raw["mass_magnitude_eV"], "reference.mass_magnitude_eV"
    )
    width = _finite_number(reference_raw["wall_width_A"], "reference.wall_width_A")
    half_window = _finite_number(
        reference_raw["half_window_xi"], "reference.half_window_xi"
    )
    if min(alpha, mass, width, half_window) <= 0.0:
        raise SpecValidationError("reference values must be positive.")

    sampling_raw = _mapping(top["sampling"], "sampling")
    _exact_keys(
        sampling_raw,
        {"grid_points", "ky_Ainv", "orientations", "wilson_r"},
        "sampling",
    )
    grid_points = _integer_list(sampling_raw["grid_points"], "sampling.grid_points")
    ky_values = _number_list(sampling_raw["ky_Ainv"], "sampling.ky_Ainv")
    orientations = _string_list(sampling_raw["orientations"], "sampling.orientations")
    wilson_r = _number_list(sampling_raw["wilson_r"], "sampling.wilson_r")

    if tuple(sorted(set(grid_points))) != grid_points:
        raise SpecValidationError("sampling.grid_points must be unique and increasing.")
    if any(points < 5 or points % 2 == 0 for points in grid_points):
        raise SpecValidationError("sampling.grid_points must contain odd integers >= 5.")
    if 0.0 not in ky_values:
        raise SpecValidationError("sampling.ky_Ainv must include 0.")
    if tuple(sorted(ky_values)) != ky_values:
        raise SpecValidationError("sampling.ky_Ainv must be increasing.")
    if orientations != ("negative_to_positive", "positive_to_negative"):
        raise SpecValidationError(
            "sampling.orientations must contain both frozen wall orientations in order."
        )
    if any(value <= 0.0 for value in wilson_r):
        raise SpecValidationError("sampling.wilson_r values must be positive.")
    if len(set(wilson_r)) != len(wilson_r):
        raise SpecValidationError("sampling.wilson_r values must be unique.")

    classification_raw = _mapping(top["classification"], "classification")
    _exact_keys(
        classification_raw,
        {
            "wall_half_width_xi",
            "edge_start_xi",
            "zero_subspace_eV",
            "in_gap_margin_eV",
            "wall_localization_min",
            "edge_localization_min",
        },
        "classification",
    )
    wall_half = _positive_threshold(
        classification_raw["wall_half_width_xi"],
        "classification.wall_half_width_xi",
    )
    edge_start = _positive_threshold(
        classification_raw["edge_start_xi"], "classification.edge_start_xi"
    )
    zero_subspace = _positive_threshold(
        classification_raw["zero_subspace_eV"], "classification.zero_subspace_eV"
    )
    in_gap_margin = _positive_threshold(
        classification_raw["in_gap_margin_eV"], "classification.in_gap_margin_eV"
    )
    wall_min = _unit_interval(
        classification_raw["wall_localization_min"],
        "classification.wall_localization_min",
    )
    edge_min = _unit_interval(
        classification_raw["edge_localization_min"],
        "classification.edge_localization_min",
    )
    if not wall_half < edge_start < half_window:
        raise SpecValidationError(
            "classification requires wall_half_width_xi < edge_start_xi < half_window_xi."
        )

    acceptance_raw = _mapping(top["acceptance"], "acceptance")
    expected_acceptance = {
        "matrix_hermiticity_abs_eV",
        "p_hermiticity_abs",
        "p_min_eigenvalue_min",
        "target_energy_abs_eV",
        "target_overlap_min",
        "target_wall_weight_min",
        "target_edge_weight_max",
        "spin_x_abs",
        "finest_profile_l1_max",
        "max_ghost_wall_modes",
        "max_boundary_artifacts",
        "max_other_in_gap_modes",
        "require_monotone_profile_convergence",
    }
    _exact_keys(acceptance_raw, expected_acceptance, "acceptance")

    require_monotone = acceptance_raw["require_monotone_profile_convergence"]
    if not isinstance(require_monotone, bool):
        raise SpecValidationError(
            "acceptance.require_monotone_profile_convergence must be boolean."
        )

    overlap_min = _unit_interval(
        acceptance_raw["target_overlap_min"], "acceptance.target_overlap_min"
    )
    target_wall_min = _unit_interval(
        acceptance_raw["target_wall_weight_min"],
        "acceptance.target_wall_weight_min",
    )
    target_edge_max = _unit_interval(
        acceptance_raw["target_edge_weight_max"],
        "acceptance.target_edge_weight_max",
    )
    profile_l1 = _finite_number(
        acceptance_raw["finest_profile_l1_max"],
        "acceptance.finest_profile_l1_max",
    )
    if not 0.0 < profile_l1 <= 2.0:
        raise SpecValidationError(
            "acceptance.finest_profile_l1_max must be in (0, 2]."
        )

    return Val001Spec(
        schema_version=schema_version,
        validation_id=validation_id,
        title=title,
        reference=Val001ReferenceSpec(
            alpha_eV_A=alpha,
            mass_magnitude_eV=mass,
            wall_width_A=width,
            half_window_xi=half_window,
        ),
        sampling=Val001SamplingSpec(
            grid_points=grid_points,
            ky_Ainv=ky_values,
            orientations=orientations,
            wilson_r=wilson_r,
        ),
        classification=Val001ClassificationSpec(
            wall_half_width_xi=wall_half,
            edge_start_xi=edge_start,
            zero_subspace_eV=zero_subspace,
            in_gap_margin_eV=in_gap_margin,
            wall_localization_min=wall_min,
            edge_localization_min=edge_min,
        ),
        acceptance=Val001AcceptanceSpec(
            matrix_hermiticity_abs_eV=_positive_threshold(
                acceptance_raw["matrix_hermiticity_abs_eV"],
                "acceptance.matrix_hermiticity_abs_eV",
            ),
            p_hermiticity_abs=_positive_threshold(
                acceptance_raw["p_hermiticity_abs"],
                "acceptance.p_hermiticity_abs",
            ),
            p_min_eigenvalue_min=_positive_threshold(
                acceptance_raw["p_min_eigenvalue_min"],
                "acceptance.p_min_eigenvalue_min",
            ),
            target_energy_abs_eV=_positive_threshold(
                acceptance_raw["target_energy_abs_eV"],
                "acceptance.target_energy_abs_eV",
            ),
            target_overlap_min=overlap_min,
            target_wall_weight_min=target_wall_min,
            target_edge_weight_max=target_edge_max,
            spin_x_abs=_positive_threshold(
                acceptance_raw["spin_x_abs"], "acceptance.spin_x_abs"
            ),
            finest_profile_l1_max=profile_l1,
            max_ghost_wall_modes=_nonnegative_integer(
                acceptance_raw["max_ghost_wall_modes"],
                "acceptance.max_ghost_wall_modes",
            ),
            max_boundary_artifacts=_nonnegative_integer(
                acceptance_raw["max_boundary_artifacts"],
                "acceptance.max_boundary_artifacts",
            ),
            max_other_in_gap_modes=_nonnegative_integer(
                acceptance_raw["max_other_in_gap_modes"],
                "acceptance.max_other_in_gap_modes",
            ),
            require_monotone_profile_convergence=require_monotone,
        ),
    )


def load_val001_spec(path: Path) -> Val001Spec:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecValidationError(f"Could not load JSON spec: {exc}") from exc
    return parse_val001_spec(_mapping(raw, "spec"))
