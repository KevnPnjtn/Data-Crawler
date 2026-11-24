"""Create OCR-ready working copies while preserving the source image."""

from pathlib import Path


def prepare_image(source: Path, working_dir: Path, config: dict) -> Path:
    """Validate and prepare an image copy using configured basic adjustments."""
    try:
        from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError
    except ImportError as exc:
        raise RuntimeError("Pillow is required for image processing. Install project requirements.") from exc

    preprocessing = config.get("preprocessing", {})
    working_dir.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(source) as opened:
            if opened.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError(f"Unsupported image content: {opened.format or 'unknown'}")
            image = ImageOps.exif_transpose(opened).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"Invalid or corrupted image: {source}") from exc

    if preprocessing.get("enabled", True):
        max_dimension = int(preprocessing.get("max_dimension", 2400))
        if preprocessing.get("resize_if_needed", True) and max(image.size) > max_dimension:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        if preprocessing.get("contrast_enhancement", True):
            image = ImageEnhance.Contrast(image).enhance(float(preprocessing.get("contrast_factor", 1.25)))

    output_path = working_dir / f"{source.stem}.png"
    image.save(output_path, format="PNG")
    return output_path
