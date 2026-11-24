# MyRobin Crawler

The existing no-argument command continues to run the configured collection flow.

## Local image OCR

Install the optional OCR runtime into the existing virtual environment after reviewing its platform requirements:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ocr.txt
```

The first OCR run may download PaddleOCR model files. Then process a supported image or a directory of images:

```powershell
.\.venv\Scripts\python.exe main.py ocr --input data/raw/manual/images
```

Supported formats are JPG, JPEG, PNG, and WEBP. Original images are preserved. OCR text, regions, confidence, source image SHA-256, and review recommendation are written under `data/interim/ocr/` as internal metadata; they are not vacancy records or release CSVs.
