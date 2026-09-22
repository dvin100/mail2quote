# Evidence 1 — End-to-end execution

> **Finding addressed:** "No execution evidence is present anywhere in the submission: no
> notebook output, run log, query result, or captured app response shows the pipeline
> actually processing a request end to end."

## 1.1 The pipeline is live and has processed real traffic

The *Underwriter Ingestion Pipeline* (`648da6b7-4893-4940-b396-5e2cbf1a3a0e`) is a Lakeflow
declarative streaming pipeline, currently **RUNNING**, with a continuous update history
(most recent update `fc1c54b1…` = RUNNING). Row counts at each of its 10 stages
(`data/pipeline_stage_rowcounts.csv`):

| # | Stage table | Rows |
|---|-------------|------|
| 1 | `pipe_email_received`     | 87 |
| 2 | `pipe_email_parsed`       | 87 |
| 3 | `pipe_email_enriched`     | 87 |
| 4 | `pipe_quote_features`     | 87 |
| 5 | `pipe_quote_risk_scoring` | 87 |
| 6 | `pipe_quote_review`       | 87 |
| 7 | `pipe_quote_creation`     | 73 |
| 8 | `pipe_pdf_created`        | 73 |
| 9 | `pipe_response_email`     | 85 |
| 10| `pipe_completed`          | 85 |

87 emails were ingested and parsed; 73 produced a bindable quote + PDF (the remainder were
declined and got a decline response, which is why `pipe_completed` = 85 while
`pipe_quote_creation` = 73). This is a real funnel, not a rubber stamp.

**Underwriting decisions across all processed emails** (`data/pipeline_decision_distribution.csv`):

| decision_tag | count |
|--------------|-------|
| auto-approved | 53 |
| uw-approved   | 20 |
| uw-declined   | 7  |
| auto-declined | 4  |
| uw-info       | 1  |

11 of 85 requests were **declined** — the decisioning logic discriminates.

## 1.2 One request traced through every stage — "Heritage Bistro"

`email_id = 82cef45c-2150-4c0f-be18-019a1c4ec74b`. Both ends of this request are included
as real files: `heritage_bistro_INPUT_email.eml` (inbound) and
`heritage_bistro_OUTPUT_quote.pdf` (generated).

**Stage 1 — Received.** Raw `.eml` picked up from
`/Volumes/dvin100_demos_catalog/email_to_quote/incoming_email/quote_request_0841d28a.eml`
(1,192 bytes): a plain-text request from `betty.thompson@heritagebistro.com` for a
commercial cyber-liability quote, food-service business, est. 1980, revenue $550,575,
6 employees, clean 5-year loss history.

**Stage 2 — Parsed (LLM).** A foundation-model call extracted structured fields from the
free-text email. The stored `llm_response` returns clean JSON:
`business_name=Heritage Bistro`, `naics_code=311812`, `risk_category=food_service`,
`annual_revenue=550575.0`, `num_employees=6`, `cyber_limit_requested=1000000.0`,
`num_claims_5yr=0`, `has_safety_procedures=true`.

**Stage 3 — Enriched.** Matched to an existing organization
(`matched_org_id=cef5a2b7-8da6-43aa-9b58-b2588e2ff11b`, `is_existing_customer=true`) and
joined to industry benchmarks: `industry_avg_premium≈20,073`, `industry_avg_claims_per_org≈0.75`,
`revenue_vs_industry_pct=1.22`, `claims_vs_industry=-0.75` (below-average claims).

**Stage 4 — Features.** `business_age_years=46`, `payroll_per_employee=53,217`,
`avg_claim_severity=0`, `safety_score=2`, `heuristic_risk_score=3.0`.

**Stage 5 — Risk scoring.** `risk_score=3.0`, `predicted_loss_ratio=0.045`,
`risk_band=Low`, `pricing_action=competitive_rate`, `underwriting_action=auto_quote`,
`scoring_method=heuristic` (see §serving note in Evidence 2).

**Stage 6 — Review.** `decision_tag=auto-approved` with an AI-written rationale:
> "Heritage Bistro was auto-approved due to its exceptionally low risk profile, with a risk
> score of 3.0/100 and a predicted loss ratio of just 0.05. … a perfect five-year claims
> history showing zero incidents and zero losses."

**Stage 7 — Quote creation.** `quote_number=QT-20260410-82cef45c`,
`risk_mult=0.85`, `industry_mult=1.6`, `experience_mod=0.9`, line-item premiums
(bi=584.99, auto=1,700, cyber=2,125, fees=150…), **total_premium=$11,456.98**,
effective 2026-04-24 → 2027-04-24.

**Stage 8 — PDF created.** `pdf_status=generated`,
`pdf_path=/Volumes/dvin100_demos_catalog/email_to_quote/quote_documents/QT-20260410-82cef45c.pdf`
(the file downloaded into this pack as `heritage_bistro_OUTPUT_quote.pdf`).

**Stage 9 — Response email.** A customer-ready reply was composed:
subject `Your Commercial Insurance Quote QT-20260410-82cef45c - Heritage Bistro`, full
approval body quoting the $11,456.98 total.

**Stage 10 — Completed.** `final_status=quote_issued`.

## 1.3 Timing proves real-time end-to-end processing

Per-stage timestamps for the traced request (`data/heritage_bistro_stage_timestamps.csv`):

| Stage | Timestamp (UTC) |
|-------|-----------------|
| Received  | 2026-04-10 02:23:07.023 |
| Parsed    | 2026-04-10 02:23:10.746 |
| Enriched  | 2026-04-10 02:23:44.761 |
| Features  | 2026-04-10 02:23:51.726 |
| Scored    | 2026-04-10 02:23:53.723 |
| Reviewed  | 2026-04-10 02:24:00.488 |
| Quoted    | 2026-04-10 02:24:19.584 |
| PDF       | 2026-04-10 02:24:21.027 |
| Completed | 2026-04-10 02:24:21.027 |

**One inbound email → issued quote PDF + response email in ~74 seconds**, with monotonically
increasing per-stage timestamps — a captured, timestamped run of the pipeline processing a
request end to end.
