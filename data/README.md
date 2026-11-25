# Data

Raw data may be committed; derived data is not. This directory documents what the data is, where it came from, and how to obtain it.

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
data/raw/        original files (may be committed; one copy only)
data/interim/    intermediate cleaned data (not committed)
data/processed/  model-ready data (not committed)
```

## Acquisition

Document the exact steps here, or provide `scripts/download_data.py`. If the data cannot be redistributed, say so explicitly and give the application steps.

## Rules

- Raw data may be committed under `data/raw/`; commit one copy only (archive or extracted files, not both).
- Never commit credentials, personal information, or per-row predictions.
- Record the license, retrieval date, checksum, and attribution before using the data.
- Keep `data/raw/` read-only; write cleaned outputs to `data/interim/` or `data/processed/`.
- GitHub rejects files over 100 MiB and warns above 50 MiB; use Git LFS or an external location for those.
