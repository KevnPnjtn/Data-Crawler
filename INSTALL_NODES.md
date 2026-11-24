Install notes
This starter kit is designed to be merged into the existing Myrobin-Crawler project. It is not a replacement repository.
1. Copy AGENTS.md into the project root.
2. Copy src/AGENTS.md into the existing src/ directory.
3. Copy tests/AGENTS.md when creating or using the tests/ directory.
4. Merge .gitignore.append.txt into the existing .gitignore. Do not overwrite existing rules.
5. Merge .env.example with the existing .env.example if it already exists. Never copy real secrets into the example file.
6. Copy config/sources.example.json to config/sources.json only if there is no existing source configuration and after reviewing its defaults.
7. Copy config/ocr_config.example.json to config/ocr_config.json only if there is no existing OCR configuration and after reviewing engine compatibility.
8. Add the docs/ files without replacing existing documentation.
9. Send CODEX_FIRST_TASK.md to Codex so it can audit and merge the guidance safely.
Do not replace config/keywords.json, config/schema_columns.json, requirements.txt, main.py, or existing src/ modules with files from this kit.