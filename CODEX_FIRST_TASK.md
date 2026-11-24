First Codex Task — Audit and Install Project Guidance
Work in the existing Myrobin-Crawler repository. Do not create a new project.
Context
The repository is an existing Python CLI project with a .venv, requirements.txt, main.py, src/crawler.py, src/exporter.py, src/pg_loader.py, src/quality.py, config/keywords.json, and config/schema_columns.json (verify each item before relying on it).

The intended product is a modular multi-source job vacancy collection tool with permitted website crawling, Telegram integrations through authorized Bot API or MTProto access, Instagram through supported official API capabilities, manual image input, OCR, structured extraction, validation, human review, and CSV output. Glints remains manual import unless suitable authorization for automated collection is obtained.
Instructions
1. Audit the current repository, Python version, requirements, CLI, data contract, and existing modules.
2. Read the supplied root AGENTS.md before editing.
3. Add the supplied src/AGENTS.md and tests/AGENTS.md in their matching locations if those directories exist or are created.
4. Merge .gitignore.append.txt into the existing .gitignore; do not overwrite existing ignore rules. Check that .env, browser profiles, Telegram sessions, raw source files, and generated releases are protected.
5. If .env.example already exists, merge the supplied variable names without deleting existing entries. Do not replace it blindly.
6. Copy config/sources.example.json and config/ocr_config.example.json to active config files only after inspecting existing config conventions. Do not overwrite existing configuration.
7. Do not modify keywords.json or schema_columns.json during this setup task.
8. Do not install OCR or social-media dependencies yet.
9. Do not call live APIs or websites.
10. Do not modify the existing crawler, exporter, OCR, or database code in this task.
Deliverables
- A concise audit report of the current repository.
- Guidance files installed without overwriting existing project files.
- A list of merged configuration and ignore rules.
- A list of files intentionally left unchanged.
- Recommended next implementation step, starting with a small local-image OCR proof of concept after dependency compatibility is assessed.
Stop after the audit and safe project-guidance setup. Do not implement the full PRD in this task.