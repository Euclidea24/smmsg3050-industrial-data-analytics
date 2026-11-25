# SMMG3050 Industrial Data Analytics — Course Project

**Course:** SMMG3050 Industrial Data Analytics, HKUST(GZ), Fall 2026 · course project (25% of the final grade)  
**Deliverables:** Project report and group presentation  
**Hard deadline:** 2026-12-04 (project presentation on 2026-12-03; late submissions score zero under the course policy)<br>
**Status:** Topic and dataset under selection — see [`docs/00-topic-selection.md`](docs/00-topic-selection.md)  
**Stack:** To be fixed after the dataset is locked

[中文版](README.zh-CN.md)

## Overview

This repository holds the code, experiment records, figures, report source, and slides for our SMMG3050 course project.

The project is an end-to-end industrial data analytics study: frame a problem with clear industrial relevance, prepare the data, build and compare models, evaluate them honestly, and explain what the results mean and where they stop being trustworthy.

The topic is not fixed yet. The course allows a problem built on a public dataset (Kaggle, Tianchi, or another public source) or a self-defined industrial problem. We will lock the dataset before modeling starts and record the rationale in [`docs/00-topic-selection.md`](docs/00-topic-selection.md).

## Repository layout

```text
.
├── configs/            # experiment configs (YAML/JSON), one file per experiment
├── data/
│   ├── raw/            # original data, never committed
│   ├── interim/        # intermediate cleaned data, never committed
│   └── processed/      # model-ready data, never committed
├── docs/               # rubric-aligned write-ups and planning notes
├── figures/            # exported figures used in the report and slides
├── literature/         # midterm papers, notes, and method-transfer evaluation
├── notebooks/          # exploration, numbered 01_, 02_, ...
├── reports/            # report source and presentation source
├── scripts/            # entry points: download data, run experiments
├── src/                # reusable code imported by notebooks and scripts
├── requirements.txt
└── README.md
```

Rules of thumb: notebooks are for exploration; anything reused goes into `src/`; anything that produces a reported number goes through `scripts/` + `configs/`, so the number can be regenerated.

## Quick start

The environment is intentionally not locked yet. Once the dataset and stack are fixed:

1. Create and activate a virtual environment.
2. Add exact versions to `requirements.txt`.
3. Record the exact setup commands in this section.

