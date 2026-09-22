# Mail2Quote — Execution Evidence Pack

Evidence captured live from the running deployment on **2026-09-22** to answer three
review findings that the earlier submission lacked verifiable proof. Every figure below
was pulled directly from the workspace, not from documentation or a validator pattern-match.

- **Workspace:** `https://<workspace-host>`
- **Catalog / schema:** `dvin100_demos_catalog.email_to_quote`
- **Streaming pipeline:** *Underwriter Ingestion Pipeline* (`648da6b7-4893-4940-b396-5e2cbf1a3a0e`) — state **RUNNING**
- **ML serving endpoint:** `email-to-quote-risk-scorer` — state **READY**

> Note: the original deployment catalog referenced in `DEPLOY.md`
> (`dvin100_email_to_quote` on `<expired-workspace-host>`) was a FEVM workspace that has since
> expired. The demo now lives at `dvin100_demos_catalog.email_to_quote` on the
> `<workspace-host>` workspace, which is where all evidence here was captured.

## Review finding → evidence map

| # | Review finding | Evidence file |
|---|----------------|---------------|
| 1 | *"No notebook output, run log, query result, or captured app response shows the pipeline actually processing a request end to end."* | [`01_end_to_end_execution_evidence.md`](01_end_to_end_execution_evidence.md) |
| 2 | *"Pipeline, governance, and serving layers were only confirmed through the validator's pattern match; actual pipeline logic, governance rules, and Lakebase schema were not visible."* | [`02_pipeline_governance_lakebase_evidence.md`](02_pipeline_governance_lakebase_evidence.md) |
| 3 | *"No visible evidence of the synthetic data generation logic … unclear whether the underlying risk and claims data is shaped with realistic correlations."* | [`03_synthetic_data_realism_evidence.md`](03_synthetic_data_realism_evidence.md) |

## Files in this pack

**Real end-to-end artifacts (input → output) for one traced request — "Heritage Bistro":**
- `heritage_bistro_INPUT_email.eml` — the raw inbound quote-request email, downloaded from the ingestion Volume
- `heritage_bistro_OUTPUT_quote.pdf` — the generated quote document, downloaded from the quote-documents Volume (2 pages)

**Supporting query exports (`data/`):**
- `pipeline_stage_rowcounts.csv` — row counts at each of the 10 pipeline stages
- `heritage_bistro_stage_timestamps.csv` — per-stage timestamps for the traced request
- `pipeline_decision_distribution.csv` — underwriting decisions across all processed emails
- `synthetic_claims_vs_risk.csv` — claims-history buckets vs. avg risk score / loss ratio
- `synthetic_pearson_correlations.csv` — Pearson correlation coefficients across 10,000 orgs

All queries were run against SQL warehouse `<warehouse-id>` on the workspace above.
