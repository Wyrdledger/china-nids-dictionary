# 2026-06-03-01 Initial Dictionary Project

## Summary

Create an independent lightweight data repository for China's notifiable infectious diseases dictionary. Use CSV/JSON files for downstream R/Python access and Git tags for reproducible version pinning.

## Key Changes

- Add current and historical dictionary CSV files plus a generated JSON mirror.
- Add schema documentation and source references.
- Add base R and standard-library Python reader examples.
- Add validation tests for row counts, class counts, dates, current/history consistency, JSON consistency, and reader smoke tests.

## Test Plan

- Run `python -m unittest discover -s tests`.
- Run `Rscript tests/r_smoke_test.R`.

## Assumptions

- The first version is a current baseline, not a full retrospective legal history.
- The repository is intended to be public on GitHub under `Wyrdledger/china-nids-dictionary`.
- Formal reproducible analysis should pin a Git tag such as `v2026.04.01`.
