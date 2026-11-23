import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_schema_columns(schema_path: Path) -> list[str]:
    with schema_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    columns = data.get("columns", [])
    if not columns:
        raise ValueError(f"Daftar 'columns' kosong di {schema_path}")
    return columns


def export_to_csv(
    rows: list[dict[str, Any]],
    columns: list[str],
    output_dir: Path,
    filename_prefix: str = "job_posts",
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = output_dir / f"{filename_prefix}_{timestamp}.csv"

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=columns,
            extrasaction="ignore",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        for row in rows:
            cleaned_row = {col: ("" if row.get(col) is None else row.get(col)) for col in columns}
            writer.writerow(cleaned_row)

    return output_path