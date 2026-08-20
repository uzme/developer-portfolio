"""Lightweight repository secret and risky-file auditor."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


SECRET_PATTERNS = {
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "generic-api-key": re.compile(r"(?i)\b(api[_-]?key|secret|token)\s*[:=]\s*[\"'][^\"']{12,}[\"']"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}

RISKY_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int | None
    rule: str
    severity: str
    detail: str


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def audit_repository(root: str | Path) -> list[Finding]:
    """Return findings while never including secret values in details."""
    base = Path(root).resolve()
    findings: list[Finding] = []
    for path in _iter_files(base):
        relative = path.relative_to(base).as_posix()
        if path.name in RISKY_NAMES:
            findings.append(Finding(relative, None, "risky-file", "high", "sensitive filename detected"))
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for rule, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    findings.append(Finding(relative, line_number, rule, "high", "possible secret pattern detected"))
    return findings
