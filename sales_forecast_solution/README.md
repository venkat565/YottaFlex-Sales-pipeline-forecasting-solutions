# Enterprise Sales Pipeline Forecasting & Scenario Analysis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: Kimball Star Schema](https://img.shields.io/badge/architecture-Kimball%20Star%20Schema-success.svg)](#-relational-architecture--kimball-star-schema)
[![Model: HistGradientBoosting](https://img.shields.io/badge/ML%20Model-HistGradientBoosting-indigo.svg)](#-machine-learning-forecasting-engine)
[![Validation: Zero Leakage](https://img.shields.io/badge/leakage%20check-Passed%20100%25-brightgreen.svg)](#-data-quality-exceptions--quarantine-engine)
[![Submission: YottaFlex AI](https://img.shields.io/badge/submission-YottaFlex%20AI%20Candidate-orange.svg)](PROMPT_HISTORY.md)

An end-to-end production sales forecasting and pipeline intelligence platform. Generates relational synthetic CRM data across 10 core business entities, snapshots historical states across 8 rolling quarters without target leakage, trains a calibrated gradient-boosted machine learning model, isolates anomalies into an automated quarantine queue, and presents executive forecasts via a Streamlit dashboard and a modern standalone HTML/React design system.

---

## 📋 Table of Contents
1. [Business Problem & Objective](#-business-problem--objective)
2. [Primary Actors & Workflows](#-primary-actors--workflows)
3. [Relational Architecture & Kimball Star Schema](#-relational-architecture--kimball-star-schema)
4. [Machine Learning Forecasting Engine](#-machine-learning-forecasting-engine)
5. [Data Quality Exceptions & Quarantine Engine](#-data-quality-exceptions--quarantine-engine)
6. [YottaFlex Guideline 04: "Explain the Why" (Architecture Decisions)](#-yottaflex-guideline-04-explain-the-why)
7. [Quick Start & Execution Guide](#-quick-start--execution-guide)
8. [Reproducibility & Verification](#-reproducibility--verification)
9. [Artifact Manifest](#-artifact-manifest)
10. [AI Disclosure & Provenance](#-ai-disclosure--provenance)

---

## 🎯 Business Problem & Objective

### The Challenge
Modern B2B revenue teams struggle with inaccurate sales forecasting due to:
- **Rep Subjectivity:** Sales representatives assign optimistic win probabilities or misclassify deal stages.
- **Deal Slippage:** Close dates frequently slip past quarter boundaries without recorded justification.
- **Stale Pipelines:** Opportunities sit idle for 60+ days with zero logged touchpoints, polluting top-line projections.
- **Look-Ahead Leakage:** Analysts mistakenly train models on final closed outcomes rather than true point-in-time snapshot states.

### The Objective
Deliver a verified, reproducible solution that:
1. Generates relational CRM master and transactional data across **10 core entities** using deterministic zero-padded IDs (`REP-000001`, `OPP-2026-000001`, `FCST-2026-01-31-001`).
2. Preserves state changes through immutable event logs and snapshots across **8 quarterly snapshot horizons** (`2026-01-31` to `2027-10-31`).
3. Predicts deal win probabilities and models **three scenario bounds**:
   - **Base Forecast:** Expected bookings (50th percentile ML probability-weighted bookings).
   - **Best Case:** Upper bound scenario (+20% conversion lift on qualified deals).
   - **Worst Case:** Conservative floor (-20% conversion drawdown for slippage).
4. Routes deliberate data quality failures to an automated **Quarantine Queue** (`ground_truth.csv` and `fct_data_quality_exceptions`).

---

## 👥 Primary Actors & Workflows

| Actor / System | Key Interaction with Solution |
| :--- | :--- |
| **Customer / Prospect** | Triggers touchpoint activities (emails, calls, meetings, demos) influencing deal age and velocity. |
| **Sales Rep** | Manages stage transitions, logs close date expectations, and works toward assigned quarterly quotas. |
| **Sales Operations / Analyst** | Monitors weighted scenario forecasts, evaluates Brier score calibration, and runs cohort conversion models. |
| **Support / Remediation Agent** | Reviews quarantined anomalies in `fct_data_quality_exceptions` and applies automated/manual fixes. |
| **System Administrator** | Triggers deterministic data regeneration, verifies SQLite schema constraints, and validates reproducibility. |

---

## 🏛️ Relational Architecture & Kimball Star Schema

The database model is structured in a strict **3NF Kimball Star Schema** design. Tables are exported as CSV, JSON, and a relational SQLite database (`sales_forecast.sqlite`):

```
                        ┌──────────────────┐
                        │ dim_territories  │
                        └────────┬─────────┘
                                 │ 1:N
┌──────────────────┐    ┌────────┴─────────┐    ┌──────────────────┐
│   dim_accounts   ├────┤fct_opportunities ├────┤  dim_sales_reps  │
└──────────────────┘ 1:N└────────┬─────────┘ 1:N└────────┬─────────┘
                                 │                        │
               ┌─────────────────┼─────────────────┐      │ 1:N
               │ 1:N             │ 1:N             │ 1:N  ▼
      ┌────────┴────────┐┌───────┴────────┐┌───────┴──────┐┌──────────────┐
      │fct_stage_hist   ││ fct_activities ││fct_forecast_ ││  fct_quotas  │
      │   (Event Log)   ││(Rep Touchpoint)││  snapshots   │└──────────────┘
      └─────────────────┘└────────────────┘└───────┬──────┘
                                                   │ 1:1
                                           ┌───────┴──────┐
                                           │ fct_forecast_│
                                           │ predictions  │
                                           └──────────────┘
```

### Table Definitions & Roles
| Table Name | Layer | Purpose | Primary Key | Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| `dim_territories` | Dimension | Regional sales territories and operating currencies | `territory_id` | - |
| `dim_sales_reps` | Dimension | Sales team directory, quotas, and assigned regions | `rep_id` | `territory_id` |
| `dim_accounts` | Dimension | Customer accounts, industries, and market segments | `account_id` | `territory_id` |
| `dim_stages` | Dimension | Pipeline milestones, sequence order, and default probabilities | `stage_id` | - |
| `fct_opportunities` | Fact | Core deal ledger with base USD amounts and dates | `opportunity_id` | `account_id`, `rep_id`, `stage_id`, `territory_id` |
| `fct_stage_histories` | Fact | Immutable audit log of every stage advancement | `stage_history_id` | `opportunity_id`, `stage_id` |
| `fct_activities` | Fact | Rep touchpoints (Calls, Emails, Meetings, Demos) | `activity_id` | `opportunity_id`, `rep_id` |
| `fct_quotas` | Fact | Rep quarterly booking quota targets | `quota_id` | `rep_id` |
| `fct_historical_bookings` | Fact | Recognized closed-won bookings ledger | `booking_id` | `opportunity_id`, `rep_id`, `account_id` |
| `fct_forecast_snapshots` | Fact | Historical point-in-time deal states across 8 quarters | `snapshot_id` | `opportunity_id`, `stage_id` |
| `fct_forecast_predictions` | Fact | ML win probabilities and 3 scenario forecasts | `snapshot_id` | `opportunity_id` |
| `fct_data_quality_exceptions`| Fact | Quarantined anomaly records and automated decisions | `record_id` | `table_name` |

---

## 🤖 Machine Learning Forecasting Engine

### Modeling Methodology
- **Algorithm:** `HistGradientBoostingClassifier` with monotonic constraints and calibrated probabilities.
- **Target Variable:** `actual_won` (Binary: 1 = Closed Won, 0 = Closed Lost / Slipped).
- **Point-in-Time Features (Zero Leakage):**
  - `stage_order` & `stage_probability`: Current stage milestone.
  - `amount_base_currency`: Deal size normalized to USD.
  - `age_days`: Opportunity age *as of the snapshot date*.
  - `days_to_close`: Days remaining until expected close date.
  - `activity_count`: Number of activities logged *prior to or on snapshot date*.
  - `segment` & `product`: One-hot encoded market segment and product line.

### Model Performance Metrics (`outputs/evaluation_metrics.json`)
- **Brier Score Loss:** `0.166` (Demonstrates well-calibrated probabilities).
- **ROC-AUC:** `0.8333` (High discriminative power between won and lost deals).
- **Forecast WAPE (Weighted Absolute Percentage Error):** `0.7244`.
- **Booking MAE:** `$1,082.16` on deal cohort testing.

---

## 🛡️ Data Quality Exceptions & Quarantine Engine

In accordance with Step 5 of the specification, 5 deliberate edge-case anomalies were generated, tagged with `issue_type` and `ground_truth`, and isolated into [ground_truth.csv](outputs/ground_truth.csv) without polluting training features:

| Record ID | Issue Type | Injected Failure Mode | Prescribed Automated Decision |
| :--- | :--- | :--- | :--- |
| `OPP-2026-000001` | `close_date_before_creation` | Close date (`2026-01-10`) is earlier than creation date (`2026-02-01`). | `quarantine_and_flag` |
| `OPP-2026-000002` | `stage_probability_inconsistent` | Stage is "Proposal" (standard: 55%), but deal was manually overridden to 99%. | `reconcile_to_stage_definition` |
| `OPP-2026-000003-DUP` | `duplicate_opportunity_counted` | Duplicate opportunity ID counted twice in pipeline. | `exclude_duplicate_from_pipeline` |
| `FCST-2026-01-31-OPP-2026-000002` | `forecast_uses_final_outcome_data` | Snapshot includes future realized booking outcome before deal closed. | `exclude_actual_outcome_fields_from_features` |
| `MIXED-CURRENCY-CHECK` | `currency_totals_mixed` | Deal amount in EUR/GBP summed directly with USD without exchange conversion. | `convert_to_base_currency_before_sum` |

---

## 📐 YottaFlex Guideline 04: "Explain the Why"

### 1. Key Assumptions
1. **Snapshot Cadence:** Point-in-time snapshots occur on the final calendar day of each quarter (`2026-01-31`, `2026-04-30`, etc.). Any activities occurring on day $T+1$ are strictly invisible to snapshot day $T$.
2. **Currency Standardization:** While opportunities are generated in multiple currencies (USD, EUR, GBP, INR), all forecast rollups and ML loss calculations operate strictly on `amount_base_currency` (USD) to avoid currency mismatch distortion.
3. **Slippage Dynamics:** If deal age exceeds 120 days without stage advancement, its win probability degrades by 35% and its close date automatically slips into the subsequent quarter.

### 2. Architectural Decisions & Rationale
- **Why Kimball Star Schema instead of flat CSVs?**  
  Enterprise forecasting requires auditability. If a rep changes territories or quotas, a star schema maintains surrogate key history (`fct_stage_histories`) rather than overwriting past quarters.
- **Why HistGradientBoosting over Linear Logistic Regression?**  
  Deal conversion is non-linear: a 90-day-old deal in "Prospecting" is high-risk, but a 90-day-old deal in "Negotiation" with 15 logged meetings is healthy. Tree-based boosting naturally captures these feature interactions without manual polynomial feature engineering.
- **Why a Separate `ground_truth.csv`?**  
  Data quality errors must never leak into model training or reporting tables. Separating anomalies into an explicit quarantine ledger guarantees full traceability while preserving clean training signals.

### 3. Trade-offs Considered
- **Starter Scale vs. Full Scale:**  
  Running 20,000 opportunities with 8 quarters of daily touchpoints generates over 250,000 relational rows. We parameterized `run_pipeline.py` with `--scale starter` (fast 5-second smoke test) and `--scale full` (production enterprise volume) so evaluators can inspect results immediately without compute bottlenecks.
- **SQLite vs. External PostgreSQL:**  
  SQLite was chosen to fulfill YottaFlex Guideline 08 (*"Use only free or locally runnable services"*). It provides complete relational foreign-key integrity with zero container or network setup requirements.

### 4. Known Limitations
- **Macroeconomic Shock Modeling:** Synthetic conversion curves assume stationary baseline market conditions; sudden industry-wide shocks are modeled through scenario bounds rather than stochastic macro simulations.
- **Human Note Parsing:** Touchpoints are currently structured as discrete activity types rather than raw unstructured sales rep call transcripts.

---

## 🚀 Quick Start & Execution Guide

### Prerequisites
- Python 3.10 or higher
- PowerShell (Windows) or Bash (macOS/Linux)

### 1. Clone & Setup Environment
```powershell
cd sales_pipeline_forecasting_solution\sales_forecast_solution

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements (if running fresh)
pip install -r requirements.txt
```

### 2. Run the Data Pipeline

#### Fast Starter Scale (Smoke Test — 500 Deals)
```powershell
python run_pipeline.py --scale starter
```

#### Full Enterprise Volume (2,000 Reps, 20,000 Opportunities, 8 Quarters)
```powershell
python run_pipeline.py --scale full
```

### 3. Launch the Streamlit Executive Dashboard
```powershell
streamlit run dashboard.py
```
Open **`http://localhost:8501`** to view:
- **Tab 1: Forecast & Scenarios:** Executive KPIs, scenario spread chart, segment breakdown.
- **Tab 2: Deal Pipeline:** Top deals table with green win-probability progress bars and segment filters.
- **Tab 3: Data Quality:** Active Quarantine Queue showing flagged edge cases and remediation decisions.
- **Tab 4: Schema Explorer:** Live interactive schema inspection for all 10 normalized tables.

### 4. Standalone HTML / React Frontend
For a lightweight zero-dependency presentation, open **`frontend/index.html`** directly in any modern browser to experience the Mantine 7 DoubleNavbar design system and Tabler icons.

---

## 🔒 Reproducibility & Verification

Generation is 100% deterministic using fixed random seed **`20261022`**.

To verify bit-for-bit reproducibility:
1. Run `python run_pipeline.py --scale full --seed 20261022`.
2. Inspect [outputs/reproducibility.json](outputs/reproducibility.json).
3. Re-run the command; all SHA-256 table hashes will match identically:
   ```json
   {
     "seed": 20261022,
     "sha256": {
       "fct_opportunities.csv": "cca986c48ce8fa4ef75d50e4716c63f...",
       "fct_forecast_predictions.csv": "4527f0aa575224169b124be34a0e..."
     }
   }
   ```

---

## 📁 Artifact Manifest

All generated artifacts are written directly to `outputs/`:
```
outputs/
├── clean_reports/                 # 12 clean CSV tables with normalized Title Case headers (0 underscores)
├── csv/                           # Relational CSV exports (dim_* and fct_* tables)
├── json/                          # Standardized JSON document exports
├── sales_forecast.sqlite          # Enforced relational SQLite database with foreign keys
├── schema.sql                     # Full SQL DDL schema specification
├── ground_truth.csv               # Isolated quarantine anomaly ledger with expected decisions
├── evaluation_metrics.json        # Model performance metrics (Brier score, AUC, WAPE)
├── data_dictionary.json           # Comprehensive field-level metadata and constraints
├── validation_summary.json        # Automated relational integrity assertion results
└── reproducibility.json           # Deterministic seed and SHA-256 artifact hashes
```

---

## 🤝 AI Disclosure & Provenance

This project was built within the **72-hour challenge window** for the **YottaFlex AI Recruitment Drive**.  
Per Guideline 03, the complete prompt history, AI tool interactions, and candidate verification decisions are fully documented in [PROMPT_HISTORY.md](../PROMPT_HISTORY.md).
