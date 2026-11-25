# 02 · Data and Preprocessing

**Rubric:** Data preprocessing (4 points) · Accuracy (20 points)  
**Owner:** TBD  
**Status:** draft

## Data card

See `data/README.md` for source, license, retrieval date, and checksum.

| Item | Value |
|---|---|
| Raw rows × columns | |
| Time span | |
| Target distribution | |
| Missing cells | |
| Duplicate rows | |
| Train / validation / test sizes | |

## Quality audit

| Issue | Finding | Treatment | Rationale |
|---|---|---|---|
| Missing values | | | |
| Duplicates | | | |
| Outliers | | | |
| Inconsistent categories | | | |
| Time or group leakage | | | |
| Target leakage | | | |

## Split strategy

- Split type (random / temporal / group):
- Ratios:
- Why this split matches the deployment setting:
- Test set locked at:

## Preprocessing pipeline

| Step | Fit on | Applied to | Reason |
|---|---|---|---|
| | train only | train / val / test | |

## Leakage checklist

- [ ] Imputers, scalers, encoders, and feature selectors are fit on training data only.
- [ ] No target-derived feature is available at prediction time.
- [ ] Temporal order is respected for time-dependent data.
- [ ] The test set was not inspected before the final model was frozen.
- [ ] Group structure (if any) does not cross splits.

## Reproducibility

- Script:
- Config:
- Seed:
- Runtime:
- Output row counts:
