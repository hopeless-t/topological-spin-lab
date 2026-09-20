from __future__ import annotations

import json
from pathlib import Path

import pytest

from topological_spin_lab.errors import SpecValidationError
from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.spec_exp003 import Exp003Spec, parse_exp003_spec

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "EXP-003.json"


def canonical_raw() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_canonical_exp003_spec_loads() -> None:
    spec = load_any_experiment_spec(SPEC_PATH)
    assert isinstance(spec, Exp003Spec)
    assert spec.model.orientation == "negative_to_positive"
    assert spec.sampling.profile.points == 241


def test_zero_mass_is_invalid() -> None:
    raw = canonical_raw()
    raw["model"]["mass_magnitude_eV"] = 0.0
    with pytest.raises(SpecValidationError, match="positive"):
        parse_exp003_spec(raw)


def test_nonpositive_wall_width_is_invalid() -> None:
    raw = canonical_raw()
    raw["model"]["wall_width_A"] = 0.0
    with pytest.raises(SpecValidationError, match="positive"):
        parse_exp003_spec(raw)


def test_even_profile_grid_is_invalid() -> None:
    raw = canonical_raw()
    raw["sampling"]["profile"]["points"] = 240
    with pytest.raises(SpecValidationError, match="odd integer"):
        parse_exp003_spec(raw)


def test_dispersion_grid_must_include_zero() -> None:
    raw = canonical_raw()
    raw["sampling"]["dispersion"]["ky_min_Ainv"] = 0.01
    raw["sampling"]["dispersion"]["ky_max_Ainv"] = 0.11
    with pytest.raises(SpecValidationError, match="include ky = 0"):
        parse_exp003_spec(raw)


def test_both_wall_orientations_are_valid() -> None:
    raw = canonical_raw()
    raw["model"]["orientation"] = "positive_to_negative"
    spec = parse_exp003_spec(raw)
    assert spec.model.orientation == "positive_to_negative"
