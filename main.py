import json
import logging
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
import sys

from src.crawler import crawl_by_keywords
from src.exporter import export_to_csv, load_schema_columns
from src.quality import filter_and_score_records

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"


def process_local_images(input_path: Path) -> None:
    """Run the independent local image OCR path and preserve per-image metadata."""
    from src.image_ingestor import discover_images
    from src.image_preprocessor import prepare_image
    from src.ocr_engine import build_engine, result_as_dict, run_ocr

    config_path = CONFIG_DIR / "ocr_config.json"
    with config_path.open("r", encoding="utf-8") as f:
        ocr_config = json.load(f)

    images = discover_images(input_path)
    if not images:
        print(f"No supported images found in: {input_path}")
        return

    output_dir = BASE_DIR / ocr_config.get("output", {}).get("ocr_directory", "data/interim/ocr")
    working_dir = output_dir / "working"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Images discovered: {len(images)}")
    successes = failures = 0
    engine = None
    engine_version = None

    for image_path in images:
        digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
        record_id = f"{image_path.stem}_{digest[:12]}"
        try:
            prepared_path = prepare_image(image_path, working_dir / record_id, ocr_config)
            if engine is None:
                engine, engine_version = build_engine(ocr_config)
            result = run_ocr(prepared_path, ocr_config, engine, engine_version)
            record = {
                "source_image": str(image_path.resolve()),
                "source_image_sha256": digest,
                "processed_at": datetime.now().astimezone().isoformat(),
                "ocr": result_as_dict(result),
                "needs_review": (
                    result.confidence_mean is None
                    or result.confidence_mean < float(ocr_config.get("review", {}).get("confidence_threshold", 0.75))
                ),
            }
            output_path = output_dir / f"{record_id}.json"
            output_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            successes += 1
            confidence = "unavailable" if result.confidence_mean is None else f"{result.confidence_mean:.3f}"
            print(f"\n[{image_path.name}] OCR confidence mean: {confidence}; review recommended: {record['needs_review']}")
            print(result.text or "(No text recognized)")
            print(f"Metadata: {output_path}")
        except Exception as exc:
            failures += 1
            print(f"[{image_path.name}] Failed: {exc}", file=sys.stderr)

    print(f"OCR complete: {successes} succeeded, {failures} failed; originals preserved.")


def _run_cli() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "ocr":
        parser = argparse.ArgumentParser(description="Process local recruitment images with OCR.")
        parser.add_argument("ocr")
        parser.add_argument("--input", required=True, type=Path, help="Image file or directory")
        args = parser.parse_args()
        process_local_images(args.input)
        return
    main()

def setup_logger() -> logging.Logger:
    log_dir = DATA_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"run_{datetime.now().strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger("myrobin_crawler")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def main() -> None:
    logger = setup_logger()

    keywords_path = CONFIG_DIR / "keywords.json"
    schema_path = CONFIG_DIR / "schema_columns.json"

    with keywords_path.open("r", encoding="utf-8") as f:
        kw_config = json.load(f)

    mode = str(kw_config.get("mode") or "dummy").strip().lower()
    telegram_channels = kw_config.get("telegram_channels", [])
    instagram_tags = kw_config.get("instagram_tags", [])
    ig_user_data_dir = kw_config.get("ig_user_data_dir", ".playwright_ig_profile")
    keywords = kw_config.get("keywords", [])
    red_flag_terms = kw_config.get("red_flag_terms", [])
    min_quality_score = int(kw_config.get("min_quality_score", 50))

    logger.info("Memulai crawling (mode=%s) dengan keywords: %s", mode, keywords)
    raw_records = crawl_by_keywords(
        keywords=keywords,
        mode=mode,
        telegram_channels=telegram_channels,
        instagram_tags=instagram_tags,
        ig_user_data_dir=ig_user_data_dir,
        ig_headless=True,
    )

    # Simpan snapshot data mentah
    raw_dir = DATA_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_file = raw_dir / f"raw_{mode}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    with raw_file.open("w", encoding="utf-8") as f:
        json.dump(raw_records, f, ensure_ascii=False, indent=2)
    logger.info("Raw data tersimpan di: %s", raw_file)

    # Filter kualitas, red flag, dan deduplikasi
    passed_records = filter_and_score_records(
        records=raw_records,
        red_flag_terms=red_flag_terms,
        min_quality_score=min_quality_score,
        only_passed=True,
    )
    logger.info("Total data lolos cek kualitas & deduplikasi: %d", len(passed_records))

    # Ekspor ke CSV sesuai skema ERD
    columns = load_schema_columns(schema_path)
    csv_path = export_to_csv(
        rows=passed_records,
        columns=columns,
        output_dir=DATA_DIR / "released",
        filename_prefix="job_posts",
    )
    logger.info("CSV siap rilis berhasil dibuat di: %s", csv_path)


if __name__ == "__main__":
    _run_cli()
