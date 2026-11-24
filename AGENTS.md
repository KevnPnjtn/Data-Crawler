AGENTS.md — MyRobin Crawler
1. Project purpose
MyRobin Crawler is an existing Python CLI project for collecting Indonesian job-vacancy information from permitted sources, extracting structured fields from text and images, validating records, and producing CSV files for a mentor-provided PostgreSQL database.

Initial target categories:
- Operator Produksi
- Kurir / Delivery Driver
- Helper Gudang
- Security / Satpam
- Cleaning Service
The intended source channels are:
- Permitted public website pages.
- Telegram through an authorized Bot API or Client API integration.
- Instagram only through supported, authorized Meta/Instagram API capabilities.
- Manually supplied text, images, screenshots, and CSV records.
- Glints manual import; do not add automated Glints scraping without appropriate written authorization.
2. Existing repository — inspect before changing
The repository already contains or is expected to contain:
- main.py
- src/crawler.py
- src/exporter.py
- src/quality.py
- src/pg_loader.py
- config/keywords.json
- config/schema_columns.json
- data/raw/
- data/released/
- data/logs/
- .env and .env.example
- requirements.txt
These files may already contain working behavior and project-specific decisions. Inspect them before editing. Do not replace, regenerate, or overwrite them merely to match an example structure.
3. Highest-priority engineering rules
1. Preserve existing functionality unless a requested change requires otherwise.
2. Work incrementally. Follow the roadmap and implement only the currently requested phase.
3. Start substantial work with a repository audit when the current state is unclear.
4. Keep the application CLI-based. Do not add a web dashboard unless explicitly requested.
5. Keep CSV as the only final release/export format. Internal JSON metadata, logs, and review state are allowed; they are not final vacancy exports.
6. config/schema_columns.json is the source of truth for final CSV column names and order. Read it before changing the exporter.
7. config/keywords.json is the source of truth for target categories and keyword aliases. Read it before changing classification logic.
8. Do not invent missing vacancy information. Unknown values must remain null/empty according to the existing data contract.
9. Preserve original source text, original job title, source platform, and source URL wherever available.
10. Keep source adapters separate from OCR, normalization, quality checking, review, and export.
11. Do not add database columns, enum values, or migrations based only on assumptions or an ERD screenshot.
12. Do not load unreviewed OCR records into PostgreSQL.
13. Do not claim a live source integration works unless it has been tested using authorized access and actual returned data.
4. Architecture principles
Use a modular pipeline:

source connector -> raw source item -> text/OCR extraction -> normalization -> classification -> quality checks -> deduplication -> human review -> CSV release -> optional PostgreSQL load

Source connectors should collect content and preserve provenance. They should not contain source-specific field extraction logic that is duplicated across the project.

OCR must be independent of the source connector. The same OCR pipeline should work with Telegram images, permitted Instagram media, website images, and manually supplied images.

Prefer small, typed, testable functions and clear data structures. Reuse existing modules where they already provide equivalent functionality. Avoid unnecessary abstraction and premature framework additions.
5. Data and extraction rules
- Preserve the original title and company name.
- Keep source-provided category separate from the project's canonical target category.
- Distinguish company address from job location.
- Distinguish recruiter/contact identity from company identity.
- Distinguish skills mentioned in a post from mandatory requirements.
- Parse salary bounds only when supported by the source text.
- Do not infer publication date, deadline, employment type, gender, age, or other requirements without evidence.
- Retain raw OCR text and useful OCR metadata for traceability.
- If multiple vacancies appear in one image/post, do not merge them into one record unless the source clearly presents one combined vacancy.
- Flag ambiguous values for manual review rather than guessing.
6. Source access, API, and privacy rules
- Follow applicable source terms, API policies, permission scopes, and access restrictions.
- Respect robots.txt where applicable to website crawling.
- Do not access private channels, private groups, protected pages, or accounts without authorization.
- Do not bypass login, anti-bot controls, rate limits, or API permissions.
- Do not use undocumented/private APIs.
- Telegram Bot API can only receive content made available to the bot. Do not assume it can read every public channel.
- Telegram Client API/MTProto requires an authorized account/session and permitted channel access.
- Instagram integration must use documented, currently supported API access. Do not use browser session scraping as a workaround for unavailable API access.
- Manual image import is the fallback when automated collection is unavailable or not permitted.
- Do not collect candidate data or recruiter personal information unless clearly necessary, authorized, and explicitly in scope.
- Add bounded requests, appropriate delays, pagination limits, and clear error reporting to network collectors.
7. Credentials and local data protection
- Read secrets from environment variables; never hardcode tokens, passwords, session strings, or API secrets.
- Never print secrets or full authorization headers in logs.
- Keep .env, Telegram session files, browser profiles, and private source material out of Git.
- Treat .playwright_ig_profile/ as sensitive authentication state. Do not inspect or reuse it to bypass platform restrictions.
- Preserve original source images. Preprocessing must operate on a copy or temporary representation.
- Do not delete raw data, released CSVs, logs, or existing project files unless explicitly asked.
8. Dependencies and environment
The project is developed on Windows and already has a .venv and requirements.txt.

Before installing or upgrading dependencies:
1. Inspect the current Python version.
2. Inspect requirements.txt and installed packages.
3. Check compatibility with the existing environment.
4. Explain large downloads or GPU/runtime requirements before proceeding.
5. Prefer one OCR engine for the initial implementation; do not install multiple OCR engines without a demonstrated need.
Do not upgrade all packages or recreate .venv as a default troubleshooting step.
9. Testing and verification
- Prefer deterministic unit tests with mocked HTTP/API/OCR responses.
- Unit tests must not require real API credentials or live network access.
- Use synthetic fixtures and clearly label them as synthetic.
- Never present synthetic fixtures as actual job vacancies.
- Use temporary directories for test outputs; do not modify the user's real data/raw or data/released files during tests.
- Add tests for failure paths as well as successful paths.
- Report exact commands and actual outcomes. Do not claim tests passed unless they were run.
- Keep live smoke tests bounded and use only authorized sources.
10. Windows development conventions
Provide commands compatible with PowerShell unless the user requests another shell.

Typical existing-environment workflow:
.\.venv\Scripts\Activate.ps1
python --version
python main.py --help
Do not assume command names or CLI subcommands before inspecting main.py.
11. Current implementation priority
Unless the user explicitly chooses another task, follow this sequence:
1. Audit the current repository and dependencies.
2. Establish a working local-image OCR foundation.
3. Implement structured field extraction and review.
4. Add Telegram integration using the authorized mode selected by the user.
5. Add Instagram integration only for endpoints and permissions actually available.
6. Improve permitted website collection and manual imports.
7. Integrate the unified CSV release and only then verify optional PostgreSQL loading.
Do not implement the entire roadmap in one uncontrolled change. After each milestone, report files changed, commands run, test results, limitations, and the next recommended step.