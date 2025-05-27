from __future__ import annotations

import sys
import types
import collections
import collections.abc


if 'imp' not in sys.modules:
    sys.modules['imp'] = types.ModuleType('imp')
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'MutableSet'):
    collections.MutableSet = collections.abc.MutableSet
if not hasattr(collections, 'MutableSequence'):
    collections.MutableSequence = collections.abc.MutableSequence

import argparse
import importlib
from typing import List

STEP_MODULES = {
    "convert": "scripts.step_1_convert_to_json",
    "analyze": "scripts.step_2_analyze_disclosures",
    "report": "scripts.step_3_generate_report",
}
DEFAULT_STEPS: List[str] = ["convert", "analyze", "report"]


def _run_step(name: str) -> None:
    module_path = STEP_MODULES.get(name)
    if module_path is None:
        sys.stderr.write(f"Unknown step: {name!r}. Available: {', '.join(STEP_MODULES)}\n")
        sys.exit(1)

    module = importlib.import_module(module_path)

    if hasattr(module, "main"):
        module.main()
    elif hasattr(module, "run"):
        module.run()
    else:
        raise RuntimeError(f"Step module {module_path} lacks an entry function (main/run)")


def _arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run one or more pipeline steps in order.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--steps",
        nargs="+",
        default=DEFAULT_STEPS,
        metavar="STEP",
        help=f"Ordered list of steps to execute (available: {', '.join(STEP_MODULES)})",
    )
    return p


def main() -> None:  
    args = _arg_parser().parse_args()
    for step_name in args.steps:
        _run_step(step_name)


if __name__ == "__main__":
    main()