# Evidence 3 — Synthetic data generation logic & realistic correlations

> **Finding addressed:** "There is no visible evidence of the synthetic data generation logic
> itself, so it is unclear whether the underlying risk and claims data is shaped with
> realistic correlations (e.g., higher claims history driving … risk scores) or is closer to
> generic filler dressed up with insurance field names."

## 3.1 The generation logic is explicit and inspectable

`scripts/generate_data.py` (46 KB) builds a coherent commercial-insurance book across 11
related tables (`organizations, locations, employees, property_assets, vehicles,
cyber_profiles, financials, policies, claims, coverage_requests, contracts`). Claims are not
random noise — they are generated with structured frequency and severity:

```python
# ~35% of orgs have any claims
if random.random() > 0.35: continue
num_claims = random.choices([1,2,3,4,5], weights=[40,30,15,10,5])[0]
# claim type is matched to an actual policy the org holds
severity = random.choices(["minor","moderate","major"], weights=[50,35,15])[0]
if   severity == "minor":    amount = random.uniform(500, 15000)
elif severity == "moderate": amount = random.uniform(15000, 100000)
else:                        amount = random.uniform(100000, 1000000)
```

The **risk score is then derived from those claims** — it is a documented, weighted
composite (`notebooks/01_feature_engineering.py`), not an independent random field:

```python
risk_score = clip(0, 100,
    least(num_claims * 5, 40)                 # claim history  — 40% weight
  + severity_band(avg_claim_severity)         # loss severity  — 20% weight
  + (3 - safety - training - cyber_ctrl) * 5  # control deficit — 15% weight
  + building_age_band(avg_building_age)       # property risk  — 10% weight
  + least(total_driver_violations*2, 10)      # fleet risk     — 10% weight
  + sensitive_data_score * 1.67)              # cyber exposure —  5% weight
```

Indicated premium is likewise exposure-driven, e.g. GL =
`annual_revenue * 0.005 * (1 + risk_score/100) * category_multiplier`.

## 3.2 The correlations actually hold in the deployed data (10,000 orgs)

Measured on `dvin100_demos_catalog.email_to_quote.risk_features`
(`data/synthetic_claims_vs_risk.csv`):

| Claims bucket | # orgs | Avg risk score | Avg loss ratio | Avg claims paid |
|---------------|--------|----------------|----------------|-----------------|
| 0 claims   | 6,435 | **17.7** | 0.00 | $0 |
| 1–2 claims | 2,521 | **36.3** | 3.59 | $163,815 |
| 3–5 claims | 1,044 | **50.1** | 9.56 | $393,373 |

Risk score rises monotonically with claims history, exactly as the finding asked to verify.

**Pearson correlation coefficients** across all orgs (`data/synthetic_pearson_correlations.csv`):

| Relationship | r |
|--------------|---|
| num_claims → risk_score          | **0.804** |
| total_claims_paid → risk_score   | 0.610 |
| loss_ratio → risk_score          | 0.339 |
| annual_revenue → indicated_premium | **0.952** |

- **0.804** — strong positive claims-history → risk-score correlation. This is the exact
  relationship the reviewer flagged as unverified; it is present and strong.
- **0.952** — bigger businesses get bigger premiums (premium is exposure-driven), which is
  actuarially correct.
- Note that `corr(risk_score, total_premium)` is near zero on its own — expected, because
  premium is dominated by *exposure* (revenue/size) and only *modified* by the risk
  multiplier `(1 + risk_score/100)`. That is realistic pricing behavior, not filler.

## 3.3 Conclusion

The risk and claims data is generated with a documented causal chain
(**claims → loss severity → risk score → premium multiplier**) and the intended correlations
are measurable in the live tables. It is a structured synthetic book, not generic filler
with insurance-flavored column names.
