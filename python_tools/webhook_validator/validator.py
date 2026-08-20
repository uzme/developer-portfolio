"""Secure GitHub webhook signature validation helpers."""

from __future__ import annotations

import hashlib
import hmac
from typing import Mapping


class WebhookValidationError(ValueError):
    """Raised when a webhook signature input is malformed."""


def _expected_signature(payload: bytes, secret: str) -> str:
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if not secret:
        raise WebhookValidationError("webhook secret must not be empty")
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    """Verify GitHub's X-Hub-Signature-256 header in constant time.

    The raw request body must be passed unchanged. Do not parse and re-serialize
    JSON before calling this function because whitespace and key ordering matter
    to the HMAC digest.
    """

    if not signature or not signature.startswith("sha256="):
        return False
    expected = _expected_signature(payload, secret)
    return hmac.compare_digest(expected, signature)


def validate_delivery(
    payload: bytes,
    headers: Mapping[str, str],
    secret: str,
    allowed_events: set[str] | None = None,
) -> bool:
    """Validate signature and optionally restrict accepted GitHub event types."""

    signature = headers.get("X-Hub-Signature-256") or headers.get("x-hub-signature-256")
    if not verify_signature(payload, signature, secret):
        return False

    if allowed_events is None:
        return True

    event = headers.get("X-GitHub-Event") or headers.get("x-github-event")
    return event in allowed_events
