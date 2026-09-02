from pathlib import Path

import pandas as pd

from src.etl.extract_transform import generate_torres_motos_data, write_raw_data


def test_generation_is_reproducible() -> None:
    ads_a, crm_a = generate_torres_motos_data(
        "2026-01-01", "2026-01-03", seed=42
    )
    ads_b, crm_b = generate_torres_motos_data(
        "2026-01-01", "2026-01-03", seed=42
    )
    pd.testing.assert_frame_equal(ads_a, ads_b)
    pd.testing.assert_frame_equal(crm_a, crm_b)


def test_funnel_business_rules() -> None:
    ads, crm = generate_torres_motos_data("2026-01-01", "2026-01-10", seed=7)
    assert len(crm) == int(ads["leads"].sum())
    assert (ads["clicks"] <= ads["impressions"]).all()
    assert (ads["leads"] <= ads["clicks"]).all()
    assert not (crm["sale_completed"] & ~crm["test_drive"]).any()
    assert (crm.loc[crm["sale_completed"], "sale_value"] > 0).all()
    assert (crm.loc[~crm["sale_completed"], "sale_value"] == 0).all()


def test_csv_output(tmp_path: Path) -> None:
    ads, crm = generate_torres_motos_data("2026-01-01", "2026-01-02")
    ads_path, crm_path = write_raw_data(ads, crm, tmp_path)
    assert ads_path.exists()
    assert crm_path.exists()
    assert len(pd.read_csv(ads_path)) == len(ads)
    assert len(pd.read_csv(crm_path)) == len(crm)
