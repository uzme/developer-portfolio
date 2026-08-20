# Python Webhook Validator

Small, dependency-free helpers for validating GitHub webhook deliveries.

The validator checks GitHub's `X-Hub-Signature-256` HMAC header with a constant-time comparison and can restrict accepted event types. The request body must be passed as the original raw bytes before JSON parsing.

```python
from python_tools.webhook_validator import validate_delivery

is_valid = validate_delivery(
    payload=request.get_data(),
    headers=request.headers,
    secret=os.environ["GITHUB_WEBHOOK_SECRET"],
    allowed_events={"push", "pull_request"},
)

if not is_valid:
    return {"error": "invalid webhook"}, 401
```

The module uses only Python's standard library. The test suite covers valid signatures, modified payloads, missing headers, event filtering, lowercase headers, and invalid input.
