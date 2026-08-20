"""Check Markdown links without exposing credentials."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\((https?://[^)\s]+)")
BARE_URL = re.compile(r"(?<![\w/=])(https?://[^\s)>]+)")


@dataclass(frozen=True)
class LinkResult:
    url: str
    status: int | None
    final_url: str | None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status is not None and 200 <= self.status < 400


def extract_urls(markdown: str) -> list[str]:
    """Return unique HTTP(S) URLs in stable source order."""
    found: list[str] = []
    for match in MARKDOWN_LINK.finditer(markdown):
        found.append(match.group(1).rstrip(".,;"))
    for match in BARE_URL.finditer(markdown):
        found.append(match.group(1).rstrip(".,;"))
    return list(dict.fromkeys(found))


def check_url(url: str, timeout: float = 8.0) -> LinkResult:
    """Check one URL with a safe HEAD request and GET fallback."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return LinkResult(url, None, None, "unsupported URL")
    request = Request(url, method="HEAD", headers={"User-Agent": "portfolio-link-checker/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return LinkResult(url, response.status, response.geturl())
    except HTTPError as error:
        if error.code not in {403, 405, 501}:
            return LinkResult(url, error.code, error.geturl(), str(error))
    except (TimeoutError, URLError) as error:
        return LinkResult(url, None, None, str(error))

    try:
        fallback = Request(url, method="GET", headers={"User-Agent": "portfolio-link-checker/1.0"})
        with urlopen(fallback, timeout=timeout) as response:
            return LinkResult(url, response.status, response.geturl())
    except HTTPError as error:
        return LinkResult(url, error.code, error.geturl(), str(error))
    except (TimeoutError, URLError) as error:
        return LinkResult(url, None, None, str(error))


def check_markdown(path: str | Path, timeout: float = 8.0) -> list[LinkResult]:
    """Extract and check links from a Markdown file."""
    content = Path(path).read_text(encoding="utf-8")
    return [check_url(url, timeout=timeout) for url in extract_urls(content)]
