from typing import Any
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


DUMMY_POSTS: list[dict[str, Any]] = [
    {
        "source_platform": "instagram",
        "source_url": "https://example.com/p/loker-kurir-batam-01",
        "company_name": "PT Logistik Nusantara Batam",
        "company_industry": "Logistik & Pengiriman",
        "company_address": "Kawasan Industri Tunas, Batam",
        "category_name": "Kurir & Pengiriman",
        "location_province": "Kepulauan Riau",
        "location_city": "Batam",
        "location_area": "Batam Center",
        "title": "Kurir Motor Antar Paket",
        "description": "Bertugas mengantarkan paket ke alamat tujuan tepat waktu, menjaga kondisi barang, dan membuat laporan harian.",
        "employment_type": "kontrak",
        "contract_months": 12,
        "quota": 5,
        "gender": "pria",
        "min_age": 19,
        "max_age": 38,
        "min_education": "sma_smk",
        "min_height_cm": 160,
        "fresh_graduate_welcome": True,
        "shift_work": True,
        "salary_type": "pokok_plus_insentif",
        "salary_min": 4600000,
        "salary_max": 6200000,
        "salary_note": "Gaji pokok + insentif per paket",
        "is_free_of_charge": True,
        "status": "published",
        "requirements": [
            {"type": "dokumen", "description": "SIM C aktif & STNK motor pribadi", "is_mandatory": True, "sort_order": 1},
            {"type": "aset", "description": "Memiliki HP Android RAM min 4GB", "is_mandatory": True, "sort_order": 2},
        ],
        "benefits": [
            {"benefit_name": "BPJS Kesehatan", "benefit_slug": "bpjs-kesehatan", "note": "Setelah masa orientasi"},
            {"benefit_name": "BPJS Ketenagakerjaan", "benefit_slug": "bpjs-ketenagakerjaan", "note": None},
        ],
        "apply_channels": [
            {"channel": "whatsapp", "value": "081270001111", "schedule_note": "Senin-Jumat 08.00-16.00 WIB", "sort_order": 1},
        ],
    },
    {
        "source_platform": "facebook",
        "source_url": "https://example.com/fb/loker-kurir-batam-01-dup",
        "company_name": "PT Logistik Nusantara Batam",
        "company_industry": "Logistik & Pengiriman",
        "company_address": "Kawasan Industri Tunas, Batam",
        "category_name": "Kurir & Pengiriman",
        "location_province": "Kepulauan Riau",
        "location_city": "Batam",
        "location_area": "Batam Center",
        "title": "Kurir Motor Antar Paket",
        "description": "Bertugas mengantarkan paket ke alamat tujuan tepat waktu, menjaga kondisi barang, dan membuat laporan harian.",
        "employment_type": "kontrak",
        "contract_months": 12,
        "quota": 5,
        "gender": "pria",
        "min_age": 19,
        "max_age": 38,
        "min_education": "sma_smk",
        "fresh_graduate_welcome": True,
        "shift_work": True,
        "salary_type": "pokok_plus_insentif",
        "salary_min": 4600000,
        "salary_max": 6200000,
        "salary_note": "Gaji pokok + insentif per paket",
        "is_free_of_charge": True,
        "status": "published",
        "requirements": [],
        "benefits": [],
        "apply_channels": [
            {"channel": "whatsapp", "value": "081270001111", "schedule_note": None, "sort_order": 1},
        ],
    },
    {
        "source_platform": "tiktok",
        "source_url": "https://example.com/tt/loker-gudang-redflag",
        "company_name": "Agen Penyalur Cepat",
        "company_industry": "Gudang",
        "location_province": "Jawa Barat",
        "location_city": "Bekasi",
        "title": "Staff Gudang Cepat Masuk",
        "description": "Langsung kerja minggu ini, wajib transfer biaya administrasi dan biaya seragam sebelum interview.",
        "employment_type": "harian",
        "gender": "semua",
        "min_education": "sma_smk",
        "salary_type": "tetap",
        "salary_min": 5500000,
        "salary_max": 5500000,
        "salary_note": "Gaji bulanan",
        "is_free_of_charge": False,
        "status": "draft",
        "requirements": [],
        "benefits": [],
        "apply_channels": [
            {"channel": "whatsapp", "value": "085200009999", "schedule_note": None, "sort_order": 1},
        ],
    },
    {
        "source_platform": "job_portal",
        "source_url": "https://example.com/job/operator-produksi-04",
        "company_name": "PT Karya Manufaktur Sejahtera",
        "company_industry": "Manufaktur",
        "company_address": "Kawasan Industri Batamindo, Batam",
        "category_name": "Operator Produksi",
        "location_province": "Kepulauan Riau",
        "location_city": "Batam",
        "location_area": "Muka Kuning",
        "title": "Operator Produksi Mesin Press",
        "description": "Mengoperasikan mesin press sesuai SOP, melakukan pengecekan kualitas produk awal, dan menjaga kebersihan area kerja.",
        "employment_type": "kontrak",
        "contract_months": 6,
        "quota": 15,
        "gender": "semua",
        "min_age": 18,
        "max_age": 35,
        "min_education": "sma_smk",
        "min_height_cm": 158,
        "fresh_graduate_welcome": True,
        "shift_work": True,
        "salary_type": "umk",
        "salary_min": 4800000,
        "salary_max": 5200000,
        "salary_note": "Mengacu UMK + tunjangan shift",
        "is_free_of_charge": True,
        "status": "published",
        "requirements": [
            {"type": "fisik", "description": "Sehat jasmani dan tidak buta warna", "is_mandatory": True, "sort_order": 1},
            {"type": "umum", "description": "Bersedia bekerja sistem 3 shift", "is_mandatory": True, "sort_order": 2},
        ],
        "benefits": [
            {"benefit_name": "BPJS Kesehatan", "benefit_slug": "bpjs-kesehatan", "note": None},
            {"benefit_name": "Antar Jemput Karyawan", "benefit_slug": "antar-jemput", "note": "Jalur utama"},
        ],
        "apply_channels": [
            {"channel": "email", "value": "hrd@karyamanufaktur.example.com", "schedule_note": None, "sort_order": 1},
        ],
    },
]


