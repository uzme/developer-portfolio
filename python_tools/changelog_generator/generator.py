"""Generate a small Markdown changelog from conventional commit subjects."""

from __future__ import annotations

import re
from collections import defaultdict


COMMIT_RE = re.compile(r"^(?P<kind>[a-z]+)(?:\([^)]*\))?(?P<breaking>!)?:\s+(?P<subject>.+)$", re.I)


def generate_changelog(commits: list[str], version: str = "Unreleased") -> str:
    """Group conventional commit subjects into a readable Markdown section."""
    groups: dict[str, list[str]] = defaultdict(list)
    labels = {"feat": "Added", "fix": "Fixed", "docs": "Documentation", "refactor": "Changed", "perf": "Performance", "chore": "Maintenance"}
    for commit in commits:
        match = COMMIT_RE.match(commit.strip())
        if not match:
            continue
        label = labels.get(match.group("kind").lower(), "Other")
        prefix = "**BREAKING:** " if match.group("breaking") else ""
        groups[label].append(f"- {prefix}{match.group('subject').strip()}")
    lines = [f"## {version}", ""]
    for label in labels.values():
        entries = groups.get(label)
        if entries:
            lines.extend([f"### {label}", *entries, ""])
    if len(lines) == 2:
        lines.append("No conventional commits found.")
    return "\n".join(lines).rstrip() + "\n"
