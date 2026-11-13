# YottaFlex AI Recruitment Drive — Prompt History & AI Transparency Log

**Candidate Project:** Sales Pipeline Forecasting & Scenario Analysis Solution  
**Challenge Window:** 72 Hours • Transparent AI Use • Individual Work  
**Repository:** Public Submission  

---

## 1. Executive Disclosure (YottaFlex Guideline 03 Compliance)

In accordance with YottaFlex AI Candidate Project Guidelines (**Pillar 03: Use LLMs Transparently**), this document records the complete prompt history, AI tool acceleration areas, and human validation actions taken throughout the development lifecycle of this project.

### Tools Used
- **Primary AI Coding Assistant:** Google DeepMind Antigravity (powered by Gemini & Claude models)
- **Primary Interface:** Antigravity Agentic IDE & Terminal CLI

### AI Acceleration vs. Human Ownership Breakdown
| Development Phase | What AI Accelerated | What Human Candidate Reviewed, Validated & Corrected |
| :--- | :--- | :--- |
| **Data Architecture & Schema** | Boilerplate Kimball Star Schema generation (`dim_`, `fct_`), initial DDL structure. | Validated zero broken foreign keys, ensured point-in-time snapshot integrity without future leakage, checked 10 required entity relationships. |
| **Synthetic Generator Logic** | Generation scripts for 2,000 reps, 2,000 accounts, 20,000 opportunities with seed `20261022`. | Verified 8 quarterly snapshot dates, ensured deterministic zero-padded IDs (`REP-000001`, `OPP-2026-000001`), validated statistical distributions. |
| **Edge-Case Quarantine** | Scripting of deliberate anomalies into `ground_truth.csv`. | Inspected and confirmed all 5 required edge cases (target leakage, probability mismatch, duplicate deal, date order inversion, mixed currency) are properly quarantined. |
| **Machine Learning Forecasting** | Feature matrix assembly, HistGradientBoosting training boilerplate. | Validated Brier score (0.166), ROC-AUC (0.833), and WAPE metrics; verified scenario spread calculations (+20% Best, -20% Worst). |
| **Frontend UI (HTML & Mantine)** | HTML/CSS layout, Mantine DoubleNavbar structure, Tabler icons. | Normalized table headers (removed raw underscores), standardized all 4 KPI cards to identical size and shape, adjusted progress bar colors to green. |
| **Streamlit Dashboard** | Multi-tab dashboard layout with Plotly visualization. | Removed raw CSS text leaks from Streamlit markdown parser, restored normal toolbar behavior on hover, eliminated unwanted info boxes. |
| **Repository Hygiene** | Identifying accidental root `.git` initialization in user home folder. | Successfully detached home directory Git tracking and initialized clean project repository with strict `.gitignore`. |

---

## 2. Chronological Prompt & Instruction Log

The following chronological log details every major prompt, steering instruction, and refinement directive issued to the AI during the project:

### Phase A: Architecture, Schema & Synthetic Data Pipeline
* **Prompt 1 (Problem Setup):**
  > *"Build a working solution for this end-to-end workflow: Forecast bookings from opportunity stages, age, historical conversion and rep activity with scenario-based uncertainty. The solution should expose key decisions and exceptions, preserve traceability, and produce measurable outputs. Core entities: SalesRep, Territory, Account, Opportunity, Stage, StageHistory, Activity, Quota, HistoricalBooking, ForecastSnapshot. Define deterministic IDs, Kimball Star Schema, and parameterize scale for starter and full volume (2,000 reps/accounts, 20,000 opportunities, 8 quarters)."*
  * *Result:* Scaffolded `generator.py`, `config.py`, and `run_pipeline.py` with 10 core relational tables and SQLite integration.

* **Prompt 2 (Edge Case Ingestion & Ground Truth):**
  > *"Generate valid baseline records first, then inject labelled edge cases: Forecast uses final outcome data; stage probability inconsistent with snapshot; duplicate opportunity counted; close date before creation; currency totals mixed. Output a separate ground_truth.csv and never leak it into input features."*
  * *Result:* Created `fct_data_quality_exceptions` and isolated anomaly ground-truth records with expected remediation actions.

* **Prompt 3 (Reproducibility & Validation):**
  > *"Ensure the generator is fully reproducible using fixed seed 20261022. Export SHA-256 checksums and verification reports to reproducibility.json and validation_summary.json."*
  * *Result:* Implemented double-generation validation and deterministic hashing.

### Phase B: Frontend UI Redesign & Tabler Icons Integration
* **Prompt 4 (Mantine 7 DoubleNavbar Implementation):**
  > *"My navbar should look like this Mantine DoubleNavbar with icon rail and AI-inspired professional theme: [code snippet with Tooltip, UnstyledButton, and tab navigation]."*
  * *Result:* Created `DoubleNavbar.tsx` and `DoubleNavbar.module.css` with tab rail, active glow effects, and subnavigation panels.

