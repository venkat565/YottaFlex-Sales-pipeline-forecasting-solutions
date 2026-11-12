# Sales Pipeline Forecasting & Scenario Analysis

A reproducible synthetic CRM data generator and sales-bookings forecasting solution using a **normalized Kimball Star Schema** architecture.

---

## 🏛️ Normalized Data Schema (Star Schema Architecture)

All tables have been normalized into clean `snake_case` with explicit **Dimensions (`dim_`)** and **Facts (`fct_`)**:

| Table Name | Layer | Description | Primary Key |
| :--- | :--- | :--- | :--- |
| `dim_territories` | Dimension | Sales geographic regions and operating currencies | `territory_id` |
| `dim_sales_reps` | Dimension | Sales team members, territories, and employment status | `rep_id` |
| `dim_accounts` | Dimension | Customer accounts, industries, and market tiers (SMB/Enterprise) | `account_id` |
| `dim_stages` | Dimension | Pipeline milestone stages and default win probabilities | `stage_id` |
| `fct_opportunities` | Fact | Core sales pipeline deals with normalized USD amounts | `opportunity_id` |
| `fct_stage_histories` | Fact | Historical audit trail of opportunity stage transitions | `stage_history_id` |
| `fct_activities` | Fact | Logged rep touchpoints (calls, emails, meetings, demos) | `activity_id` |
| `fct_quotas` | Fact | Assigned quarterly revenue quota targets per rep | `quota_id` |
| `fct_historical_bookings` | Fact | Realized closed-won revenue recognition ledger | `booking_id` |
| `fct_forecast_snapshots` | Fact | Point-in-time historical pipeline states (leakage-free) | `snapshot_id` |
| `fct_forecast_predictions` | Fact | Scored deal probabilities, base forecast, best/worst cases | `snapshot_id` |
| `fct_data_quality_exceptions` | Fact | Quarantined anomaly ledger with remediation actions | `record_id` |

*(Note: Legacy PascalCase CSV/JSON files such as `Opportunity.csv` and `SalesRep.csv` are also automatically exported for backward compatibility).*

---

## 🚀 Quick Start (Windows PowerShell)

```powershell
cd sales_forecast_solution

# 1. Activate Virtual Environment
.venv\Scripts\Activate.ps1

# 2. Run Starter Pipeline (Fast Smoke Test)
python run_pipeline.py --scale starter

# 3. Launch Interactive Streamlit Dashboard
streamlit run dashboard.py
```

### Full Enterprise Scale
```powershell
python run_pipeline.py --scale full
```

### Custom Scale
```powershell
python run_pipeline.py --reps 2000 --accounts 2000 --opportunities 20000 --seed 20261022
```

---

## 🧠 Modeling & Architecture Highlights
- **Point-in-Time Freshness:** Snapshot features are point-in-time strictly. Final outcomes and future touchpoints are never leaked into the model features.
- **Relational Integrity:** SQLite export enforces `FOREIGN KEY` constraints and table DDL schemas via `schema.sql`.
- **Clean Number Formatting:** Monetary fields are rounded to 2 decimal places (`$0.00`) and probabilities are bounded and rounded to 4 decimal places.
- **Data Quality Quarantine:** Data quality issues (duplicate deals, inverted close dates, stage probability overrides) are isolated into `fct_data_quality_exceptions`.
- **Interactive Multi-Tab Dashboard:** Executive KPI summary cards, scenario bar charts, interactive deal filters (by segment and stage), and schema inspection.

---

## 📁 Artifact Outputs (`outputs/`)
- `outputs/csv/`: Clean CSV files for all `dim_` and `fct_` tables.
- `outputs/json/`: Standardized JSON record exports.
- `outputs/sales_forecast.sqlite`: Relational SQLite database with enforced schema.
- `outputs/schema.sql`: Clean SQL DDL statements.
- `outputs/evaluation_metrics.json`: Brier score, ROC-AUC, MAE, RMSE, and WAPE.
- `outputs/data_dictionary.json`: Comprehensive data dictionary.
- `outputs/validation_summary.json`: Integrity checks and assertion results.
- `outputs/reproducibility.json`: Seed and SHA-256 file checksums.
