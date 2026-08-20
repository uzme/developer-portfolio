"""Parse common dependency files into a stable report."""

from __future__ import annotations

import json
import re
from pathlib import Path


VERSION_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*(?:==|>=|<=|~=|>|<)\s*(.+)$")


def parse_requirements(path: str | Path) -> list[dict[str, str]]:
    """Parse pinned or constrained requirements.txt lines."""
    result: list[dict[str, str]] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "git+")):
            continue
        match = VERSION_RE.match(line)
        if match:
            result.append({"name": match.group(1), "constraint": match.group(2).strip()})
        else:
            result.append({"name": line, "constraint": "unspecified"})
    return result


def parse_package_json(path: str | Path) -> list[dict[str, str]]:
    """Parse dependencies and devDependencies from package.json."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    result: list[dict[str, str]] = []
    for section in ("dependencies", "devDependencies"):
        for name, version in sorted(data.get(section, {}).items()):
            result.append({"name": name, "constraint": version, "section": section})
    return result