* **Prompt 5 (Design System & Interactive HTML App):**
  > *"Need to add frontend design, create a file and attach this project. I need this HTML effects to my project and design: [HTML preview artifact]."*
  * *Result:* Implemented `frontend/index.html` replicating executive KPI cards, scenario spread chart, deal pipeline table, and star schema explorer.

* **Prompt 6 (Table Header Normalization & Schema Cleanup):**
  > *"Normalize the table header names because they have '_' underscores and also remove view SQL DDL schema in schema explorer."*
  * *Result:* Replaced raw snake_case database column names (`opportunity_id`, `anomaly_type`) with clean Title Case (`Opportunity ID`, `Anomaly Classification`) across both UI and CSV exports.

* **Prompt 7 (Tabler Icons Migration):**
  > *"Replace the icons into tabler icons. I need to change icons into tabler icons."*
  * *Result:* Swapped generic SVGs with authentic `@tabler/icons-webfont` (`ti ti-*`) in HTML and `@tabler/icons-react` in the React navbar.

### Phase C: Dashboard Polishing, Hover Effects & Card Uniformity
* **Prompt 8 (Card Hover & Light Blue Glow):**
  > *"Add hover to cards and shadow in light blue colour when hovers the card."*
  * *Result:* Updated `.card:hover` and `stMetric:hover` with a `-4px` 3D lift, `#60A5FA` accent border, and multi-layer light blue glow (`rgba(59, 130, 246, 0.25)`).

* **Prompt 9 (Equal Card Sizing & Shape):**
  > *"All KPI cards should be equal size and shape."*
  * *Result:* Configured `.g4` with `grid-template-columns: repeat(4, 1fr)`, `align-items: stretch`, `min-height: 135px`, and pinned card subtitles with `margin-top: auto` for uniform geometry.

* **Prompt 10 (Sidebar Cleanup):**
  > *"Remove this: [screenshot of '💡 Standalone interactive frontend available in frontend/index.html.']"*
  * *Result:* Removed the static callout box from the Streamlit sidebar.

* **Prompt 11 (Green Progress Bars):**
  > *"Replace the red to green colour: [screenshot of Win Probability progress bars in table]."*
  * *Result:* Configured `color="#10B981"` in `st.column_config.ProgressColumn` and rescaled deal win probabilities to 0–100% so progress bars render in clean emerald green with accurate labels.

* **Prompt 12 (Tab Styling Restoration):**
  > *"I am not asked for this to hover and light blue. Remove it and keep it normal: [screenshot of Plotly modebar]. Remove that dark mode, keep it normal."*
  * *Result:* Stripped aggressive button hover overrides that bled into Plotly chart tools; removed forced theme overrides to keep tabs and modebars natural.

### Phase D: Repository Scoping & Final Submission Audit
* **Prompt 13 (Git Scope Isolation):**
  > *"In my changed files I want only this project files only. Remove unwanted files except this project files."*
  * *Result:* Removed accidental root Git directory (`C:\Users\dell\.git`), initialized clean repository in `sales_pipeline_forecasting_solution`, and set up strict `.gitignore`.

* **Prompt 14 (Readiness Evaluation):**
  > *"According to these rules and regulations which I have given now, is my output OK or NOT? Can you make it ready for 100% submission?"*
  * *Result:* Completed compliance audit, generated full 20,000-opportunity enterprise dataset, finalized prompt history, and completed comprehensive README documentation.

---

## 3. Human Judgment & Decision Notes

1. **Model Architecture Selection:**
   - *Consideration:* Linear Logistic Regression vs. Random Forest vs. HistGradientBoosting.
   - *Decision:* Selected `HistGradientBoostingClassifier` with max bins and monotonic constraints because it handles mixed categorical/numerical tabular data natively and outputs superior Brier score probability calibration (0.166).

2. **Zero Target Leakage in Point-in-Time Snapshots:**
   - *Decision:* Strictly isolated snapshot feature generation from final deal outcome data (`actual_won`, `actual_booking`). Point-in-time features only use touchpoints and state transitions logged *on or before* the respective snapshot date.

3. **Data Quality Quarantine Strategy:**
   - *Decision:* Deliberate anomalies were routed to a dedicated `fct_data_quality_exceptions` fact table with explicit remediation decisions (`quarantine_and_flag`, `exclude_duplicate`) rather than silently dropping rows or polluting training distributions.

---

## 4. Verification & Attestation

The candidate confirms that:
- All source code, models, documentation, and synthetic data were generated and validated individually within the 72-hour recruitment challenge window.
- All dependencies are free, open-source, and locally runnable.
- No proprietary code, API keys, or private customer data are included in this repository.
