import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from python_tools.api_health_monitor import check_endpoint
from python_tools.changelog_generator import generate_changelog
from python_tools.dependency_reporter import parse_package_json, parse_requirements
from python_tools.environment_audit import audit_environment, missing_variables
from python_tools.event_router import EventRouter
from python_tools.image_optimizer import optimize_image
from python_tools.prompt_validator import validate_json_input, validate_prompt
from python_tools.project_stats import collect_stats, to_markdown
from python_tools.readme_link_checker import check_url, extract_urls
from python_tools.repository_security_auditor import audit_repository


class LinkCheckerTests(unittest.TestCase):
    def test_extracts_unique_urls(self):
        text = "[site](https://example.com) and https://example.com/docs."
        self.assertEqual(extract_urls(text), ["https://example.com", "https://example.com/docs"])

    @patch("python_tools.readme_link_checker.link_checker.urlopen")
    def test_checks_url(self, urlopen):
        response = MagicMock(status=200, geturl=lambda: "https://example.com")
        urlopen.return_value.__enter__.return_value = response
        self.assertTrue(check_url("https://example.com").ok)


class SecurityAuditorTests(unittest.TestCase):
    def test_reports_secret_without_value(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.py").write_text('API_KEY = "not-a-real-secret-value"\n', encoding="utf-8")
            findings = audit_repository(root)
            self.assertEqual(findings[0].rule, "generic-api-key")
            self.assertNotIn("not-a-real-secret-value", findings[0].detail)


class HealthMonitorTests(unittest.TestCase):
    @patch("python_tools.api_health_monitor.monitor.urlopen")
    def test_healthy_endpoint(self, urlopen):
        response = MagicMock(status=204)
        urlopen.return_value.__enter__.return_value = response
        self.assertTrue(check_endpoint("https://example.com").healthy)


class EventRouterTests(unittest.TestCase):
    def test_action_handler_takes_precedence(self):
        router = EventRouter()
        router.register("push", lambda payload: "generic")
        router.register("push", lambda payload: "main", action="created")
        self.assertEqual(router.dispatch("push", {"action": "created"}), "main")
        self.assertEqual(router.dispatch("push", {"action": "deleted"}), "generic")


class TextReportTests(unittest.TestCase):
    def test_changelog_groups_commits(self):
        output = generate_changelog(["feat: add monitor", "fix: handle timeout", "bad commit"])
        self.assertIn("### Added", output)
        self.assertIn("### Fixed", output)
        self.assertNotIn("bad commit", output)

    def test_dependency_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements = root / "requirements.txt"
            requirements.write_text("requests>=2.0\n# comment\n", encoding="utf-8")
            package = root / "package.json"
            package.write_text(json.dumps({"dependencies": {"react": "^18"}}), encoding="utf-8")
            self.assertEqual(parse_requirements(requirements)[0]["name"], "requests")
            self.assertEqual(parse_package_json(package)[0]["name"], "react")


class StatsAndEnvironmentTests(unittest.TestCase):
    def test_stats_and_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.py").write_text("print('ok')", encoding="utf-8")
            stats = collect_stats(root)
            self.assertEqual(stats["languages"]["Python"], 1)
            self.assertIn("Project statistics", to_markdown(stats))

    def test_environment_never_returns_values(self):
        values = {"TOKEN": "secret", "EMPTY": ""}
        statuses = audit_environment(["TOKEN", "EMPTY", "MISSING"], values)
        self.assertEqual([item.non_empty for item in statuses], [True, False, False])
        self.assertEqual(missing_variables(["TOKEN", "EMPTY"], values), ["EMPTY"])


class ImageOptimizerTests(unittest.TestCase):
    def test_optimizes_png_to_jpeg(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.png"
            destination = Path(directory) / "optimized.jpg"
            Image.new("RGBA", (4, 4), (20, 40, 60, 255)).save(source)
            size = optimize_image(source, destination)
            self.assertGreater(size, 0)
            self.assertTrue(destination.exists())


class PromptValidatorTests(unittest.TestCase):
    def test_validates_prompt_length(self):
        self.assertTrue(validate_prompt("Explain this API").valid)
        self.assertFalse(validate_prompt("").valid)

    def test_validates_json_fields(self):
        self.assertTrue(validate_json_input('{"task":"summarize"}', {"task"}).valid)
        self.assertFalse(validate_json_input("not-json", {"task"}).valid)
        self.assertFalse(validate_json_input("{}", {"task"}).valid)


if __name__ == "__main__":
    unittest.main()
