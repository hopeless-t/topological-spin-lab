from __future__ import annotations

import json
from pathlib import Path

import pytest

from topological_spin_lab.errors import SpecValidationError
from topological_spin_lab.spec import load_experiment_spec, parse_experiment_spec

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "EXP-001.json"


def canonical_raw() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_canonical_spec_loads() -> None:
    spec = load_experiment_spec(SPEC_PATH)
    assert spec.experiment_id == "EXP-001"
    assert spec.model.alpha_eV_A == 1.0


def test_unknown_field_is_invalid() -> None:
    raw = canonical_raw()
    raw["model"]["alhpa_eV_A"] = raw["model"].pop("alpha_eV_A")
    with pytest.raises(SpecValidationError, match="unknown field"):
        parse_experiment_spec(raw)


def test_missing_field_is_invalid() -> None:
    raw = canonical_raw()
    del raw["model"]["alpha_eV_A"]
    with pytest.raises(SpecValidationError, match="missing field"):
        parse_experiment_spec(raw)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_alpha_is_invalid(bad: float) -> None:
    raw = canonical_raw()
    raw["model"]["alpha_eV_A"] = bad
    with pytest.raises(SpecValidationError, match="finite"):
        parse_experiment_spec(raw)


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_nonpositive_alpha_is_invalid(bad: float) -> None:
    raw = canonical_raw()
    raw["model"]["alpha_eV_A"] = bad
    with pytest.raises(SpecValidationError, match="positive"):
        parse_experiment_spec(raw)


def test_spectrum_range_must_include_zero() -> None:
    raw = canonical_raw()
    raw["sampling"]["spectrum"]["min_Ainv"] = 0.01
    raw["sampling"]["spectrum"]["max_Ainv"] = 0.11
    with pytest.raises(SpecValidationError, match="range must include kx = 0"):
        parse_experiment_spec(raw)


def test_spectrum_grid_must_include_zero() -> None:
    raw = canonical_raw()
    raw["sampling"]["spectrum"]["points"] = 200
    with pytest.raises(SpecValidationError, match="grid must include kx = 0"):
        parse_experiment_spec(raw)
