from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, create_engine, text

from src.etl.extract_transform import DEFAULT_OUTPUT_DIR, validate_generated_data


def get_database_url() -> str:
    try:
        return os.environ["DATABASE_URL"]
    except KeyError as exc:
        raise RuntimeError(
            "DATABASE_URL is required. Copy .env.example and export the variable."
        ) from exc


def read_raw_data(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    ads = pd.read_csv(raw_dir / "raw_marketing_ads.csv")
    crm = pd.read_csv(raw_dir / "raw_crm_sales.csv")
    ads["date"] = pd.to_datetime(ads["date"])
    crm["date"] = pd.to_datetime(crm["date"])
    validate_generated_data(ads, crm)
    return ads, crm


def build_dimensions(
    ads: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    platforms = pd.DataFrame(
        {"nome_plataforma": sorted(ads["platform"].dropna().unique())}
    )
    vehicles = pd.DataFrame(
        {
            "modelo_veiculo": sorted(ads["vehicle_model"].dropna().unique()),
            "categoria": "Motocicleta",
        }
    )
    dates = pd.date_range(ads["date"].min(), ads["date"].max(), freq="D")
    calendar = pd.DataFrame(
        {
            "data": dates,
            "ano": dates.year,
            "mes": dates.month,
            "nome_mes": dates.month_name(),
            "trimestre": dates.quarter,
            "dia_semana": dates.day_name(),
        }
    )
    return platforms, vehicles, calendar


def run_full_refresh(engine: Engine, raw_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    """Load a complete snapshot atomically and safely support reruns."""
    ads, crm = read_raw_data(raw_dir)
    platforms, vehicles, calendar = build_dimensions(ads)

    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE fato_funil_crm, fato_desempenho_midia, "
                "dim_tempo, dim_veiculo, dim_plataforma RESTART IDENTITY CASCADE"
            )
        )

        platforms.to_sql("dim_plataforma", connection, if_exists="append", index=False)
        vehicles.to_sql("dim_veiculo", connection, if_exists="append", index=False)
        calendar.to_sql("dim_tempo", connection, if_exists="append", index=False)

        db_platforms = pd.read_sql(
            "SELECT id_plataforma, nome_plataforma FROM dim_plataforma", connection
        )
        db_vehicles = pd.read_sql(
            "SELECT id_veiculo, modelo_veiculo FROM dim_veiculo", connection
        )
        platform_ids = dict(
            zip(db_platforms["nome_plataforma"], db_platforms["id_plataforma"])
        )
        vehicle_ids = dict(
            zip(db_vehicles["modelo_veiculo"], db_vehicles["id_veiculo"])
        )

        ads_fact = ads.assign(
            id_plataforma=ads["platform"].map(platform_ids),
            id_veiculo=ads["vehicle_model"].map(vehicle_ids),
        ).rename(
            columns={
                "date": "data",
                "impressions": "impressoes",
                "clicks": "cliques",
                "cost_brl": "custo_brl",
            }
        )
        ads_fact = ads_fact[
            [
                "data",
                "id_plataforma",
                "id_veiculo",
                "impressoes",
                "cliques",
                "custo_brl",
                "leads",
            ]
        ]

        crm_fact = crm.assign(
            id_plataforma=crm["platform"].map(platform_ids),
            id_veiculo=crm["vehicle_model"].map(vehicle_ids),
        ).rename(
            columns={
                "lead_id": "id_lead",
                "date": "data",
                "sale_completed": "venda_concluida",
                "sale_value": "valor_venda",
            }
        )
        crm_fact = crm_fact[
            [
                "id_lead",
                "data",
                "id_plataforma",
                "id_veiculo",
                "test_drive",
                "venda_concluida",
                "valor_venda",
            ]
        ]

        if ads_fact[["id_plataforma", "id_veiculo"]].isna().any().any():
            raise ValueError("Unmapped media dimension key detected.")
        if crm_fact[["id_plataforma", "id_veiculo"]].isna().any().any():
            raise ValueError("Unmapped CRM dimension key detected.")

        ads_fact.to_sql(
            "fato_desempenho_midia", connection, if_exists="append", index=False
        )
        crm_fact.to_sql("fato_funil_crm", connection, if_exists="append", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load Torres Motos data into PostgreSQL.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    engine = create_engine(get_database_url(), pool_pre_ping=True)
    try:
        run_full_refresh(engine, args.raw_dir)
        print("Full refresh completed successfully.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
