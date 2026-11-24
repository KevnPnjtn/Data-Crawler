"""Discover and validate locally supplied images without modifying originals."""

from pathlib import Path

SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def discover_images(input_path: Path) -> list[Path]:
    """Return supported image files from a file or directory, in stable order."""
    path = input_path.expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Input path does not exist: {path}")
    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported image format: {path.suffix or '(no extension)'}")
        return [path]
    return sorted(
        (item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES),
        key=lambda item: str(item).casefold(),
    )
