"""Validation helpers for structured AI prompts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]


def validate_prompt(text: str, min_length: int = 1, max_length: int = 12000) -> ValidationResult:
    errors: list[str] = []
    if not text.strip():
        errors.append("prompt must not be empty")
    if len(text) < min_length:
        errors.append(f"prompt must be at least {min_length} characters")
    if len(text) > max_length:
        errors.append(f"prompt must not exceed {max_length} characters")
    return ValidationResult(not errors, tuple(errors))


def validate_json_input(text: str, required_fields: set[str] | None = None) -> ValidationResult:
    try:
        value: Any = json.loads(text)
    except json.JSONDecodeError as error:
        return ValidationResult(False, (f"invalid JSON at line {error.lineno}, column {error.colno}",))
    if not isinstance(value, dict):
        return ValidationResult(False, ("JSON root must be an object",))
    missing = sorted((required_fields or set()) - value.keys())
    if missing:
        return ValidationResult(False, (f"missing required fields: {', '.join(missing)}",))
    return ValidationResult(True, ())
