"""Small local project statistics helpers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


LANGUAGE_BY_SUFFIX = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".css": "CSS", ".html": "HTML", ".md": "Markdown",
}


def collect_stats(root: str | Path) -> dict[str, object]:
    """Count tracked-looking files by language without reading file contents."""
    base = Path(root)
    counts: Counter[str] = Counter()
    files = 0
    for path in base.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "node_modules" in path.parts or "__pycache__" in path.parts:
            continue
        files += 1
        counts[LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "Other")] += 1
    return {"root": str(base), "files": files, "languages": dict(counts.most_common())}


def to_markdown(stats: dict[str, object]) -> str:
    """Render collected stats as a compact Markdown report."""
    lines = ["# Project statistics", "", f"Files scanned: **{stats['files']}**", "", "| Language | Files |", "|---|---:|"]
    for language, count in stats["languages"].items():
        lines.append(f"| {language} | {count} |")
    return "\n".join(lines) + "\n"


def to_json(stats: dict[str, object]) -> str:
    return json.dumps(stats, indent=2, ensure_ascii=False) + "\n"
