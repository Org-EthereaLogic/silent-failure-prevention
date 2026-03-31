# Silent Failure Prevention Agent Governance

## Authorized Agent Behavior

All coding agents working in this repository must:

1. Read [README.md](/Users/etherealogic-2/Dev/Databricks/silent-failure-prevention/README.md), [technical-approach.md](/Users/etherealogic-2/Dev/Databricks/silent-failure-prevention/docs/technical-approach.md), and `config/kpi_thresholds.json` before proposing or editing code.
2. Treat Chapter 2 as a release-control repository with its own evidence lineage inside the portfolio.
3. Preserve Chapter 2 boundaries. This repo proves local detection of silent distribution degradation and gate-based publication control. It does not prove intake certification, benchmark superiority, or live Databricks execution.
4. Keep drift logic, gate thresholds, provenance behavior, and README claims aligned.
5. Preserve deterministic sample data and the local runner output used as evidence.
6. Use only public, documented methods in this repository. Shannon entropy is allowed here; proprietary UMIF formulas and terminology are prohibited.
7. Keep docs, notebook walkthrough, and CI aligned with executable behavior.

## Claim Scope

- Chapter 2 may validate only the checked-in release-control pattern implemented by `src/stability/`, the gate config, the sample datasets, and the local runner.
- Chapter 2 may not claim production readiness, cross-system drift coverage, or live Databricks proof without separate evidence.
- Missing test, runner, or provenance evidence blocks completion claims.

## Required Control Surfaces

- `src/stability/` is the canonical implementation surface.
- `config/kpi_thresholds.json` is the canonical gate-definition surface.
- `data/sample/` is the canonical demo corpus.
- `docs/`, `notebooks/`, and `.github/workflows/ci.yml` are the canonical explanation and verification surfaces.

## Hard Stops

- No secrets in repository files, docs, notebooks, or sample data.
- No unverifiable KPI, PASS, or readiness claims.
- No changes to docs or tests that obscure the actual runner output.
- No introduction of proprietary UMIF formulas, hidden scoring rules, or protected IP into this public repository.
