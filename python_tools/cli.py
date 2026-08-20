"""Command-line entry point for the Portfolio Automation Toolkit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .api_health_monitor import check_endpoint
from .project_stats import collect_stats, to_markdown
from .readme_link_checker import check_markdown
from .repository_security_auditor import audit_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portfolio Automation Toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    links = subparsers.add_parser("links", help="check Markdown links")
    links.add_argument("path", type=Path)

    audit = subparsers.add_parser("audit", help="scan a repository without printing secrets")
    audit.add_argument("path", type=Path)

    health = subparsers.add_parser("health", help="check one HTTP endpoint")
    health.add_argument("url")

    stats = subparsers.add_parser("stats", help="collect local project statistics")
    stats.add_argument("path", type=Path)
    stats.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "links":
        results = check_markdown(args.path)
        for result in results:
            print(f"{'OK' if result.ok else 'FAIL'}\t{result.status or '-'}\t{result.url}")
        return 0 if all(result.ok for result in results) else 1
    if args.command == "audit":
        findings = audit_repository(args.path)
        for finding in findings:
            location = f":{finding.line}" if finding.line else ""
            print(f"{finding.severity.upper()}\t{finding.path}{location}\t{finding.rule}\t{finding.detail}")
        return 1 if findings else 0
    if args.command == "health":
        result = check_endpoint(args.url)
        print(json.dumps(result.__dict__, ensure_ascii=False))
        return 0 if result.healthy else 1
    if args.command == "stats":
        collected = collect_stats(args.path)
        print(json.dumps(collected, indent=2) if args.as_json else to_markdown(collected), end="")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
