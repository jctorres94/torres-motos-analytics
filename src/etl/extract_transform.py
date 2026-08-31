import pandas as pd
import numpy as np
from datetime import datetime

# Configuração de semente para reprodutibilidade dos dados
np.random.seed(42)

def generate_torres_motors_data():
    """Gera dados brutos simulados de Mídia (Meta/Google Ads) e CRM para a Torres Motors."""
    dates = pd.date_range(start="2026-01-01", end="2026-08-30", freq="D")
    platforms = ["Meta Ads", "Google Ads"]
    models = ["Yamaha MT-07", "Yamaha NMAX 160", "Yamaha Crosser 150", "Yamaha Fazer 250"]
    
    ads_records = []
    crm_records = []
    lead_id = 1000
    
    for date in dates:
        for platform in platforms:
            for model in models:
                impressions = np.random.randint(1000, 10000)
                clicks = int(impressions * np.random.uniform(0.02, 0.08))
                cost = round(clicks * np.random.uniform(1.2, 4.5), 2)
                leads = int(clicks * np.random.uniform(0.05, 0.15))
                
                ads_records.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "platform": platform,
                    "vehicle_model": model,
                    "impressions": impressions,
                    "clicks": clicks,
                    "cost_brl": cost,
                    "leads": leads
                })
                
                # Conversões no CRM a partir dos leads gerados
                for _ in range(leads):
                    lead_id += 1
                    test_drive = np.random.choice([True, False], p=[0.35, 0.65])
                    sale = np.random.choice([True, False], p=[0.25, 0.75]) if test_drive else False
                    
                    prices = {
                        "Yamaha MT-07": 46000, 
                        "Yamaha NMAX 160": 21000, 
                        "Yamaha Crosser 150": 20000, 
                        "Yamaha Fazer 250": 23000
                    }
                    sale_value = prices[model] if sale else 0

                    crm_records.append({
                        "lead_id": f"TLD-{lead_id}",
                        "date": date.strftime("%Y-%m-%d"),
                        "platform": platform,
                        "vehicle_model": model,
                        "test_drive": test_drive,
                        "sale_completed": sale,
                        "sale_value": sale_value
                    })

    df_ads = pd.DataFrame(ads_records)
    df_crm = pd.DataFrame(crm_records)
    
    # Salvar dados brutos na pasta data/raw
    df_ads.to_csv("data/raw/raw_marketing_ads.csv", index=False)
    df_crm.to_csv("data/raw/raw_crm_sales.csv", index=False)
    
    print("✓ [Torres Motors] Dados de Mídia gerados: data/raw/raw_marketing_ads.csv")
    print("✓ [Torres Motors] Dados de CRM gerados: data/raw/raw_crm_sales.csv")

if __name__ == "__main__":
    generate_torres_motors_data()