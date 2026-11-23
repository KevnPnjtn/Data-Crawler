import json
import logging
from datetime import datetime
from pathlib import Path

from src.crawler import crawl_by_keywords
from src.exporter import export_to_csv, load_schema_columns
from src.quality import filter_and_score_records

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"


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
    keywords = kw_config.get("keywords", [])
    red_flag_terms = kw_config.get("red_flag_terms", [])
    min_quality_score = int(kw_config.get("min_quality_score", 50))

    logger.info("Memulai crawling (mode=%s) dengan keywords: %s", mode, keywords)
    raw_records = crawl_by_keywords(
        keywords=keywords,
        mode=mode,
        telegram_channels=telegram_channels,
    )
    logger.info("Total data mentah cocok keyword: %d", len(raw_records))

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
    main()