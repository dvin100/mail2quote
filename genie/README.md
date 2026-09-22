# Genie Space — Insurance Underwriting and Risk Analysis

Exported configuration for the Genie Space that backs the **mail2quote** (email-to-quote)
underwriting demo.

| Field | Value |
|-------|-------|
| Title | Insurance Underwriting and Risk Analysis |
| Space ID | `01f1b67699a5152eb9d9e54d15adbc79` |
| Workspace | https://fevm-dvin100-demos.cloud.databricks.com |
| Warehouse ID | `a5017ad6932bc2d7` |
| Run as | VIEWER |
| Catalog / schema | `dvin100_demos_catalog.email_to_quote` |
| Exported | 2026-09-22 |

## Files

| File | Source endpoint | Contents |
|------|-----------------|----------|
| `space.json` | `GET /api/2.0/data-rooms/{id}` | Space metadata, description, `table_identifiers`, warehouse, suggestion description |
| `space-public-api.json` | `GET /api/2.0/genie/spaces/{id}` | Public Genie API view of the space |
| `instructions.json` | `GET /api/2.0/data-rooms/{id}/instructions` | Curated text instructions ("Notes") — the data model, joins, and value dictionaries |
| `curated-questions.json` | `GET /api/2.0/data-rooms/{id}/curated-questions` | Sample questions shown to users |

> No SQL example queries / trusted-asset queries were configured on this space at export time —
> only sample questions and one text instruction.

## Tables in the space (24)

Entity tables (join on `org_id` → `organizations.org_id`):
`organizations`, `financials`, `employees`, `locations`, `vehicles`, `property_assets`,
`contracts`, `cyber_profiles`, `coverage_requests`, `claims`, `policies`

Pipeline tables (join on `email_id`, ordered):
`pipe_email_received` → `pipe_email_parsed` → `pipe_email_enriched` → `pipe_quote_features`
→ `pipe_quote_risk_scoring` → `pipe_quote_review` → `pipe_quote_creation` → `pipe_pdf_created`
→ `pipe_response_email` → `pipe_completed`

Risk / underwriting tables:
`risk_features`, `risk_scored_accounts`, `lb_underwriter_history`

## Sample questions

1. Distribution of `contract_type` in contracts table
2. Monthly sum of `total_revenue` in financials table
3. What tables are there and how are they connected? Give me a short summary.

## Re-download / refresh

```bash
databricks auth login --host https://fevm-dvin100-demos.cloud.databricks.com --profile fevm-dvin100-demos
ID=01f1b67699a5152eb9d9e54d15adbc79
P=fevm-dvin100-demos
databricks api get "/api/2.0/data-rooms/$ID"                    --profile $P > space.json
databricks api get "/api/2.0/data-rooms/$ID/instructions"       --profile $P > instructions.json
databricks api get "/api/2.0/data-rooms/$ID/curated-questions"  --profile $P > curated-questions.json
databricks api get "/api/2.0/genie/spaces/$ID"                  --profile $P > space-public-api.json
```

## Recreate in another workspace

Use the AI Dev Kit `create_or_update_genie` MCP tool (or the Genie UI) with the
`table_identifiers`, `description`, and `sample_questions` from these files, then paste the
`instructions.json` "Notes" content into the space's **Instructions**. Update the catalog/schema
prefix on the table identifiers to match the target workspace.
