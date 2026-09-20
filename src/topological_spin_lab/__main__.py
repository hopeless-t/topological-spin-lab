from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import SpecValidationError
from .evidence import write_evidence
from .experiments.exp001 import execute_exp001
from .plotting import write_figures
from .provenance import collect_provenance
from .results import ExperimentStatus
from .spec import load_experiment_spec


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="topological_spin_lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run an experiment spec.")
    run.add_argument("spec", type=Path)
    run.add_argument("--out", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command != "run":
        return 3

    try:
        spec = load_experiment_spec(args.spec)
    except SpecValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2

    try:
        result = execute_exp001(spec)
        provenance = collect_provenance(Path.cwd())
        write_evidence(spec, result, provenance, args.out)
        write_figures(result, args.out / "figures")
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
