# Versions

Every day before 22:00 (Beijing), the rotating integrator merges the day's PRs into `main`, writes a summary, and tags a major version. The tag is a rollback point, not an approval gate.

Authors open PRs; the integrator is the only one who merges them. If a PR is urgent, the integrator can merge it earlier, but there is at least one consolidation per day.

| Tag | Date | Integrator | Dataset | Best result | Blockers | Next step |
|---|---|---|---|---|---|---|
| v0.1 | 2026-11-25 | | | | | |
| v0.2 | 2026-11-26 | | | | | |
| v0.3 | 2026-11-27 | | | | | |
| v1.0 | 2026-11-28 | | | | | |

## Rotation

`Euclidea24 → HapLotes405-1000 → Lzh328-SMMG → Euclidea24`. If someone is absent, the next person takes the slot; note the swap in the table.

## Tagging

```bash
git tag -a v0.1 -m "Daily summary: <one line>"
git push origin v0.1
```

Tag the commit that contains the summary row. Do not move or delete a published tag.
