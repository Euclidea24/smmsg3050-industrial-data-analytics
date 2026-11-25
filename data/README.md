# Data

Raw and processed data are **not committed**. This directory documents what the data is, where it came from, and how to obtain it.

## Dataset card

| Field | Value |
|---|---|
| Dataset name | TBD |
| Source / URL | TBD |
| License / terms | TBD |
| Retrieval date | TBD |
| Version / checksum | TBD |
| Size (rows × columns) | TBD |
| Target column | TBD |
| Unit of analysis | TBD |
| Known issues | TBD |

## Placement

```text
data/raw/        original files, read-only
data/interim/    intermediate cleaned data
data/processed/  model-ready data
```

## Acquisition

Document the exact steps here, or provide `scripts/download_data.py`. If the data cannot be redistributed, say so explicitly and give the application steps.

## Rules

- Never commit raw data, credentials, or personal information.
- Record the license and retrieval date before using the data.
- Keep `data/raw/` read-only; write cleaned outputs to `data/interim/` or `data/processed/`.
