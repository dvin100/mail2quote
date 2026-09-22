# Notebook & script index (the actual build code)

The reviewer noted the data-generation and pipeline code "was not part of what could be
reviewed directly." It is all in this repo — this index points to each file and shows the
load-bearing excerpts so the logic can be read without a workspace.

| File | What it does |
|------|--------------|
| [`scripts/generate_data.py`](../../scripts/generate_data.py) | Generates the 11-table synthetic insurance book (10,000 orgs) with correlated claims/financials |
| [`scripts/generate_sample_emails.py`](../../scripts/generate_sample_emails.py) | Generates realistic inbound `.eml` quote requests from the org data |
| [`notebooks/01_feature_engineering.py`](../../notebooks/01_feature_engineering.py) | Builds the 117-col `risk_features` table + target labels (risk_score, loss_ratio, has_claim) |
| [`notebooks/02_automl_training.py`](../../notebooks/02_automl_training.py) | Trains LightGBM classifier + regressors (Optuna), logs to MLflow, registers `insurance_risk_scorer` |
| [`notebooks/03_model_registration.py`](../../notebooks/03_model_registration.py) | Registers/aliases the model in Unity Catalog |
| [`notebooks/04_model_serving.py`](../../notebooks/04_model_serving.py) | Deploys the real-time serving endpoint |
| [`notebooks/05_monitoring.py`](../../notebooks/05_monitoring.py) | Lakehouse monitoring on scored output |
| [`notebooks/pipeline_email_ingestion.py`](../../notebooks/pipeline_email_ingestion.py) | The 10-stage Lakeflow streaming pipeline (email → parse → enrich → score → quote → PDF → response) |

## Data generation — claims are correlated, not random (`generate_data.py`)

```python
# ~35% of orgs have any claims
if random.random() > 0.35: continue
num_claims = random.choices([1,2,3,4,5], weights=[40,30,15,10,5])[0]
# claim type is matched to a policy the org actually holds
severity = random.choices(["minor","moderate","major"], weights=[50,35,15])[0]
if   severity == "minor":    amount = random.uniform(500, 15000)
elif severity == "moderate": amount = random.uniform(15000, 100000)
else:                        amount = random.uniform(100000, 1000000)
```

## Risk score derived from claims + controls (`01_feature_engineering.py`)

```python
risk_score = clip(0, 100,
    least(num_claims * 5, 40)                 # claim history   — 40% weight
  + severity_band(avg_claim_severity)         # loss severity   — 20% weight
  + (3 - safety - training - cyber_ctrl) * 5  # control deficit — 15% weight
  + building_age_band(avg_building_age)       # property risk   — 10% weight
  + least(total_driver_violations*2, 10)      # fleet risk      — 10% weight
  + sensitive_data_score * 1.67)              # cyber exposure  —  5% weight
```

(Measured effect in the live data: `corr(num_claims, risk_score) = 0.804` — see Evidence 3.)

## AutoML training — leakage-aware feature selection (`02_automl_training.py`)

```python
exclude_cols = [ ...ids, split, target columns... ]
all_feature_cols = [c for c in features_df.columns if c not in exclude_cols]
# Classification: predict has_claim (uses full feature set)
# Risk-score regression: EXCLUDES claim-derived features to avoid leakage
risk_feature_cols = risk_num_cols + cat_cols
```

## Pipeline calls the real-time endpoint, with heuristic fallback (`pipeline_email_ingestion.py`)

```python
RISK_ENDPOINT = "email-to-quote-risk-scorer"
endpoint_url = f"{host}/serving-endpoints/{RISK_ENDPOINT}/invocations"
payload = {"dataframe_records": [{k: data.get(k, 0) for k in SCORING_FEATURES}]}
resp = _req.post(endpoint_url, json=payload, ...)
# on non-200 / schema mismatch -> heuristic scoring (scoring_method='heuristic')
```

Live outputs from these files are in [`logs/`](logs/): the pipeline run log, model prediction
samples, MLflow training metrics, and the Genie Q&A.
