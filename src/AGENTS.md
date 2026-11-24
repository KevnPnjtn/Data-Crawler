src/AGENTS.md — Source and Processing Modules
These instructions apply to Python modules under src/.
Module boundaries
- sources/ or source-specific modules collect permitted content and return raw source items with provenance.
- crawler.py handles website collection and must retain existing behavior unless explicitly changed.
- image_ingestor.py validates and registers images; it must not perform vacancy classification.
- image_preprocessor.py prepares a working image and must preserve the original.
- ocr_engine.py performs OCR and returns recognized text plus available confidence/geometry metadata. It must not infer missing vacancy fields.
- extractor.py maps text into candidate vacancy fields and must preserve evidence/raw text.
- normalizer.py normalizes values without changing their meaning.
- quality.py validates, flags, and deduplicates; uncertain records should be flagged, not silently discarded.
- review.py supports human correction and approval.
- exporter.py produces the final CSV according to config/schema_columns.json.
- pg_loader.py remains optional and must not load unapproved records.
Reuse existing files and interfaces before creating duplicate modules.
Source adapter rules
Each source item should preserve, where available:
- source platform
- source URL/permalink or platform-specific identifier
- source publication timestamp
- collection timestamp
- original text/caption
- local media path(s)
- source-specific metadata needed for traceability
Do not place secrets in source objects, logs, or exported vacancy fields.

Use documented APIs and authorized access only. Implement timeouts, bounded pagination, rate-limit handling, and actionable errors. Do not bypass authentication, private-channel permissions, anti-bot protections, or API restrictions.

Do not let one source failure terminate unrelated source processing.
OCR and extraction rules
- Keep OCR independent of Telegram, Instagram, and website adapters.
- Preserve the original image and process a working copy.
- Record engine/model metadata where available.
- Keep recognized text and text-region metadata for audit/review.
- Treat confidence as a signal, not proof of correctness.
- Do not invent a company, location, salary, date, requirement, or benefit.
- Keep source-provided category separate from canonical target classification.
- Flag ambiguous extraction for human review.
Data contract rules
Read config/schema_columns.json before changing export behavior. Read config/keywords.json before changing category matching. Do not silently add, remove, rename, or reorder final CSV fields. Internal metadata may be stored separately when it is not part of the approved output schema.
Implementation style
- Follow the existing project's Python style and dependencies.
- Use clear type hints for public functions when consistent with existing code.
- Keep functions small and handle errors explicitly.
- Avoid broad exception swallowing; log actionable context without secrets.
- Avoid unnecessary global state and hidden network calls during module import.
- Keep modules testable without real API credentials.