```bash
git clone git@github.com:Euclidea24/smmsg3050-industrial-data-analytics.git
cd smmsg3050-industrial-data-analytics

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Do not add unpinned dependencies. If a package is needed for exploration only, keep it out of the shared environment or pin it as well.

## How the work maps to the grading rubric

| Rubric item | Points | Where it is addressed | Owner |
|---|---:|---|---|
| Problem statement | 6 | `docs/01-problem-statement.md`, report §1 | TBD |
| Data preprocessing | 4 | `docs/02-data-preprocessing.md`, report §3 | TBD |
| Modeling | 6 | `docs/03-modeling.md`, report §4 | TBD |
| Model selection | 3 | `docs/03-modeling.md` § selection, report §4.4 | TBD |
| Evaluation | 6 | `docs/04-evaluation.md`, report §5 | TBD |
| Interpret the results | 5 | `docs/05-interpretation.md`, report §6 | TBD |
| Accuracy | 20 | Every reported number traceable to a committed script, config, and log | All |
| Relevance | 20 | Industrial framing and implications, throughout | TBD |
| Writing quality | 15 | `docs/06-report-outline.md`, final report | TBD |
| Presentation | 15 | `docs/07-presentation-outline.md`, slides | TBD |
| Participation bonus | +4 | Insightful questions during other groups' talks | All |

Accuracy is not a separate section: it is the requirement that every claim in the report can be reproduced from this repository. If a number cannot be regenerated from a committed script and config, it does not belong in the report.

## Topic and dataset selection

Decision record: [`docs/00-topic-selection.md`](docs/00-topic-selection.md). Candidates are screened on:

1. **Industrial relevance** — a real process, asset, product, or operation, not a generic ML benchmark with an industrial label attached.
2. **Access and license** — the data is legally obtainable and we can publish code without redistributing restricted data.
3. **Label quality and leakage risk** — the target is measured, not trivially derived from other columns.
4. **Feasibility** — a meaningful baseline must run within the first day, and the full pipeline must fit before 11-28.
5. **Interpretability** — the result can be explained to a non-ML audience.
6. **Reproducibility** — a teammate or the TA can obtain the same data and rerun the pipeline.

## Data rules

- Raw data may be committed under `data/raw/`; commit one copy only (archive or extracted files, not both). Derived data and personal information are not committed.
- Credentials are never committed.
- Record dataset name, source URL, license, retrieval date, checksum, and attribution in [`data/README.md`](data/README.md).
- Split the data once, before any preprocessing that learns parameters (imputers, scalers, encoders, feature selection). Fit on training data only.
- Do not inspect the test set until the final model is frozen. Report how many times the test set was evaluated.
- Keep `data/raw/` read-only; write cleaned data to `data/interim/` or `data/processed/`.

## Reproducibility

- Every figure and table in the report must be regenerated by a committed script and config.
- Fix random seeds and record them in the config.
- Record the Python version, package versions, and hardware in [`docs/08-reproducibility.md`](docs/08-reproducibility.md).
- The target is one command that reproduces the final result from raw data.

## Collaboration workflow

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full workflow.
- Open a PR for every change; authors do not merge into `main`.
- No teammate review is required. The rotating integrator merges the open PRs.
- Every day before 22:00, the integrator writes the summary in [`docs/VERSIONS.md`](docs/VERSIONS.md) and tags `v0.x`. This is a rollback point, not an approval gate.
- Never force-push `main` or overwrite a teammate's work.
- Keep pull requests small and scoped; do not mix data, code, and report changes in one PR.
- Use issues for tasks. Suggested labels: `data`, `model`, `eval`, `report`, `slides`, `blocked`.
- Decisions belong in the repository (issue, PR, or the relevant `docs/` file), not only in chat.
- Do not rewrite a teammate's section without asking; comment in the PR instead.

## AI use and academic integrity

- The course permits AI assistance for the project only, not for homework or exams.
- Log every tool and model used, and what it contributed, in [`docs/09-ai-usage-log.md`](docs/09-ai-usage-log.md).
- Verify all generated code by reading and running it. Every member must be able to explain the submitted work.
- Never fabricate citations, dataset statistics, or results. If a number was not produced by a committed script, it does not go in the report.
- Do not paste licensed or confidential data into external services.

## Suggested schedule

| Date | Milestone | Output |
|---|---|---|
| 11-25 | Repository scaffold; dataset vote (v001-11252149) | README, `docs/summaries/v001-11252149.md` |
| 11-26 | Lock topic and problem statement | `docs/00`, `docs/01` |
| 11-27–11-30 | Data audit, preprocessing, baselines | notebooks, baseline |
| 12-01–12-02 | Modeling, model selection, evaluation, interpretation | `docs/03-05`, figures |
| 12-03 | Project presentation | slides |
| 12-04 | Final report, code, submission | report PDF, code |

Submit by the morning of 12-04, not at 23:59. Leave a buffer for upload and last-minute format fixes.

## Submission checklist

- [ ] Topic and dataset justified; industrial relevance explicit.
- [ ] Data card complete: source, license, size, splits.
- [ ] Preprocessing reproducible; no leakage.
- [ ] At least one strong baseline and one tuned model compared.
- [ ] Model selection justified with validation evidence.
- [ ] Metrics reported with uncertainty and per-segment analysis.
- [ ] Results interpreted, with limitations stated.
- [ ] Report proofread; figures and tables numbered and referenced.
- [ ] Slides fit 11 + 4 minutes (3 members) or 15 + 5 minutes (4 members).
- [ ] AI usage log complete.
- [ ] Clean-machine reproduction attempted, or the gap documented.

## Team

| Name | GitHub | Primary responsibility |
|---|---|---|
| TBD | @Euclidea24 | TBD |
| TBD | | TBD |
| TBD | | TBD |
| TBD | | TBD |
