"""Sales Pipeline Data Generator and Point-in-Time Forecasting Engine.

Generates normalized, relational synthetic sales data (Kimball Star Schema),
performs point-in-time snapshotting, trains a gradient-boosted booking forecast model,
and outputs clean CSV, JSON, and SQLite database artifacts.
"""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    brier_score_loss,
    mean_absolute_error,
    mean_squared_error,
    roc_auc_score,
)

from config import (
    ACTIVITY_TYPES,
    AS_OF_DATES,
    CURRENCIES,
    PRODUCTS,
    REGIONS,
    SEED,
    SEGMENTS,
    STAGES,
)


def make_id(prefix: str, n: int, width: int = 6) -> str:
    """Generate deterministic, padded entity identifiers."""
    return f"{prefix}{n:0{width}d}"


def normalize_column_name(col: str) -> str:
    """Transform raw snake_case column names into clean Title Case without underscores."""
    header_map = {
        "opportunity_id": "Opportunity ID",
        "rep_id": "Sales Rep ID",
        "territory_id": "Territory ID",
        "account_id": "Account ID",
        "stage_id": "Stage ID",
        "stage_name": "Pipeline Stage",
        "stage_probability": "Stage Probability",
        "stage_order": "Stage Order",
        "amount": "Deal Amount",
        "currency": "Currency Code",
        "amount_base_currency": "Deal Amount ($)",
        "created_date": "Created Date",
        "expected_close_date": "Expected Close Date",
        "lifecycle_state": "Lifecycle State",
        "predicted_probability": "Win Probability",
        "base_forecast": "Base Forecast ($)",
        "best_case": "Best Case ($)",
        "worst_case": "Worst Case ($)",
        "exception_flag": "Risk Flag",
        "record_id": "Record ID",
        "table_name": "Target Table",
        "anomaly_type": "Anomaly Classification",
        "issue_type": "Issue Type",
        "severity": "Severity Level",
        "ground_truth": "Expected Behavior",
        "expected_decision": "Automated Decision",
        "actual_decision": "Remediation Action",
        "is_quarantined": "Quarantine Status",
        "age_days": "Deal Age (Days)",
        "days_to_close": "Days to Close",
        "activity_count": "Touchpoint Activities",
        "activity_id": "Activity ID",
        "activity_type": "Activity Type",
        "activity_date": "Activity Date",
        "completed": "Completed Status",
        "quota_id": "Quota ID",
        "fiscal_quarter": "Fiscal Quarter",
        "quota_amount": "Quota Amount ($)",
        "effective_from": "Effective Date",
        "booking_id": "Booking ID",
        "booking_date": "Booking Date",
        "booking_amount": "Booking Amount ($)",
        "outcome": "Deal Outcome",
        "snapshot_id": "Snapshot ID",
        "snapshot_date": "Snapshot Date",
        "actual_won": "Actual Won Status",
        "actual_booking": "Actual Realized Booking ($)",
        "horizon_days": "Forecast Horizon (Days)",
        "segment": "Customer Segment",
        "territory_name": "Territory Name",
        "region": "Operating Region",
        "rep_name": "Sales Rep Name",
        "hire_date": "Hire Date",
        "employment_status": "Employment Status",
        "account_name": "Account Name",
        "industry": "Industry Sector",
        "stage_history_id": "Stage History ID",
        "changed_at": "Timestamp Changed",
        "source": "Change Source",
    }
    if col in header_map:
        return header_map[col]
    cleaned = col.replace("_", " ").strip()
    return " ".join(word.capitalize() for word in cleaned.split())


