import logging
import re
from typing import Any
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logger = logging.getLogger("myrobin_crawler")

MAJOR_CITIES = [
    "jakarta", "bogor", "depok", "tangerang", "bekasi", "karawang", "cikarang",
    "bandung", "semarang", "solo", "surakarta", "yogyakarta", "jogja",
    "surabaya", "sidoarjo", "gresik", "malang", "batam", "medan", "palembang",
    "pekanbaru", "padang", "lampung", "makassar", "balikpapan", "samarinda",
    "banjarmasin", "pontianak", "denpasar", "bali",
]

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


def extract_info_from_caption(caption: str) -> dict[str, Any]:
    """Ekstrak kontak WA/email, kota penempatan, dan indikasi gaji dari teks bebas medsos."""
    text_lower = (caption or "").lower()

    apply_channels: list[dict[str, Any]] = []
    wa_matches = re.findall(r"(?:\+62|62|0)8[1-9][0-9\-\s]{7,13}", caption or "")
    seen_contacts: set[str] = set()
    for raw_num in wa_matches:
        clean_num = re.sub(r"[\s\-]", "", raw_num)
        if clean_num not in seen_contacts:
            seen_contacts.add(clean_num)
            apply_channels.append(
                {
                    "channel": "whatsapp",
                    "value": clean_num,
                    "schedule_note": None,
                    "sort_order": len(apply_channels) + 1,
                }
            )

    email_matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", caption or "")
    for email in email_matches:
        if email.lower() not in seen_contacts:
            seen_contacts.add(email.lower())
            apply_channels.append(
                {
                    "channel": "email",
                    "value": email.lower(),
                    "schedule_note": None,
                    "sort_order": len(apply_channels) + 1,
                }
            )

    detected_city = None
    for city in MAJOR_CITIES:
        if re.search(rf"\b{re.escape(city)}\b", text_lower):
            detected_city = city.title()
            break

    salary_min = None
    salary_type = None
    if "umr" in text_lower or "umk" in text_lower:
        salary_type = "umk"

    jt_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:jt|juta)\b", text_lower)
    rp_match = re.search(r"rp\.?\s*(\d{1,2}[.,]\d{3}[.,]\d{3})", text_lower)
    if jt_match:
        val = float(jt_match.group(1).replace(",", "."))
        salary_min = int(val * 1_000_000)
        salary_type = salary_type or "tetap"
    elif rp_match:
        val = int(re.sub(r"[.,]", "", rp_match.group(1)))
        salary_min = val
        salary_type = salary_type or "tetap"

    return {
        "location_city": detected_city,
        "salary_min": salary_min,
        "salary_type": salary_type,
        "apply_channels": apply_channels,
    }


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


