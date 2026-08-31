import pandas as pd
from sqlalchemy import create_engine

# String de Conexão do PostgreSQL (Ajuste usuário, senha e porta conforme seu banco)
DB_URL = "postgresql://postgres:postgres@localhost:5432/torres_motors_db"

def run_database_pipeline():
    try:
        engine = create_engine(DB_URL)
        print("✓ Conexão estabelecida com o PostgreSQL.")
        
        # 1. Leitura dos CSVs brutos
        df_ads = pd.read_csv("data/raw/raw_marketing_ads.csv")
        df_crm = pd.read_csv("data/raw/raw_crm_sales.csv")
        
        # 2. Carga Dimensão Plataforma
        platforms = pd.DataFrame({"nome_plataforma": df_ads["platform"].unique()})
        platforms.to_sql("dim_plataforma", engine, if_exists="append", index=False)
        print("✓ Tabela 'dim_plataforma' populada.")

        # 3. Carga Dimensão Veículo
        models = pd.DataFrame({"modelo_veiculo": df_ads["vehicle_model"].unique()})
        models.to_sql("dim_veiculo", engine, if_exists="append", index=False)
        print("✓ Tabela 'dim_veiculo' populada.")

        # 4. Carga Dimensão Tempo
        df_ads['date'] = pd.to_datetime(df_ads['date'])
        dates = pd.date_range(start=df_ads['date'].min(), end=df_ads['date'].max())
        dim_tempo = pd.DataFrame({
            "data": dates,
            "ano": dates.year,
            "mes": dates.month,
            "nome_mes": dates.strftime("%B"),
            "trimestre": dates.quarter,
            "dia_semana": dates.strftime("%A")
        })
        dim_tempo.to_sql("dim_tempo", engine, if_exists="append", index=False)
        print("✓ Tabela 'dim_tempo' populada.")

        # 5. Mapeamento e Carga Fato Desempenho Mídia
        df_platforms_db = pd.read_sql("SELECT * FROM dim_plataforma", engine)
        df_models_db = pd.read_sql("SELECT * FROM dim_veiculo", engine)
        
        map_platform = dict(zip(df_platforms_db['nome_plataforma'], df_platforms_db['id_plataforma']))
        map_model = dict(zip(df_models_db['modelo_veiculo'], df_models_db['id_veiculo']))
        
        df_ads['id_plataforma'] = df_ads['platform'].map(map_platform)
        df_ads['id_veiculo'] = df_ads['vehicle_model'].map(map_model)
        
        fato_midia = df_ads[['date', 'id_plataforma', 'id_veiculo', 'impressions', 'clicks', 'cost_brl', 'leads']]
        fato_midia.columns = ['data', 'id_plataforma', 'id_veiculo', 'impressoes', 'cliques', 'custo_brl', 'leads']
        fato_midia.to_sql("fato_desempenho_midia", engine, if_exists="append", index=False)
        print("✓ Tabela 'fato_desempenho_midia' populada.")

        # 6. Mapeamento e Carga Fato Funil CRM
        df_crm['id_plataforma'] = df_crm['platform'].map(map_platform)
        df_crm['id_veiculo'] = df_crm['vehicle_model'].map(map_model)
        
        fato_crm = df_crm[['lead_id', 'date', 'id_plataforma', 'id_veiculo', 'test_drive', 'sale_completed', 'sale_value']]
        fato_crm.columns = ['id_lead', 'data', 'id_plataforma', 'id_veiculo', 'test_drive', 'venda_concluida', 'valor_venda']
        fato_crm.to_sql("fato_funil_crm", engine, if_exists="append", index=False)
        print("✓ Tabela 'fato_funil_crm' populada com sucesso.")
        
    except Exception as e:
        print(f"❌ Erro ao executar o pipeline de banco de dados: {e}")

if __name__ == "__main__":
    run_database_pipeline()