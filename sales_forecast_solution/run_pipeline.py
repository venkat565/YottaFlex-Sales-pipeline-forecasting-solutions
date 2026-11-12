"""Pipeline runner script for synthetic sales forecasting generation."""

import argparse
import sys
from pathlib import Path

# Set script and project directories
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from generator import generate  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run synthetic sales pipeline generation and ML forecasting."
    )
    parser.add_argument(
        "--scale",
        choices=["starter", "full"],
        default="starter",
        help="Select scale: starter (fast smoke test) or full (enterprise volume)",
    )
    parser.add_argument("--reps", type=int, help="Override number of sales reps")
    parser.add_argument("--accounts", type=int, help="Override number of accounts")
    parser.add_argument(
        "--opportunities", type=int, help="Override number of opportunities"
    )
    parser.add_argument(
        "--seed", type=int, default=20261022, help="Fixed random seed"
    )
    parser.add_argument(
        "--out",
        default=str(PROJECT_DIR / "outputs"),
        help="Output directory for generated data (defaults to sales_forecast_solution/outputs)",
    )

    args = parser.parse_args()
    defaults = (
        (100, 150, 500) if args.scale == "starter" else (2000, 2000, 20000)
    )

    reps = args.reps or defaults[0]
    accounts = args.accounts or defaults[1]
    opps = args.opportunities or defaults[2]

    print(
        f"Starting pipeline [Scale: {args.scale} | Reps: {reps} | Accounts: {accounts} | Opps: {opps}]..."
    )
    tables, metrics = generate(
        reps=reps,
        accounts=accounts,
        opportunities=opps,
        seed=args.seed,
        out=args.out,
    )

    print("\n Pipeline completed successfully!")
    print(f" Normalized tables created: {len(tables)}")
    print(f" SQLite Database: {Path(args.out) / 'sales_forecast.sqlite'}")
    print(f" CSV and JSON artifacts written to '{args.out}'.")
    if "brier_score" in metrics and metrics["brier_score"] is not None:
        print(f" Model Brier Score: {metrics['brier_score']}")
        print(f" Model ROC-AUC:     {metrics.get('roc_auc', 'N/A')}")
        print(f" Forecast WAPE:     {metrics.get('booking_wape', 'N/A')}")


if __name__ == "__main__":
    main()
