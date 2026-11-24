"""PaddleOCR adapter independent of any vacancy source connector."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class OCRResult:
    text: str
    regions: list[dict[str, Any]]
    engine: str
    engine_version: str | None
    confidence_mean: float | None


def build_engine(config: dict):
    try:
        import paddleocr
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise RuntimeError(
            "PaddleOCR is not installed. Install the OCR dependencies described in requirements.txt; "
            "the first run may download CPU runtime/model files."
        ) from exc

    kwargs: dict[str, Any] = {"device": config.get("device", "cpu")}
    # Indonesian recruitment posters use Latin text. The English recognizer handles
    # Latin script without claiming language-specific Indonesian model support.
    try:
        engine = PaddleOCR(lang="en", **kwargs)
    except TypeError:
        # Compatibility with PaddleOCR releases that predate the device argument.
        kwargs.pop("device", None)
        engine = PaddleOCR(lang="en", **kwargs)
    return engine, getattr(paddleocr, "__version__", None)


def _flatten_prediction(prediction: Any) -> list[dict[str, Any]]:
    """Normalize PaddleOCR prediction objects across supported result layouts."""
    if hasattr(prediction, "json"):
        prediction = prediction.json
        if callable(prediction):
            prediction = prediction()
    if isinstance(prediction, dict) and "res" in prediction:
        prediction = prediction["res"]
    if not isinstance(prediction, (dict, list, tuple)) and hasattr(prediction, "__iter__"):
        prediction = list(prediction)
    if isinstance(prediction, list) and len(prediction) == 1 and isinstance(prediction[0], dict):
        prediction = prediction[0]
        if "res" in prediction:
            prediction = prediction["res"]
    if isinstance(prediction, dict):
        texts = prediction.get("rec_texts", [])
        scores = prediction.get("rec_scores", [])
        boxes = prediction.get("dt_polys", prediction.get("rec_polys", []))
        return [
            {"text": str(value), "confidence": float(scores[i]) if i < len(scores) else None,
             "box": boxes[i].tolist() if i < len(boxes) and hasattr(boxes[i], "tolist") else (boxes[i] if i < len(boxes) else None)}
            for i, value in enumerate(texts)
        ]

    regions: list[dict[str, Any]] = []
    if isinstance(prediction, list):
        for page in prediction:
            if not isinstance(page, list):
                continue
            for line in page:
                if isinstance(line, (list, tuple)) and len(line) >= 2:
                    box, recognition = line[0], line[1]
                    if isinstance(recognition, (list, tuple)) and recognition:
                        regions.append({"text": str(recognition[0]), "confidence": float(recognition[1]) if len(recognition) > 1 else None,
                                        "box": box.tolist() if hasattr(box, "tolist") else box})
    return regions


def run_ocr(image_path: Path, config: dict, engine=None, engine_version: str | None = None) -> OCRResult:
    """Recognize text in a prepared image and return regions plus confidence."""
    if engine is None:
        engine, engine_version = build_engine(config)
    if hasattr(engine, "predict"):
        prediction = engine.predict(str(image_path))
    else:
        prediction = engine.ocr(str(image_path), cls=True)
    regions = _flatten_prediction(prediction)
    confidences = [region["confidence"] for region in regions if region["confidence"] is not None]
    return OCRResult(
        text="\n".join(region["text"] for region in regions),
        regions=regions,
        engine="paddleocr",
        engine_version=engine_version,
        confidence_mean=sum(confidences) / len(confidences) if confidences else None,
    )


def result_as_dict(result: OCRResult) -> dict[str, Any]:
    return asdict(result)
