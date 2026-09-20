from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import SpecValidationError
from .evidence import write_evidence, write_exp003_evidence
from .experiment_loader import load_any_experiment_spec
from .experiments.exp001 import execute_exp001
from .experiments.exp002 import execute_exp002
from .experiments.exp003 import execute_exp003
from .plotting import write_exp002_figures, write_exp003_figures, write_figures
from .provenance import collect_provenance
from .results import ExperimentStatus
from .spec import Exp001Spec
from .spec_exp002 import Exp002Spec
from .spec_exp003 import Exp003Spec
from .spec_val001 import load_val001_spec
from .validation.evidence import write_val001_evidence
from .validation.val001 import execute_val001


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="topological_spin_lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run an experiment spec.")
    run.add_argument("spec", type=Path)
    run.add_argument("--out", type=Path, required=True)

    validate = subparsers.add_parser("validate", help="Run a validation spec.")
    validate.add_argument("spec", type=Path)
    validate.add_argument("--out", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "validate":
        try:
            spec = load_val001_spec(args.spec)
        except SpecValidationError as exc:
            print(f"INVALID: {exc}", file=sys.stderr)
            return 2

        try:
            provenance = collect_provenance(Path.cwd())
            result = execute_val001(spec)
            write_val001_evidence(spec, result, provenance, args.out)
        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 3

        print(f"{result.status.value}: {spec.validation_id}")
        for gate in result.gates:
            state = "PASS" if gate.passed else "FAIL"
            print(f"  {state} {gate.name}: {gate.observed}")
        print(f"  spectral_validator={result.spectral_validator}")
        print(f"  transport_candidate={result.transport_candidate}")
        print(f"  transport_authorized={result.transport_authorized}")
        return 0 if result.status is ExperimentStatus.PASS else 1

    if args.command != "run":
        return 3

    try:
        spec = load_any_experiment_spec(args.spec)
    except SpecValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2

    try:
        provenance = collect_provenance(Path.cwd())

        if isinstance(spec, Exp001Spec):
            result = execute_exp001(spec)
            write_evidence(spec, result, provenance, args.out)
            write_figures(result, args.out / "figures")
        elif isinstance(spec, Exp002Spec):
            result = execute_exp002(spec)
            write_evidence(spec, result, provenance, args.out)
            write_exp002_figures(result, args.out / "figures")
        elif isinstance(spec, Exp003Spec):
            result = execute_exp003(spec)
            write_exp003_evidence(spec, result, provenance, args.out)
            write_exp003_figures(result, args.out / "figures")
        else:
            raise TypeError(f"Unsupported spec type: {type(spec).__name__}")
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    print(f"{result.status.value}: {spec.experiment_id}")
    for check in result.checks:
        state = "PASS" if check.passed else "FAIL"
        print(
            f"  {state} {check.name}: "
            f"observed={check.observed:.6g} limit={check.limit:.6g} {check.unit}"
        )

    return 0 if result.status is ExperimentStatus.PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
