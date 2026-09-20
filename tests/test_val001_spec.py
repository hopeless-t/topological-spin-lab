from __future__ import annotations

import json
from pathlib import Path

import pytest

from topological_spin_lab.errors import SpecValidationError
from topological_spin_lab.spec_val001 import (
    Val001Spec,
    load_val001_spec,
    parse_val001_spec,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "VAL-001.json"


def canonical_raw() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_canonical_val001_spec_loads() -> None:
    spec = load_val001_spec(SPEC_PATH)
    assert isinstance(spec, Val001Spec)
    assert spec.validation_id == "VAL-001"
    assert spec.sampling.grid_points == (61, 121, 241)
    assert spec.sampling.wilson_r == (0.5, 1.0, 1.5)


def test_even_grid_is_invalid() -> None:
    raw = canonical_raw()
    raw["sampling"]["grid_points"] = [61, 120, 241]
    with pytest.raises(SpecValidationError, match="odd integers"):
        parse_val001_spec(raw)


def test_ky_grid_must_include_zero() -> None:
    raw = canonical_raw()
    raw["sampling"]["ky_Ainv"] = [-0.04, -0.02, 0.02, 0.04]
    with pytest.raises(SpecValidationError, match="include 0"):
        parse_val001_spec(raw)


def test_wall_orientation_contract_is_exact() -> None:
    raw = canonical_raw()
    raw["sampling"]["orientations"] = ["negative_to_positive"]
    with pytest.raises(SpecValidationError, match="both frozen wall orientations"):
        parse_val001_spec(raw)


def test_unknown_field_is_invalid() -> None:
    raw = canonical_raw()
    raw["classification"]["mystery_threshold"] = 0.5
    with pytest.raises(SpecValidationError, match="unknown field"):
        parse_val001_spec(raw)
