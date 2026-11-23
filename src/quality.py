import json
import re
from datetime import datetime, timezone
from typing import Any

VALID_EMPLOYMENT_TYPES = {"tetap", "kontrak", "harian", "mitra", "magang"}
VALID_GENDERS = {"pria", "wanita", "semua"}
VALID_EDUCATIONS = {"tidak_ada", "sd", "smp", "sma_smk", "d3", "s1"}
VALID_SALARY_TYPES = {"umk", "tetap", "rentang", "pokok_plus_insentif", "nego"}
VALID_STATUSES = {"draft", "published", "closed", "archived"}

DEFAULT_RED_FLAGS = [
    "biaya administrasi",
    "biaya seragam",
    "transfer biaya",
    "titip dana",
    "jaminan ijazah",
    "biaya proses",
    "bayar pendaftaran",
]


def slugify(text: str | None) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def _normalize_enum(value: Any, allowed: set[str], fallback: str | None = None) -> str | None:
    if not value:
        return fallback
    val = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    return val if val in allowed else fallback


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    val = str(value).strip().lower()
    if val in {"1", "true", "ya", "yes", "y"}:
        return True
    if val in {"0", "false", "tidak", "no", "n"}:
        return False
    return default


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(".", "").replace(",", "").strip()))
    except ValueError:
        return None


def _to_json_str(value: Any) -> str:
    if isinstance(value, str):
        # Coba pastikan valid JSON string; kalau bukan, bungkus jadi list/string aman
        try:
            parsed = json.loads(value)
            return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            return json.dumps([{"note": value}], ensure_ascii=False)
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return "[]"


def evaluate_record(
    raw: dict[str, Any],
    red_flag_terms: list[str] | None = None,
    min_quality_score: int = 50,
) -> dict[str, Any]:
    terms = [t.lower().strip() for t in (red_flag_terms or DEFAULT_RED_FLAGS)]

    title = str(raw.get("title") or "").strip()
    description = str(raw.get("description") or "").strip()
    company_name = str(raw.get("company_name") or "").strip()
    location_city = str(raw.get("location_city") or "").strip()
    salary_min = _to_int(raw.get("salary_min"))
    salary_max = _to_int(raw.get("salary_max"))
    salary_info_text = str(raw.get("salary_note") or "").strip()
    apply_channels_json = _to_json_str(raw.get("apply_channels"))
    requirements_json = _to_json_str(raw.get("requirements"))
    benefits_json = _to_json_str(raw.get("benefits"))

    combined_text = f"{title} {description} {company_name} {location_city} {salary_info_text} {apply_channels_json}".lower()

    score = 0
    notes: list[str] = []

    # 1. Kelengkapan informasi inti
    if title:
        score += 20
    else:
        notes.append("missing_title")

    if len(description) >= 30:
        score += 20
    else:
        notes.append("short_or_missing_description")

    if company_name and company_name.lower() not in {"pt ternama", "perusahaan", "-", "n/a"}:
        score += 20
    else:
        notes.append("unclear_company_name")

    if location_city:
        score += 15
    else:
        notes.append("missing_location_city")

    if apply_channels_json != "[]":
        score += 15
    else:
        notes.append("missing_apply_channel")

    if salary_min is not None or salary_max is not None or salary_info_text:
        score += 10

    # 2. Cek red flag indikasi calo / penipuan
    matched_flags = [term for term in terms if term in combined_text]
    is_free = _to_bool(raw.get("is_free_of_charge"), default=len(matched_flags) == 0)

    if matched_flags:
        score -= 60
        is_free = False
        notes.append(f"red_flag:{','.join(matched_flags)}")

    score = max(0, min(100, score))
    status_quality = "PASSED" if (score >= min_quality_score and not matched_flags) else "REJECTED"

    now_iso = datetime.now(timezone.utc).isoformat()

    normalized: dict[str, Any] = {
        "source_platform": str(raw.get("source_platform") or "").strip().lower(),
        "source_url": str(raw.get("source_url") or "").strip(),
        "company_name": company_name,
        "company_slug": str(raw.get("company_slug") or slugify(company_name)),
        "company_logo_url": str(raw.get("company_logo_url") or "").strip() or None,
        "company_industry": str(raw.get("company_industry") or "").strip() or None,
        "company_address": str(raw.get("company_address") or "").strip() or None,
        "category_name": str(raw.get("category_name") or "").strip() or None,
        "category_slug": str(raw.get("category_slug") or slugify(raw.get("category_name"))),
        "location_province": str(raw.get("location_province") or "").strip() or None,
        "location_city": location_city or None,
        "location_area": str(raw.get("location_area") or "").strip() or None,
        "title": title,
        "slug": str(raw.get("slug") or slugify(f"{title}-{company_name}")),
        "description": description,
        "employment_type": _normalize_enum(raw.get("employment_type"), VALID_EMPLOYMENT_TYPES, "kontrak"),
        "contract_months": _to_int(raw.get("contract_months")),
        "quota": _to_int(raw.get("quota")),
        "gender": _normalize_enum(raw.get("gender"), VALID_GENDERS, "semua"),
        "min_age": _to_int(raw.get("min_age")),
        "max_age": _to_int(raw.get("max_age")),
        "min_education": _normalize_enum(raw.get("min_education"), VALID_EDUCATIONS, "sma_smk"),
        "min_height_cm": _to_int(raw.get("min_height_cm")),
        "fresh_graduate_welcome": _to_bool(raw.get("fresh_graduate_welcome"), default=False),
        "shift_work": _to_bool(raw.get("shift_work"), default=False),
        "salary_type": _normalize_enum(raw.get("salary_type"), VALID_SALARY_TYPES, "nego"),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_note": salary_info_text or None,
        "is_free_of_charge": is_free,
        "status": _normalize_enum(raw.get("status"), VALID_STATUSES, "draft"),
        "published_at": raw.get("published_at") or now_iso,
        "expires_at": raw.get("expires_at"),
        "requirements_json": requirements_json,
        "benefits_json": benefits_json,
        "apply_channels_json": apply_channels_json,
        "quality_score": score,
        "quality_notes": f"{status_quality}: {'; '.join(notes)}" if notes else f"{status_quality}: ok",
    }
    return normalized


def filter_and_score_records(
    records: list[dict[str, Any]],
    red_flag_terms: list[str] | None = None,
    min_quality_score: int = 50,
    only_passed: bool = True,
) -> list[dict[str, Any]]:
    seen_keys: set[tuple[str, str, str]] = set()
    results: list[dict[str, Any]] = []

    for item in records:
        evaluated = evaluate_record(
            item,
            red_flag_terms=red_flag_terms,
            min_quality_score=min_quality_score,
        )

        # Deduplikasi berdasarkan judul + perusahaan + kota
        dedup_key = (
            evaluated["title"].lower(),
            evaluated["company_name"].lower(),
            (evaluated["location_city"] or "").lower(),
        )
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        is_passed = evaluated["quality_notes"].startswith("PASSED:")
        if only_passed and not is_passed:
            continue

        results.append(evaluated)

    return results