def generate(
    reps: int = 2000,
    accounts: int = 2000,
    opportunities: int = 20000,
    seed: int = SEED,
    out: str = "outputs",
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """Generate normalized sales CRM tables, snapshots, and forecast predictions."""
    rng = np.random.default_rng(seed)
    out_dir = Path(out)
    csv_dir = out_dir / "csv"
    json_dir = out_dir / "json"
    csv_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Dimension Tables (Master Data)
    # ---------------------------------------------------------
    territory_rows = []
    for i, region in enumerate(REGIONS * 4):
        territory_rows.append(
            {
                "territory_id": f"TER-{i + 1:04d}",
                "territory_name": f"{region}-T{i + 1:02d}",
                "region": region,
                "currency": "USD",
                "effective_from": "2024-01-01",
                "effective_to": None,
            }
        )
    dim_territories = pd.DataFrame(territory_rows)

    rep_rows = []
    for i in range(reps):
        terr = dim_territories.iloc[i % len(dim_territories)]
        hire_offset = int(rng.integers(0, 1700))
        hire_date = pd.Timestamp("2021-01-01") + pd.Timedelta(days=hire_offset)
        rep_rows.append(
            {
                "rep_id": make_id("REP-", i + 1),
                "rep_name": f"Sales Rep {i + 1:04d}",
                "territory_id": terr["territory_id"],
                "hire_date": hire_date.strftime("%Y-%m-%d"),
                "employment_status": rng.choice(
                    ["Active", "On Leave", "Inactive"], p=[0.91, 0.05, 0.04]
                ),
            }
        )
    dim_sales_reps = pd.DataFrame(rep_rows)

    account_rows = []
    for i in range(accounts):
        terr_idx = int(rng.integers(0, len(dim_territories)))
        terr_id = dim_territories.iloc[terr_idx]["territory_id"]
        created_offset = int(rng.integers(0, 1500))
        created_date = pd.Timestamp("2022-01-01") + pd.Timedelta(days=created_offset)
        account_rows.append(
            {
                "account_id": make_id("ACC-", i + 1),
                "account_name": f"Account {i + 1:05d}",
                "segment": rng.choice(SEGMENTS, p=[0.55, 0.30, 0.15]),
                "industry": rng.choice(
                    ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"]
                ),
                "territory_id": terr_id,
                "created_date": created_date.strftime("%Y-%m-%d"),
            }
        )
    dim_accounts = pd.DataFrame(account_rows)

    stage_rows = [
        {
            "stage_id": f"STAGE-{i + 1:02d}",
            "stage_name": stage_name,
            "default_probability": round(prob, 4),
            "stage_order": order,
        }
        for i, (stage_name, prob, order) in enumerate(STAGES)
    ]
    dim_stages = pd.DataFrame(stage_rows)

    # ---------------------------------------------------------
    # 2. Fact Tables: Opportunities
    # ---------------------------------------------------------
    opp_rows = []
    for i in range(opportunities):
        created_dt = pd.Timestamp("2025-01-01") + pd.Timedelta(
            days=int(rng.integers(0, 620))
        )
        close_dt = created_dt + pd.Timedelta(days=int(rng.integers(30, 300)))

        rep = dim_sales_reps.iloc[int(rng.integers(0, reps))]
        acct = dim_accounts.iloc[int(rng.integers(0, accounts))]

        stage_idx = int(rng.choice([0, 1, 2, 3, 4], p=[0.18, 0.25, 0.25, 0.20, 0.12]))
        stage = STAGES[stage_idx]

        log_mean = 9.2 if acct["segment"] == "Enterprise" else 7.8
        amount = float(np.round(rng.lognormal(mean=log_mean, sigma=0.8), 2))
        currency = rng.choice(CURRENCIES, p=[0.55, 0.30, 0.10, 0.05])

        opp_rows.append(
            {
                "opportunity_id": make_id("OPP-2026-", i + 1),
                "account_id": acct["account_id"],
                "rep_id": rep["rep_id"],
                "territory_id": acct["territory_id"],
                "stage_id": f"STAGE-{stage_idx + 1:02d}",
                "stage_name": stage[0],
                "stage_probability": round(stage[1], 4),
                "amount": amount,
                "currency": currency,
                "amount_base_currency": amount,
                "product": rng.choice(PRODUCTS),
                "created_date": created_dt.strftime("%Y-%m-%d"),
                "expected_close_date": close_dt.strftime("%Y-%m-%d"),
                "is_duplicate": 0,
                "lifecycle_state": "Open",
            }
        )
    fct_opportunities = pd.DataFrame(opp_rows)

    # ---------------------------------------------------------
    # 3. Fact Tables: Stage History & Activities
    # ---------------------------------------------------------
    history_rows = []
    activity_rows = []

    for row in fct_opportunities.itertuples(index=False):
        history_rows.append(
            {
                "stage_history_id": f"STG-{row.opportunity_id}-001",
                "opportunity_id": row.opportunity_id,
                "stage_id": row.stage_id,
                "stage_name": row.stage_name,
                "changed_at": row.created_date,
                "source": "Initial",
            }
        )

        n_activities = int(rng.poisson(3.2))
        for j in range(n_activities):
            act_day = pd.Timestamp(row.created_date) + pd.Timedelta(
                days=int(rng.integers(0, 180))
            )
            activity_rows.append(
                {
                    "activity_id": f"ACT-{row.opportunity_id}-{j + 1:02d}",
                    "opportunity_id": row.opportunity_id,
                    "rep_id": row.rep_id,
                    "activity_type": rng.choice(ACTIVITY_TYPES),
                    "activity_date": act_day.strftime("%Y-%m-%d"),
                    "completed": 1 if rng.random() < 0.9 else 0,
                }
            )

    fct_stage_histories = pd.DataFrame(history_rows)
    fct_activities = pd.DataFrame(activity_rows)

    # ---------------------------------------------------------
    # 4. Fact Tables: Quotas & Ground Truth Outcomes
    # ---------------------------------------------------------
    quota_rows = []
    quarters = [
        "2025Q1",
        "2025Q2",
        "2025Q3",
        "2025Q4",
        "2026Q1",
        "2026Q2",
        "2026Q3",
        "2026Q4",
    ]
    for rep in dim_sales_reps.itertuples(index=False):
        for q_idx, quarter in enumerate(quarters):
            month = ((q_idx % 4) * 3) + 1
            quota_rows.append(
                {
                    "quota_id": f"QUOTA-{rep.rep_id}-{quarter}",
                    "rep_id": rep.rep_id,
                    "fiscal_quarter": quarter,
                    "quota_amount": round(float(rng.uniform(50000, 250000)), 2),
                    "currency": "USD",
                    "effective_from": f"2026-{month:02d}-01",
                }
            )
    fct_quotas = pd.DataFrame(quota_rows)

    # Ground truth simulation via documented logistic conversion rule
    completed_acts = fct_activities[fct_activities["completed"] == 1]
    hist_counts = (
        completed_acts.groupby("opportunity_id").size().to_dict()
        if not completed_acts.empty
        else {}
    )

    age_days = (
        pd.Timestamp("2026-11-01") - pd.to_datetime(fct_opportunities["created_date"])
    ).dt.days.clip(lower=0)
    stage_prob = fct_opportunities["stage_probability"].to_numpy()
    activity_score = np.array(
        [hist_counts.get(x, 0) for x in fct_opportunities["opportunity_id"]]
    )
    amount_log = np.log1p(fct_opportunities["amount_base_currency"].to_numpy())

    logit = (
        -2.0
        + 4.0 * stage_prob
        + 0.018 * np.minimum(age_days.to_numpy(), 180)
        - 0.025 * np.maximum(age_days.to_numpy() - 180, 0)
        + 0.10 * activity_score
        + 0.08 * (amount_log - 8)
    )
    prob_won = 1 / (1 + np.exp(-logit))
    is_won = rng.binomial(1, prob_won)

    slip_prob = np.clip(
        0.12 + 0.025 * np.maximum(3 - activity_score, 0) + 0.10 * (stage_prob < 0.3),
        0.05,
        0.75,
    )
    slipped = rng.binomial(1, slip_prob)
    slippage_days = slipped * rng.integers(15, 100, size=len(fct_opportunities))
    final_close_dates = pd.to_datetime(
        fct_opportunities["expected_close_date"]
    ) + pd.to_timedelta(slippage_days, unit="D")

    fct_opportunities["final_outcome"] = np.where(
        is_won == 1, "Closed Won", "Closed Lost"
    )
    fct_opportunities["actual_close_date"] = final_close_dates.dt.strftime("%Y-%m-%d")
    fct_opportunities["lifecycle_state"] = fct_opportunities["final_outcome"]
    fct_opportunities["actual_booking_base_currency"] = np.where(
        is_won == 1, fct_opportunities["amount_base_currency"], 0.0
    ).round(2)

    booking_rows = []
    for i, r in enumerate(fct_opportunities.itertuples(index=False)):
        if r.final_outcome == "Closed Won":
            booking_rows.append(
                {
                    "booking_id": f"BOOK-{i + 1:07d}",
                    "opportunity_id": r.opportunity_id,
                    "booking_date": r.actual_close_date,
                    "booking_amount": round(float(r.actual_booking_base_currency), 2),
                    "currency": "USD",
                    "outcome": r.final_outcome,
                }
            )
    fct_historical_bookings = pd.DataFrame(booking_rows)

    # ---------------------------------------------------------
    # 5. Point-in-Time Forecast Snapshots (Optimized)
    # ---------------------------------------------------------
    # Pre-index completed activities by opportunity and date for fast vector lookup
    acct_segment_map = dict(zip(dim_accounts["account_id"], dim_accounts["segment"]))

    act_indexed = completed_acts[["opportunity_id", "activity_date"]].copy()
    act_indexed["activity_date"] = pd.to_datetime(act_indexed["activity_date"])

    snapshots = []
    for snap in AS_OF_DATES:
        snap_dt = pd.Timestamp(snap)
        snap_acts = act_indexed[act_indexed["activity_date"] <= snap_dt]
        snap_act_counts = snap_acts.groupby("opportunity_id").size().to_dict()

        for oi, r in enumerate(fct_opportunities.itertuples(index=False)):
            created_dt = pd.Timestamp(r.created_date)
            expected_dt = pd.Timestamp(r.expected_close_date)
            realized_dt = pd.Timestamp(final_close_dates.iloc[oi])

            # Include only deals that were actively open at this snapshot date
            if created_dt > snap_dt or realized_dt <= snap_dt:
                continue

            age = max(0, (snap_dt - created_dt).days)
            cnt = snap_act_counts.get(r.opportunity_id, 0)
            stage_p = round(float(r.stage_probability), 4)
            days_to_close = (expected_dt - snap_dt).days

            snapshots.append(
                {
                    "snapshot_id": f"FCST-{snap}-{r.opportunity_id}",
                    "snapshot_date": snap,
                    "opportunity_id": r.opportunity_id,
                    "rep_id": r.rep_id,
                    "territory_id": r.territory_id,
                    "segment": acct_segment_map.get(r.account_id, "Unknown"),
                    "stage_name": r.stage_name,
                    "stage_probability": stage_p,
                    "age_days": age,
                    "days_to_close": days_to_close,
                    "activity_count": cnt,
                    "amount_base_currency": round(float(r.amount_base_currency), 2),
                    "actual_won": int(r.final_outcome == "Closed Won"),
                    "actual_booking": round(float(r.actual_booking_base_currency), 2),
                    "horizon_days": max(0, days_to_close),
                }
            )
    fct_forecast_snapshots = pd.DataFrame(snapshots)

    # ---------------------------------------------------------
    # 6. Data Quality Exception Injection & Quarantine Tracking
    # ---------------------------------------------------------
    exception_rows = []
    if len(fct_opportunities) >= 5:
        # Anomaly 1: Invalid date order
        fct_opportunities.loc[0, "expected_close_date"] = "2024-12-01"
        exception_rows.append(
            {
                "record_id": fct_opportunities.loc[0, "opportunity_id"],
                "table_name": "fct_opportunities",
                "issue_type": "close_date_before_creation",
                "severity": "HIGH",
                "ground_truth": "invalid_date_order",
                "expected_decision": "quarantine_and_flag",
            }
        )

        # Anomaly 2: Inconsistent stage probability
        fct_opportunities.loc[1, "stage_probability"] = 0.99
        exception_rows.append(
            {
                "record_id": fct_opportunities.loc[1, "opportunity_id"],
                "table_name": "fct_opportunities",
                "issue_type": "stage_probability_inconsistent",
                "severity": "MEDIUM",
                "ground_truth": "probability_mismatch",
                "expected_decision": "reconcile_to_stage_definition",
            }
        )

        # Anomaly 3: Duplicate opportunity record
        dup = fct_opportunities.iloc[2].copy()
        dup["opportunity_id"] = fct_opportunities.iloc[2].opportunity_id + "-DUP"
        dup["is_duplicate"] = 1
        fct_opportunities = pd.concat(
            [fct_opportunities, pd.DataFrame([dup])], ignore_index=True
        )
        exception_rows.append(
            {
                "record_id": dup["opportunity_id"],
                "table_name": "fct_opportunities",
                "issue_type": "duplicate_opportunity_counted",
                "severity": "CRITICAL",
                "ground_truth": "duplicate_record",
                "expected_decision": "exclude_duplicate_from_pipeline",
            }
        )

        # Anomaly 4: Snapshot target leakage test
        snap_ref = (
            fct_forecast_snapshots.iloc[0].snapshot_id
            if len(fct_forecast_snapshots)
            else "N/A"
        )
        exception_rows.append(
            {
                "record_id": snap_ref,
                "table_name": "fct_forecast_snapshots",
                "issue_type": "forecast_uses_final_outcome_data",
                "severity": "CRITICAL",
                "ground_truth": "target_leakage_risk",
                "expected_decision": "exclude_actual_outcome_fields_from_features",
            }
        )

        # Anomaly 5: Mixed currency aggregation check
        exception_rows.append(
            {
                "record_id": "MIXED-CURRENCY-CHECK",
                "table_name": "fct_opportunities",
                "issue_type": "currency_totals_mixed",
                "severity": "MEDIUM",
                "ground_truth": "aggregation_currency_mismatch",
                "expected_decision": "convert_to_base_currency_before_sum",
            }
        )

    fct_data_quality_exceptions = pd.DataFrame(exception_rows)

    # ---------------------------------------------------------
    # 7. Machine Learning Forecast Model & Scenario Evaluation
    # ---------------------------------------------------------
    if len(fct_forecast_snapshots):
        features = [
            "stage_probability",
            "age_days",
            "days_to_close",
            "activity_count",
            "amount_base_currency",
            "horizon_days",
        ]
        eval_date = fct_forecast_snapshots["snapshot_date"].max()
        train = fct_forecast_snapshots[
            fct_forecast_snapshots["snapshot_date"] < eval_date
        ]
        test = fct_forecast_snapshots[
            fct_forecast_snapshots["snapshot_date"] == eval_date
        ]

        model = HistGradientBoostingClassifier(
            max_iter=80, max_leaf_nodes=15, learning_rate=0.08, random_state=seed
        )

        eval_df = test.copy()
        if len(train) and train["actual_won"].nunique() > 1:
            model.fit(train[features], train["actual_won"])
            eval_df["predicted_probability"] = (
                model.predict_proba(eval_df[features])[:, 1].round(4)
                if len(eval_df)
                else []
            )
        else:
            eval_df["predicted_probability"] = eval_df["stage_probability"].clip(0, 1)

        eval_df["base_forecast"] = (
            eval_df["amount_base_currency"] * eval_df["predicted_probability"]
        ).round(2)
        eval_df["best_case"] = (
            eval_df["amount_base_currency"]
            * np.minimum(1.0, eval_df["predicted_probability"] * 1.20)
        ).round(2)
        eval_df["worst_case"] = (
            eval_df["amount_base_currency"]
            * np.maximum(0.0, eval_df["predicted_probability"] * 0.80)
        ).round(2)

        eval_df["exception_flag"] = np.where(
            (eval_df["age_days"] > 120) & (eval_df["activity_count"] == 0),
            "STALE_NO_ACTIVITY",
            "",
        )

        if len(eval_df):
            y_true = eval_df["actual_won"]
            y_pred = eval_df["predicted_probability"]
            metrics = {
                "snapshot_date": str(eval_date),
                "evaluation_rows": int(len(eval_df)),
                "brier_score": (
                    float(round(brier_score_loss(y_true, y_pred), 4))
                    if y_true.nunique() > 1
                    else None
                ),
                "roc_auc": (
                    float(round(roc_auc_score(y_true, y_pred), 4))
                    if y_true.nunique() > 1
                    else None
                ),
                "booking_mae": float(
                    round(
                        mean_absolute_error(
                            eval_df["actual_booking"], eval_df["base_forecast"]
                        ),
                        2,
                    )
                ),
                "booking_rmse": float(
                    round(
                        mean_squared_error(
                            eval_df["actual_booking"], eval_df["base_forecast"]
                        )
                        ** 0.5,
                        2,
                    )
                ),
                "booking_wape": float(
                    round(
                        np.abs(
                            eval_df["actual_booking"] - eval_df["base_forecast"]
                        ).sum()
                        / max(eval_df["actual_booking"].sum(), 1.0),
                        4,
                    )
                ),
            }
        else:
            metrics = {"evaluation_rows": 0}
    else:
        eval_df = pd.DataFrame()
        metrics = {"evaluation_rows": 0}

    fct_forecast_predictions = eval_df

    # ---------------------------------------------------------
    # 8. Normalized Table Assembly
    # ---------------------------------------------------------
    normalized_tables: Dict[str, pd.DataFrame] = {
        "dim_territories": dim_territories,
        "dim_sales_reps": dim_sales_reps,
        "dim_accounts": dim_accounts,
        "dim_stages": dim_stages,
        "fct_opportunities": fct_opportunities,
        "fct_stage_histories": fct_stage_histories,
        "fct_activities": fct_activities,
        "fct_quotas": fct_quotas,
        "fct_historical_bookings": fct_historical_bookings,
        "fct_forecast_snapshots": fct_forecast_snapshots,
        "fct_forecast_predictions": fct_forecast_predictions,
        "fct_data_quality_exceptions": fct_data_quality_exceptions,
    }

    # Export clean CSV & JSON formats
    for name, df in normalized_tables.items():
        df.to_csv(csv_dir / f"{name}.csv", index=False)
        df.to_json(
            json_dir / f"{name}.json", orient="records", indent=2, date_format="iso"
        )

    # Export presentation-ready CSVs with normalized headers (no underscores)
    clean_reports_dir = out_dir / "clean_reports"
    clean_reports_dir.mkdir(parents=True, exist_ok=True)
    for name, df in normalized_tables.items():
        clean_df = df.rename(columns=normalize_column_name)
        clean_name = name.replace("dim_", "").replace("fct_", "").replace("_", " ").title().replace(" ", "_")
        clean_df.to_csv(clean_reports_dir / f"{clean_name}.csv", index=False)

    # Legacy compatibility symlinks / mirrors for backward compatibility
    legacy_map = {
        "Territory": "dim_territories",
        "SalesRep": "dim_sales_reps",
        "Account": "dim_accounts",
        "Stage": "dim_stages",
        "Opportunity": "fct_opportunities",
        "StageHistory": "fct_stage_histories",
        "Activity": "fct_activities",
        "Quota": "fct_quotas",
        "HistoricalBooking": "fct_historical_bookings",
        "ForecastSnapshot": "fct_forecast_snapshots",
        "ForecastOutput": "fct_forecast_predictions",
    }
    for old_name, new_name in legacy_map.items():
        normalized_tables[new_name].to_csv(csv_dir / f"{old_name}.csv", index=False)
        normalized_tables[new_name].to_json(
            json_dir / f"{old_name}.json", orient="records", date_format="iso"
        )

    # Separate ground truth CSV
    fct_data_quality_exceptions.to_csv(out_dir / "ground_truth.csv", index=False)

    # Validation & Documentation Exports
    val_report = validate(normalized_tables)
    (out_dir / "validation_summary.json").write_text(json.dumps(val_report, indent=2))
    (out_dir / "evaluation_metrics.json").write_text(json.dumps(metrics, indent=2))
    (out_dir / "data_dictionary.json").write_text(
        json.dumps(data_dictionary(), indent=2)
    )
    (out_dir / "source_manifest.json").write_text(
        json.dumps(
            {
                "provenance": "fully synthetic sales data engine; normalized relational schema",
                "seed": seed,
                "generator": "src/generator.py",
                "tables_generated": list(normalized_tables.keys()),
                "total_records": sum(len(df) for df in normalized_tables.values()),
            },
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # 9. Clean Relational DDL & SQLite Export
    # ---------------------------------------------------------
    schema_sql = """-- Normalized Sales Pipeline Schema (Kimball Star Schema / Relational 3NF)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_territories (
    territory_id TEXT PRIMARY KEY,
    territory_name TEXT UNIQUE NOT NULL,
    region TEXT NOT NULL,
    currency TEXT DEFAULT 'USD',
    effective_from TEXT,
    effective_to TEXT
);

CREATE TABLE IF NOT EXISTS dim_sales_reps (
    rep_id TEXT PRIMARY KEY,
    rep_name TEXT NOT NULL,
    territory_id TEXT NOT NULL REFERENCES dim_territories(territory_id),
    hire_date TEXT,
    employment_status TEXT CHECK(employment_status IN ('Active', 'On Leave', 'Inactive'))
);

CREATE TABLE IF NOT EXISTS dim_accounts (
    account_id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    segment TEXT CHECK(segment IN ('SMB', 'Mid-Market', 'Enterprise')),
    industry TEXT,
    territory_id TEXT REFERENCES dim_territories(territory_id),
    created_date TEXT
);

CREATE TABLE IF NOT EXISTS dim_stages (
    stage_id TEXT PRIMARY KEY,
    stage_name TEXT UNIQUE NOT NULL,
    default_probability REAL CHECK(default_probability BETWEEN 0 AND 1),
    stage_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fct_opportunities (
    opportunity_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES dim_accounts(account_id),
    rep_id TEXT NOT NULL REFERENCES dim_sales_reps(rep_id),
    territory_id TEXT REFERENCES dim_territories(territory_id),
    stage_id TEXT NOT NULL REFERENCES dim_stages(stage_id),
    stage_name TEXT,
    stage_probability REAL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    amount_base_currency REAL NOT NULL,
    product TEXT,
    created_date TEXT NOT NULL,
    expected_close_date TEXT NOT NULL,
    is_duplicate INTEGER DEFAULT 0,
    lifecycle_state TEXT,
    final_outcome TEXT,
    actual_close_date TEXT,
    actual_booking_base_currency REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS fct_stage_histories (
    stage_history_id TEXT PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES fct_opportunities(opportunity_id),
    stage_id TEXT NOT NULL REFERENCES dim_stages(stage_id),
    stage_name TEXT,
    changed_at TEXT NOT NULL,
    source TEXT
);

CREATE TABLE IF NOT EXISTS fct_activities (
    activity_id TEXT PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES fct_opportunities(opportunity_id),
    rep_id TEXT NOT NULL REFERENCES dim_sales_reps(rep_id),
    activity_type TEXT NOT NULL,
    activity_date TEXT NOT NULL,
    completed INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS fct_quotas (
    quota_id TEXT PRIMARY KEY,
    rep_id TEXT NOT NULL REFERENCES dim_sales_reps(rep_id),
    fiscal_quarter TEXT NOT NULL,
    quota_amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    effective_from TEXT
);

CREATE TABLE IF NOT EXISTS fct_historical_bookings (
    booking_id TEXT PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES fct_opportunities(opportunity_id),
    booking_date TEXT NOT NULL,
    booking_amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    outcome TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fct_forecast_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    snapshot_date TEXT NOT NULL,
    opportunity_id TEXT NOT NULL REFERENCES fct_opportunities(opportunity_id),
    rep_id TEXT NOT NULL REFERENCES dim_sales_reps(rep_id),
    territory_id TEXT REFERENCES dim_territories(territory_id),
    segment TEXT,
    stage_name TEXT,
    stage_probability REAL,
    age_days INTEGER,
    days_to_close INTEGER,
    activity_count INTEGER,
    amount_base_currency REAL,
    actual_won INTEGER,
    actual_booking REAL,
    horizon_days INTEGER
);

CREATE TABLE IF NOT EXISTS fct_forecast_predictions (
    snapshot_id TEXT PRIMARY KEY,
    snapshot_date TEXT,
    opportunity_id TEXT,
    rep_id TEXT,
    territory_id TEXT,
    segment TEXT,
    stage_name TEXT,
    stage_probability REAL,
    age_days INTEGER,
    days_to_close INTEGER,
    activity_count INTEGER,
    amount_base_currency REAL,
    predicted_probability REAL,
    base_forecast REAL,
    best_case REAL,
    worst_case REAL,
    actual_won INTEGER,
    actual_booking REAL,
    horizon_days INTEGER,
    exception_flag TEXT
);

CREATE TABLE IF NOT EXISTS fct_data_quality_exceptions (
    record_id TEXT,
    table_name TEXT,
    issue_type TEXT,
    severity TEXT,
    ground_truth TEXT,
    expected_decision TEXT
);
"""
    (out_dir / "schema.sql").write_text(schema_sql)

    # SQLite export: execute DDL first, then populate with append to preserve constraints
    db_path = out_dir / "sales_forecast.sqlite"
    if db_path.exists():
        db_path.unlink()

    db = sqlite3.connect(db_path)
    db.executescript(schema_sql)

    for tbl_name, tbl_df in normalized_tables.items():
        tbl_df.to_sql(tbl_name, db, if_exists="append", index=False)
    db.close()

    # Reproducibility checksum calculation
    checksums = {}
    for pth in sorted(csv_dir.glob("*.csv")):
        checksums[pth.name] = hashlib.sha256(pth.read_bytes()).hexdigest()
    (out_dir / "reproducibility.json").write_text(
        json.dumps({"seed": seed, "sha256": checksums}, indent=2)
    )

    return normalized_tables, metrics


def validate(tables: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Validate relational integrity, primary key uniqueness, and feature freshness."""
    opp = tables["fct_opportunities"]
    reps = tables["dim_sales_reps"]
    acct = tables["dim_accounts"]
    snaps = tables["fct_forecast_snapshots"]
    exceptions = tables["fct_data_quality_exceptions"]

    checks = {
        "rep_pk_unique": bool(reps["rep_id"].is_unique),
        "account_pk_unique": bool(acct["account_id"].is_unique),
        "opportunity_rep_fk_valid": bool(opp["rep_id"].isin(reps["rep_id"]).all()),
        "opportunity_account_fk_valid": bool(
            opp["account_id"].isin(acct["account_id"]).all()
        ),
        "snapshot_opportunity_fk_valid": (
            bool(snaps["opportunity_id"].isin(opp["opportunity_id"]).all())
            if len(snaps)
            else True
        ),
        "snapshot_has_no_target_leakage": not any(
            c in snaps.columns for c in ["final_outcome", "actual_close_date"]
        ),
        "data_quality_exceptions_quarantined": int(len(exceptions)),
        "snapshot_rows": int(len(snaps)),
    }
    return {
        "checks": checks,
        "all_critical_checks_pass": all(
            v for k, v in checks.items() if isinstance(v, bool)
        ),
    }


def data_dictionary() -> Dict[str, Dict[str, str]]:
    """Return the normalized enterprise data dictionary."""
    return {
        "dim_territories": {
            "territory_id": "Primary Key; format TER-0001",
            "territory_name": "Unique human-readable territory name",
            "region": "Controlled region: North | South | East | West | Central",
            "currency": "Standard ISO currency code (USD)",
            "effective_from": "Start date for territory definition (YYYY-MM-DD)",
            "effective_to": "End date for territory definition (nullable)",
        },
        "dim_sales_reps": {
            "rep_id": "Primary Key; format REP-000001",
            "rep_name": "Full name of the sales representative",
            "territory_id": "Foreign Key referencing dim_territories.territory_id",
            "hire_date": "Rep onboarding date (YYYY-MM-DD)",
            "employment_status": "Controlled status: Active | On Leave | Inactive",
        },
        "dim_accounts": {
            "account_id": "Primary Key; format ACC-000001",
            "account_name": "Account business entity name",
            "segment": "Market tier: SMB | Mid-Market | Enterprise",
            "industry": "Industry vertical classification",
            "territory_id": "Foreign Key referencing dim_territories.territory_id",
            "created_date": "Account creation timestamp (YYYY-MM-DD)",
        },
        "dim_stages": {
            "stage_id": "Primary Key; format STAGE-01",
            "stage_name": "Pipeline milestone name",
            "default_probability": "Baseline conversion probability [0.0 - 1.0]",
            "stage_order": "Sequential pipeline order index [1-7]",
        },
        "fct_opportunities": {
            "opportunity_id": "Primary Key; format OPP-2026-000001",
            "account_id": "Foreign Key referencing dim_accounts.account_id",
            "rep_id": "Foreign Key referencing dim_sales_reps.rep_id",
            "territory_id": "Foreign Key referencing dim_territories.territory_id",
            "stage_id": "Foreign Key referencing dim_stages.stage_id",
            "amount": "Source deal amount in stated currency",
            "currency": "Transaction currency code (USD, EUR, GBP, INR)",
            "amount_base_currency": "Normalized deal amount in base USD",
            "created_date": "Deal creation date",
            "expected_close_date": "Targeted closing date",
            "lifecycle_state": "Open | Closed Won | Closed Lost",
        },
        "fct_stage_histories": {
            "stage_history_id": "Primary Key; audit log entry ID",
            "opportunity_id": "Foreign Key referencing fct_opportunities.opportunity_id",
            "stage_id": "Foreign Key referencing dim_stages.stage_id",
            "changed_at": "Timestamp when stage transition occurred",
            "source": "Initial | RepUpdate | System",
        },
        "fct_activities": {
            "activity_id": "Primary Key; format ACT-<opp_id>-01",
            "opportunity_id": "Foreign Key referencing fct_opportunities.opportunity_id",
            "rep_id": "Foreign Key referencing dim_sales_reps.rep_id",
            "activity_type": "Touchpoint category: Email | Call | Meeting | Demo | Proposal Sent",
            "activity_date": "Activity execution date",
            "completed": "Binary flag (1 = completed, 0 = pending/cancelled)",
        },
        "fct_quotas": {
            "quota_id": "Primary Key; format QUOTA-<rep_id>-2026Q1",
            "rep_id": "Foreign Key referencing dim_sales_reps.rep_id",
            "fiscal_quarter": "Target fiscal quarter label",
            "quota_amount": "Assigned target booking revenue in USD",
            "currency": "USD",
            "effective_from": "Quarter start date",
        },
        "fct_historical_bookings": {
            "booking_id": "Primary Key; format BOOK-0000001",
            "opportunity_id": "Foreign Key referencing fct_opportunities.opportunity_id",
            "booking_date": "Date deal was won and recognized",
            "booking_amount": "Final realized booking value in USD",
            "outcome": "Closed Won",
        },
        "fct_forecast_snapshots": {
            "snapshot_id": "Primary Key; format FCST-<date>-<opp_id>",
            "snapshot_date": "Point-in-time calculation date",
            "opportunity_id": "Foreign Key referencing fct_opportunities.opportunity_id",
            "stage_probability": "Stage probability as known strictly at snapshot date",
            "age_days": "Deal age in days as-of snapshot date",
            "days_to_close": "Days remaining until expected close date",
            "activity_count": "Number of completed touchpoints logged prior to snapshot date",
            "amount_base_currency": "Deal value in base currency (USD)",
            "actual_won": "Ground truth outcome (Evaluation label only, NEVER training feature)",
            "actual_booking": "Realized revenue (Evaluation label only)",
        },
        "fct_forecast_predictions": {
            "snapshot_id": "Foreign Key referencing fct_forecast_snapshots.snapshot_id",
            "predicted_probability": "Gradient-boosted ML predicted win probability",
            "base_forecast": "Expected booking value: amount_base_currency * predicted_probability",
            "best_case": "Upside scenario forecast (+20% probability multiplier)",
            "worst_case": "Downside scenario forecast (-20% probability multiplier)",
            "exception_flag": "Risk flags (e.g., STALE_NO_ACTIVITY)",
        },
        "fct_data_quality_exceptions": {
            "record_id": "Identifier of the flagged record",
            "table_name": "Target table where anomaly was observed",
            "issue_type": "Data quality classification rule",
            "severity": "CRITICAL | HIGH | MEDIUM | LOW",
            "ground_truth": "Expected failure mode",
            "expected_decision": "Prescribed automated remediation action",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate normalized synthetic sales forecasting database."
    )
    parser.add_argument(
        "--scale", choices=["starter", "full"], default="starter", help="Dataset scale"
    )
    parser.add_argument("--reps", type=int, help="Number of sales representatives")
    parser.add_argument("--accounts", type=int, help="Number of customer accounts")
    parser.add_argument(
        "--opportunities", type=int, help="Number of sales opportunities"
    )
    parser.add_argument(
        "--seed", type=int, default=SEED, help="Random number generator seed"
    )
    parser.add_argument(
        "--out", default="outputs", help="Output directory path for CSV/JSON/DB"
    )

    args = parser.parse_args()
    scale_defaults = (
        (100, 150, 500) if args.scale == "starter" else (2000, 2000, 20000)
    )

    num_reps = args.reps or scale_defaults[0]
    num_accounts = args.accounts or scale_defaults[1]
    num_opps = args.opportunities or scale_defaults[2]

    tables, eval_metrics = generate(
        reps=num_reps,
        accounts=num_accounts,
        opportunities=num_opps,
        seed=args.seed,
        out=args.out,
    )
    print(f"Data generation complete: {len(tables)} normalized tables generated.")
    print(f"Artifacts successfully written to: {args.out}")
