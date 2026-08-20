# Portfolio Automation Toolkit

A dependency-light Python toolkit for maintaining a professional developer portfolio, validating integrations, and automating repository hygiene.

## Modules

| Module | Purpose |
|---|---|
| `webhook_validator` | Verifies GitHub `X-Hub-Signature-256` signatures using HMAC and constant-time comparison. |
| `readme_link_checker` | Extracts and checks Markdown HTTP(S) links with timeout and redirect reporting. |
| `repository_security_auditor` | Finds risky filenames and possible secret patterns without printing secret values. |
| `api_health_monitor` | Reports endpoint status and latency without storing response bodies. |
| `event_router` | Routes validated GitHub events by event name and optional action. |
| `changelog_generator` | Groups conventional commits into a Markdown changelog. |
| `dependency_reporter` | Parses common Python and Node dependency files into stable records. |
| `project_stats` | Counts project files by language and renders Markdown/JSON reports. |
| `image_optimizer` | Optimizes common PNG, JPEG and WEBP assets when Pillow is installed. |
| `environment_audit` | Checks required environment variable presence without exposing values. |
| `prompt_validator` | Validates AI prompt length and structured JSON input fields. |

## Design principles

The modules use the Python standard library wherever practical. Network checks have explicit timeouts, webhook secrets are never logged, security findings contain no secret values, and image processing validates formats and quality boundaries. Every public helper has unit-test coverage in `tests/`.

## Example

```python
from python_tools.readme_link_checker import check_markdown
from python_tools.repository_security_auditor import audit_repository

links = check_markdown("README.md")
findings = audit_repository(".")

for result in links:
    print(result.url, result.status, result.ok)
for finding in findings:
    print(finding.path, finding.line, finding.rule, finding.severity)
```

Run the full test suite with:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The lightweight CLI exposes the most common checks:

```bash
python -m python_tools.cli links README.md
python -m python_tools.cli audit .
python -m python_tools.cli health https://github.com
python -m python_tools.cli stats . --json
```

This toolkit is designed for portfolio demonstration and safe local/CI checks. It does not upload source files, send credentials to third parties, or replace a full secret-scanning service.
