# Silent Failure Prevention Directives

These directives are enforceable rules for humans and agents working in this repository.

## CRITICAL

- **No placeholders**: do not add TODO, FIXME, TBD, XXX, or template brackets.
- **No secrets**: never commit credentials, tokens, passwords, or private endpoints.
- **No hidden dependencies**: implementation and verification dependencies must be explicit in repo-managed config or docs.
- **No claim inflation**: do not state more than the checked-in runner, tests, and docs prove.
- **No stale docs**: README, notebook, and technical docs must match the current runner behavior and gate config.
- **No destructive artifact mutation**: do not rewrite checked-in sample CSVs or outputs to conceal failures.
- **Public-method discipline**: Shannon entropy and other public, standard methods are allowed. UMIF or other proprietary formulas are prohibited.

## IMPORTANT

- `config/kpi_thresholds.json` is the source of truth for gate thresholds.
- The health score definition in docs and tests must match the implemented mean-of-column-scores behavior.
- Distinguish local demo evidence from any future live Databricks evidence.
- Preserve deterministic sample generation and reproducible runner output.

## RECOMMENDED

- Add tests for any new gate, drift scenario, or provenance field.
- Keep docs business-readable without weakening evidence traceability.

## Verification Commands

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
python -m ruff check src tests
PYTHONPATH=src python -m stability.runners
PYTHONPATH=src python -m stability.sample_data
```