def fetch_telegram_public_channel(
    channel_username: str,
    keyword: str,
    timeout: int = 12,
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
        parsed = extract_info_from_caption(text_content)

        items.append(
            {
                "source_platform": "telegram",
                "source_url": post_url,
                "company_name": None,
                "location_city": parsed["location_city"],
                "title": first_line[:120],
                "description": text_content,
                "salary_min": parsed["salary_min"],
                "salary_type": parsed["salary_type"],
                "status": "published",
                "requirements": [],
                "benefits": [],
                "apply_channels": parsed["apply_channels"],
            }
        )

    return items


def fetch_public_job_listings_from_url(
    search_url: str,
    keyword: str,
    source_platform: str = "job_portal",
    max_items: int = 10,
    timeout: int = 12,
) -> list[dict[str, Any]]:
    """
    Fetcher generik untuk halaman daftar loker publik berbasis HTML/teks.
    Sesuaikan CSS selector jika diarahkan ke portal loker tertentu.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(search_url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    candidates = soup.select("article, .job-card, .job-item, .vacancy, li")
    items: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    kw_lower = keyword.lower().strip()

    for el in candidates:
        text_block = " ".join(el.get_text(" ", strip=True).split())
        if len(text_block) < 40 or kw_lower not in text_block.lower():
            continue

        link_el = el.select_one("a[href]")
        href = link_el.get("href", "").strip() if link_el else search_url
        if href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(search_url, href)

        if href in seen_urls:
            continue
        seen_urls.add(href)

        title_el = el.select_one("h1, h2, h3, h4, a")
        title = title_el.get_text(" ", strip=True)[:120] if title_el else text_block[:120]
        parsed = extract_info_from_caption(text_block)

        items.append(
            {
                "source_platform": source_platform,
                "source_url": href,
                "company_name": None,
                "location_city": parsed["location_city"],
                "title": title,
                "description": text_block[:1000],
                "salary_min": parsed["salary_min"],
                "salary_type": parsed["salary_type"],
                "status": "published",
                "requirements": [],
                "benefits": [],
                "apply_channels": parsed["apply_channels"],
            }
        )

        if len(items) >= max_items:
            break

    return items


def fetch_instagram_tag_playwright(
    tag: str,
    max_scrolls: int = 1,
    max_posts: int = 3,
    wait_ms: int = 1500,
    browser_channel: str | None = "msedge",
    user_data_dir: str | None = ".playwright_ig_profile",
    headless: bool = True,
) -> list[dict[str, Any]]:
    """Ambil caption beberapa post teratas dari tag Instagram via Playwright."""
    clean_tag = tag.strip().lstrip("#").lower()
    if not clean_tag:
        return []

    url = f"https://www.instagram.com/explore/tags/{quote(clean_tag)}/"
    posts: list[dict[str, Any]] = []

    with sync_playwright() as p:
        browser = None
        if user_data_dir:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                channel=browser_channel,
            )
            page = context.new_page()
        else:
            launch_kwargs: dict[str, Any] = {"headless": headless}
            if browser_channel:
                launch_kwargs["channel"] = browser_channel
            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context()
            page = context.new_page()

        try:
            logger.info("IG tag #%s: membuka halaman explore...", clean_tag)
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(wait_ms)

            for _ in range(max_scrolls):
                page.mouse.wheel(0, 900)
                page.wait_for_timeout(wait_ms)

            anchors = page.locator("a[href*='/p/'], a[href*='/reel/']").all()
            post_urls: list[str] = []
            seen_hrefs: set[str] = set()

            for a in anchors:
                href = a.get_attribute("href") or ""
                if not href or href in seen_hrefs:
                    continue
                seen_hrefs.add(href)
                full_url = href if href.startswith("http") else f"https://www.instagram.com{href}"
                post_urls.append(full_url)
                if len(post_urls) >= max_posts:
                    break

            logger.info("IG tag #%s: mengambil detail %d post...", clean_tag, len(post_urls))
            for idx, post_url in enumerate(post_urls, start=1):
                try:
                    page.goto(post_url, wait_until="domcontentloaded", timeout=12000)
                    page.wait_for_timeout(wait_ms)

                    body_text = (
                        page.locator("article").first.inner_text(timeout=4000)
                        if page.locator("article").count() > 0
                        else ""
                    )
                    caption_text = "\n".join(
                        line.strip() for line in body_text.splitlines() if line.strip()
                    )
                    if not caption_text:
                        continue

                    parsed = extract_info_from_caption(caption_text)
                    first_line = caption_text.splitlines()[0][:120]

                    posts.append(
                        {
                            "source_platform": "instagram",
                            "source_url": post_url,
                            "company_name": None,
                            "location_city": parsed["location_city"],
                            "title": first_line,
                            "description": caption_text,
                            "salary_min": parsed["salary_min"],
                            "salary_type": parsed["salary_type"],
                            "status": "published",
                            "requirements": [],
                            "benefits": [],
                            "apply_channels": parsed["apply_channels"],
                        }
                    )
                    logger.info("IG tag #%s: post %d/%d berhasil diparse", clean_tag, idx, len(post_urls))
                except Exception as exc:
                    logger.warning("IG tag #%s: lewati post %d (%s)", clean_tag, idx, exc)
                    continue
        finally:
            context.close()
            if browser is not None:
                browser.close()

    return posts


def crawl_by_keywords(
    keywords: list[str],
    mode: str = "dummy",
    telegram_channels: list[str] | None = None,
    instagram_tags: list[str] | None = None,
    ig_user_data_dir: str | None = ".playwright_ig_profile",
    ig_headless: bool = True,
) -> list[dict[str, Any]]:
    if mode == "dummy":
        return crawl_dummy_by_keywords(keywords)

    results: list[dict[str, Any]] = []
    channels = [ch.strip() for ch in (telegram_channels or []) if ch.strip()]
    tags = [t.strip().lstrip("#") for t in (instagram_tags or []) if t.strip()]

    for kw in keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue
        for ch in channels:
            try:
                results.extend(fetch_telegram_public_channel(ch, kw_clean))
            except requests.RequestException as exc:
                logger.warning("Telegram %s gagal untuk '%s': %s", ch, kw_clean, exc)

    for tag in tags:
        try:
            fetched = fetch_instagram_tag_playwright(
                tag=tag,
                user_data_dir=ig_user_data_dir,
                headless=ig_headless,
            )
            if keywords:
                kw_lower = [k.strip().lower() for k in keywords if k.strip()]
                fetched = [
                    item
                    for item in fetched
                    if any(
                        k in f"{item.get('title', '')} {item.get('description', '')}".lower()
                        for k in kw_lower
                    )
                ]
            logger.info("IG tag #%s: %d post cocok keyword", tag, len(fetched))
            results.extend(fetched)
        except Exception as exc:
            logger.warning("IG tag #%s gagal: %s", tag, exc)

    return results