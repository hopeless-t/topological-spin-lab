from __future__ import annotations

import json
from pathlib import Path

import pytest

from topological_spin_lab.errors import SpecValidationError
from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.spec_exp002 import Exp002Spec, parse_exp002_spec

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "EXP-002.json"


def canonical_raw() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_canonical_exp002_spec_loads() -> None:
    spec = load_any_experiment_spec(SPEC_PATH)
    assert isinstance(spec, Exp002Spec)
    assert spec.experiment_id == "EXP-002"
    assert spec.model.mass_eV == 0.02


def test_zero_mass_is_invalid_for_exp002() -> None:
    raw = canonical_raw()
    raw["model"]["mass_eV"] = 0.0
    with pytest.raises(SpecValidationError, match="nonzero"):
        parse_exp002_spec(raw)


def test_negative_mass_is_valid() -> None:
    raw = canonical_raw()
    raw["model"]["mass_eV"] = -0.02
    spec = parse_exp002_spec(raw)
    assert spec.model.mass_eV == -0.02


def test_unknown_exp002_model_field_is_invalid() -> None:
    raw = canonical_raw()
    raw["model"]["exchange_eV"] = 0.02
    with pytest.raises(SpecValidationError, match="unknown field"):
        parse_exp002_spec(raw)


def test_unsupported_experiment_id_is_invalid(tmp_path: Path) -> None:
    raw = canonical_raw()
    raw["experiment_id"] = "EXP-999"
    path = tmp_path / "unknown.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(SpecValidationError, match="Unsupported experiment_id"):
        load_any_experiment_spec(path)