def crawl_dummy_by_keywords(keywords: list[str]) -> list[dict[str, Any]]:
    normalized_keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
    if not normalized_keywords:
        return DUMMY_POSTS

    matched: list[dict[str, Any]] = []
    for post in DUMMY_POSTS:
        haystack = " ".join(
            [
                str(post.get("title") or ""),
                str(post.get("description") or ""),
                str(post.get("category_name") or ""),
                str(post.get("company_industry") or ""),
            ]
        ).lower()

        if any(kw in haystack for kw in normalized_keywords):
            matched.append(post)

    return matched


def fetch_dynamic_page_html(
    url: str,
    wait_ms: int = 2000,
    browser_channel: str | None = None,
) -> str:
    """Ambil HTML halaman yang di-render JavaScript menggunakan Playwright."""
    launch_kwargs: dict[str, Any] = {"headless": True}
    if browser_channel:
        launch_kwargs["channel"] = browser_channel

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(wait_ms)
        html = page.content()
        browser.close()
    return html


def fetch_telegram_public_channel(
    channel_username: str,
    keyword: str,
    timeout: int = 15,
) -> list[dict[str, Any]]:
    """Ambil postingan dari channel Telegram publik via pratinjau web t.me/s/<channel>."""
    clean_user = channel_username.strip().lstrip("@")
    url = f"https://t.me/s/{clean_user}?q={quote(keyword)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items: list[dict[str, Any]] = []

    for msg in soup.select(".tgme_widget_message"):
        text_el = msg.select_one(".tgme_widget_message_text")
        link_el = msg.select_one("a.tgme_widget_message_date")
        if not text_el:
            continue

        text_content = text_el.get_text("\n", strip=True)
        if keyword.lower() not in text_content.lower():
            continue

        first_line = text_content.splitlines()[0] if text_content.splitlines() else f"Lowongan {keyword}"
        post_url = link_el.get("href") if link_el else url

        items.append(
            {
                "source_platform": "telegram",
                "source_url": post_url,
                "company_name": None,
                "location_city": None,
                "title": first_line[:120],
                "description": text_content,
                "status": "published",
                "requirements": [],
                "benefits": [],
                "apply_channels": [],
            }
        )

    return items


def crawl_by_keywords(
    keywords: list[str],
    mode: str = "dummy",
    telegram_channels: list[str] | None = None,
) -> list[dict[str, Any]]:
    if mode == "dummy":
        return crawl_dummy_by_keywords(keywords)

    results: list[dict[str, Any]] = []
    channels = [ch.strip() for ch in (telegram_channels or []) if ch.strip()]

    for kw in keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue
        for ch in channels:
            try:
                results.extend(fetch_telegram_public_channel(ch, kw_clean))
            except requests.RequestException:
                continue

    return results