import hashlib
import hmac
import unittest

from python_tools.webhook_validator import (
    WebhookValidationError,
    validate_delivery,
    verify_signature,
)


class WebhookValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = b'{"action":"push","repository":"demo"}'
        self.secret = "local-test-secret"
        digest = hmac.new(self.secret.encode(), self.payload, hashlib.sha256).hexdigest()
        self.signature = f"sha256={digest}"

    def test_accepts_valid_signature(self) -> None:
        self.assertTrue(verify_signature(self.payload, self.signature, self.secret))

    def test_rejects_modified_payload(self) -> None:
        self.assertFalse(verify_signature(b'{"action":"delete"}', self.signature, self.secret))

    def test_rejects_missing_or_wrong_prefix(self) -> None:
        self.assertFalse(verify_signature(self.payload, None, self.secret))
        self.assertFalse(verify_signature(self.payload, "sha1=abc", self.secret))

    def test_validates_event_type(self) -> None:
        headers = {
            "X-Hub-Signature-256": self.signature,
            "X-GitHub-Event": "push",
        }
        self.assertTrue(validate_delivery(self.payload, headers, self.secret, {"push"}))
        self.assertFalse(validate_delivery(self.payload, headers, self.secret, {"pull_request"}))

    def test_accepts_lowercase_header_names(self) -> None:
        headers = {
            "x-hub-signature-256": self.signature,
            "x-github-event": "push",
        }
        self.assertTrue(validate_delivery(self.payload, headers, self.secret, {"push"}))

    def test_empty_secret_is_rejected(self) -> None:
        with self.assertRaises(WebhookValidationError):
            verify_signature(self.payload, self.signature, "")

    def test_payload_must_be_raw_bytes(self) -> None:
        with self.assertRaises(TypeError):
            verify_signature("not-bytes", self.signature, self.secret)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
