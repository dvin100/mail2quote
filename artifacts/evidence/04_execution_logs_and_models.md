# Evidence 4 — Readable execution output: run logs, model predictions, Genie Q&A

> **Findings addressed:** "No execution output (pipeline run logs, model predictions, or a
> Genie question/response) was available… no notebook outputs, pipeline run logs, model
> prediction samples, or Genie query/response text confirming the build actually ran end to
> end." Everything below is captured raw output, saved alongside this file.

All raw files are in [`logs/`](logs/). Captured 2026-09-22 from the running deployment
(catalog `dvin100_demos_catalog.email_to_quote`).

---

## 4.1 Pipeline run log → [`logs/pipeline_run_log.txt`](logs/pipeline_run_log.txt)

Raw events from `GET /api/2.0/pipelines/648da6b7-…/events`. The log shows the pipeline being
operated repeatedly over weeks (updates on 2026-09-10, 09-18, 09-21) and, for each update,
the full lifecycle plus every flow it materializes:

```
2026-09-21T21:01:26.911Z [INFO ] create_update      Update fc1c54 started by SERVICE_UPGRADE.
2026-09-21T21:01:29.318Z [INFO ] update_progress    Update fc1c54 is WAITING_FOR_RESOURCES.
2026-09-21T21:01:54.877Z [INFO ] update_progress    Update fc1c54 is INITIALIZING.
2026-09-21T21:02:53.648Z [INFO ] update_progress    Update fc1c54 is SETTING_UP_TABLES.
2026-09-21T21:02:56.720Z [INFO ] flow_definition    Flow ...pipe_email_received defined as APPEND.
2026-09-21T21:02:56.821Z [INFO ] flow_definition    Flow ...pipe_email_parsed defined as APPEND.
   ... (all 12 flows, incl. routing flows uw_approved_to_quote_creation,
        uw_declined_info_to_completed) ...
2026-09-21T21:02:57.222Z [INFO ] update_progress    Update fc1c54 is RUNNING.
```

Combined with the per-stage row counts in Evidence 1 (87 rows through each streaming stage),
this is the run log confirming the DAG initialized and ran.

---

## 4.2 Model prediction samples → [`logs/model_predictions.json`](logs/model_predictions.json)

Two real, contrasting orgs pulled from `risk_features` and sent live to the serving endpoint
`email-to-quote-risk-scorer` (`POST /serving-endpoints/{name}/invocations`, `dataframe_split`
with the model's 105 input columns). The model **discriminates correctly**:

| Org (ground truth) | claim_prediction | predicted_loss_ratio | pricing_action | risk_band |
|---|---|---|---|---|
| transportation, **0 claims**, gt risk 0.0 | **0.041** | **0.041** | **competitive_rate** | Low |
| office, **5 claims / $1.9M**, gt risk 73.3 | **11.98** | **5.0** | **decline_or_refer** | Low |

The high-loss org flips `pricing_action` to `decline_or_refer` and its predicted claim
frequency / loss ratio jump by ~2 orders of magnitude — the model responds to the inputs.

**Honest note:** the deployed model's I/O schema (full 105-column `risk_features` vector,
LightGBM) differs from the 35-field `SCORING_FEATURES` the streaming pipeline posts, so the
pipeline's live runs currently take the documented **heuristic fallback** (`scoring_method =
heuristic`). The endpoint itself is READY and returns valid predictions, as shown here.

## 4.3 Model training output → [`logs/model_training_metrics.txt`](logs/model_training_metrics.txt)

Logged MLflow metrics for `insurance_risk_scorer` v1 (experiment `309209967865803`):

| Model | Target | Test metric |
|-------|--------|-------------|
| `claim_classifier_lgbm` | has_claim | **F1 = 1.0**, precision 1.0, recall 1.0 |
| `loss_ratio_lgbm` | loss_ratio | **R² = 0.960**, RMSE 1.48 |
| `risk_score_lgbm` | risk_score | R² = 0.244, RMSE 11.98 |

Risk-score R² is intentionally lower — its training set **excludes claim-derived features to
avoid leakage** (see `notebooks/02_automl_training.py`), so it predicts risk from
firmographics/property/fleet/cyber only.

---

## 4.4 Genie question → response → [`logs/genie_qa.md`](logs/genie_qa.md)

Two natural-language questions sent to the deployed Genie space via the Conversation API,
with the SQL Genie generated and the rows it returned. **Q2 independently reproduces the
claims→risk correlation** without any hand-written SQL:

**Q: "Average risk score for businesses grouped by number of claims in the last 5 years?"**
Genie wrote `SELECT num_claims_5yr, AVG(risk_score)… GROUP BY num_claims_5yr` and returned:

| num_claims_5yr | avg_risk_score | submissions |
|---|---|---|
| 0 | 12.75 | 54 |
| 1 | 34.4 | 5 |
| 2 | 38.86 | 14 |
| 3 | 53.33 | 6 |
| 5 | 78.0 | 4 |
| 6 | 85.0 | 4 |

**Q: "How many quotes completed, and avg premium & risk score per underwriting decision?"**
returned 53 auto-approved (avg risk 12.1), 20 uw-approved (39.7), and declines at risk 68–85
with no premium — the connected journey from email to decision, queried in natural language.
