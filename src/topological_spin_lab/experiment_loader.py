from __future__ import annotations

import json
from pathlib import Path
from typing import TypeAlias

from .errors import SpecValidationError
from .spec import Exp001Spec, parse_experiment_spec
from .spec_exp002 import Exp002Spec, parse_exp002_spec

ExperimentSpec: TypeAlias = Exp001Spec | Exp002Spec


def load_any_experiment_spec(path: Path) -> ExperimentSpec:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecValidationError(f"Could not load JSON spec: {exc}") from exc

    if not isinstance(raw, dict):
        raise SpecValidationError("spec must be an object.")

    experiment_id = raw.get("experiment_id")
    if experiment_id == "EXP-001":
        return parse_experiment_spec(raw)
    if experiment_id == "EXP-002":
        return parse_exp002_spec(raw)

    if not isinstance(experiment_id, str) or not experiment_id:
        raise SpecValidationError("experiment_id must be a non-empty string.")
    raise SpecValidationError(f"Unsupported experiment_id: {experiment_id}")
