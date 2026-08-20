"""Simple image optimization helpers using Pillow when installed."""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional runtime dependency
    Image = None


SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


def optimize_image(source: str | Path, destination: str | Path, quality: int = 85) -> int:
    """Save an optimized image and return its output size in bytes."""
    if Image is None:
        raise RuntimeError("Pillow is required for image optimization")
    source_path = Path(source)
    destination_path = Path(destination)
    if source_path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"unsupported image format: {source_path.suffix}")
    if not 1 <= quality <= 100:
        raise ValueError("quality must be between 1 and 100")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as image:
        output = image
        if destination_path.suffix.lower() in {".jpg", ".jpeg"} and image.mode in {"RGBA", "P", "LA"}:
            output = image.convert("RGB")
        output.save(destination_path, optimize=True, quality=quality)
    return destination_path.stat().st_size
