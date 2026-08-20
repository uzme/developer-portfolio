"""Dependency-free HTTP health checks."""

from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class HealthResult:
    url: str
    status: int | None
    elapsed_ms: float | None
    error: str | None = None

    @property
    def healthy(self) -> bool:
        return self.error is None and self.status is not None and 200 <= self.status < 400


def check_endpoint(url: str, timeout: float = 8.0) -> HealthResult:
    """Perform a minimal HEAD request and report latency without response bodies."""
    started = time.perf_counter()
    request = Request(url, method="HEAD", headers={"User-Agent": "portfolio-health-monitor/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            elapsed = (time.perf_counter() - started) * 1000
            return HealthResult(url, response.status, round(elapsed, 2), None)
    except HTTPError as error:
        elapsed = (time.perf_counter() - started) * 1000
        return HealthResult(url, error.code, round(elapsed, 2), str(error))
    except (TimeoutError, URLError, ValueError) as error:
        return HealthResult(url, None, None, str(error))
