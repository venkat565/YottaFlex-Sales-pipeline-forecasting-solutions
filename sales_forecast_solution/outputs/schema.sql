-- Normalized Sales Pipeline Schema (Kimball Star Schema / Relational 3NF)
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
