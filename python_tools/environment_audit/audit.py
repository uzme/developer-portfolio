"""Safe environment variable presence checks."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class VariableStatus:
    name: str
    present: bool
    non_empty: bool


def audit_environment(names: list[str], environ: dict[str, str] | None = None) -> list[VariableStatus]:
    """Report presence only; never return variable values."""
    values = os.environ if environ is None else environ
    return [VariableStatus(name, name in values, bool(values.get(name, ""))) for name in names]


def missing_variables(names: list[str], environ: dict[str, str] | None = None) -> list[str]:
    return [item.name for item in audit_environment(names, environ) if not item.non_empty]
