from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"

PLATFORMS = ("Meta Ads", "Google Ads")
VEHICLE_PRICES = {
    "Yamaha MT-07": 46_000,
    "Yamaha NMAX 160": 21_000,
    "Yamaha Crosser 150": 20_000,
    "Yamaha Fazer 250": 23_000,
}


def generate_torres_motos_data(
    start_date: str = "2026-01-01",
    end_date: str = "2026-08-30",
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate reproducible synthetic media and CRM data."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    ads_records: list[dict[str, object]] = []
    crm_records: list[dict[str, object]] = []
    lead_id = 1000

    for date in dates:
        for platform in PLATFORMS:
            for model, price in VEHICLE_PRICES.items():
                impressions = int(rng.integers(1_000, 10_000))
                clicks = int(impressions * rng.uniform(0.02, 0.08))
                cost = round(clicks * rng.uniform(1.2, 4.5), 2)
                leads = int(clicks * rng.uniform(0.05, 0.15))

                ads_records.append(
                    {
                        "date": date.date().isoformat(),
                        "platform": platform,
                        "vehicle_model": model,
                        "impressions": impressions,
                        "clicks": clicks,
                        "cost_brl": cost,
                        "leads": leads,
                    }
                )

                for _ in range(leads):
                    lead_id += 1
                    test_drive = bool(rng.random() < 0.35)
                    sale_completed = bool(test_drive and rng.random() < 0.25)
                    crm_records.append(
                        {
                            "lead_id": f"TLD-{lead_id}",
                            "date": date.date().isoformat(),
                            "platform": platform,
                            "vehicle_model": model,
                            "test_drive": test_drive,
                            "sale_completed": sale_completed,
                            "sale_value": price if sale_completed else 0,
                        }
                    )

    ads = pd.DataFrame(ads_records)
    crm = pd.DataFrame(crm_records)
    validate_generated_data(ads, crm)
    return ads, crm


def validate_generated_data(ads: pd.DataFrame, crm: pd.DataFrame) -> None:
    """Fail fast when the synthetic funnel violates its business rules."""
    if len(crm) != int(ads["leads"].sum()):
        raise ValueError("CRM rows must equal the number of generated leads.")
    if not (ads["clicks"] <= ads["impressions"]).all():
        raise ValueError("Clicks cannot exceed impressions.")
    if not (ads["leads"] <= ads["clicks"]).all():
        raise ValueError("Leads cannot exceed clicks.")
    if (crm["sale_completed"] & ~crm["test_drive"]).any():
        raise ValueError("A sale cannot occur without a test drive.")
    expected_positive_value = crm["sale_completed"] == (crm["sale_value"] > 0)
    if not expected_positive_value.all():
        raise ValueError("Only completed sales may have a positive sale value.")


def write_raw_data(
    ads: pd.DataFrame,
    crm: pd.DataFrame,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ads_path = output_dir / "raw_marketing_ads.csv"
    crm_path = output_dir / "raw_crm_sales.csv"
    ads.to_csv(ads_path, index=False)
    crm.to_csv(crm_path, index=False)
    return ads_path, crm_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Torres Motos data.")
    parser.add_argument("--start-date", default="2026-01-01")
    parser.add_argument("--end-date", default="2026-08-30")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    ads, crm = generate_torres_motos_data(args.start_date, args.end_date, args.seed)
    ads_path, crm_path = write_raw_data(ads, crm, args.output_dir)
    print(f"Generated {len(ads):,} media rows at {ads_path}")
    print(f"Generated {len(crm):,} CRM rows at {crm_path}")


if __name__ == "__main__":
    main()
