# Evidence 5 — System-tables output (independent, platform-recorded proof)

> Captured 2026-09-22 by querying Databricks `system.*` tables — records the platform itself
> writes, independent of the app. Raw exports in [`logs/`](logs/).

## 5.1 Billing — real DBU consumption per component → [`logs/system_billing_usage.csv`](logs/system_billing_usage.csv)

`system.billing.usage`, last 14 days, filtered to this demo's pipeline / app / endpoint / warehouse:

| billing_origin_product | resource | total_dbus | usage_records | first_day | last_day |
|---|---|---|---|---|---|
| DLT | `<pipeline-id>` (Underwriter Ingestion Pipeline) | **1787.81** | 2276 | 2026-09-09 | 2026-09-22 |
| APPS | `mail2quote` | **160.99** | 323 | 2026-09-09 | 2026-09-22 |
| SQL | `<genie-warehouse-id>` (Genie) | **150.12** | 18 | 2026-09-09 | 2026-09-19 |
| AI_FUNCTIONS | `databricks-ai-extract` | 2.94 | 4 | 2026-09-09 | 2026-09-17 |
| AI_FUNCTIONS | `databricks-ai-parse-document` | 0.98 | 12 | 2026-09-09 | 2026-09-17 |

Every layer of the app consumed metered compute over two weeks: the **streaming pipeline**
(DLT), the **front-end app** (APPS), the **Genie** SQL warehouse, and the **AI functions**
(`ai_extract` / `ai_parse_document`) that parse the inbound emails — confirming the LLM
parsing stage actually executed, not just exists in code.

## 5.2 Pipeline runs → [`logs/system_pipeline_update_timeline.csv`](logs/system_pipeline_update_timeline.csv)

`system.lakeflow.pipeline_update_timeline` — the pipeline has run continuously as a streaming
REFRESH for two weeks (newest rows):

| update_id | update_type | trigger_type | start_time | end_time |
|---|---|---|---|---|
| fc1c54b1… | REFRESH | SERVICE_UPGRADE | 2026-09-22 13:00:00 | 2026-09-22 14:00:00 |
| fc1c54b1… | REFRESH | SERVICE_UPGRADE | 2026-09-21 21:01:26 | 2026-09-21 22:00:00 |
| 51c32152… | REFRESH | INFRASTRUCTURE_MAINTENANCE | 2026-09-19 05:00:00 | 2026-09-20 10:00:00 |

(full history back to 2026-09-09 in the CSV)

## 5.3 Deployed app

`databricks apps get mail2quote`:
- **state:** `ACTIVE`
- **active_deployment:** `SUCCEEDED`
- **url:** `<app-url>` (Databricks Apps)
- **creator:** underwriting-admin (service account)

## 5.4 Model serving endpoint

`system.serving.endpoint_usage` for `email-to-quote-risk-scorer` had not yet flushed the
just-issued test invocations at capture time (this system table ingests on a delay). The live
prediction calls and their responses are captured directly in
[`logs/model_predictions.json`](logs/model_predictions.json) (Evidence 4.2), and the endpoint
state is `READY`.
