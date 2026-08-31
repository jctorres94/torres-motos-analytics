-- SCHEMA TORRES MOTORS ANALYTICS (STAR SCHEMA)

-- Drop de tabelas existentes para recriação limpa (caso necessário)
DROP TABLE IF EXISTS fato_funil_crm CASCADE;
DROP TABLE IF EXISTS fato_desempenho_midia CASCADE;
DROP TABLE IF EXISTS dim_tempo CASCADE;
DROP TABLE IF EXISTS dim_veiculo CASCADE;
DROP TABLE IF EXISTS dim_plataforma CASCADE;

-- 1. Tabelas Dimensionais
CREATE TABLE dim_plataforma (
    id_plataforma SERIAL PRIMARY KEY,
    nome_plataforma VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE dim_veiculo (
    id_veiculo SERIAL PRIMARY KEY,
    modelo_veiculo VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(50) DEFAULT 'Motocicleta'
);

CREATE TABLE dim_tempo (
    data DATE PRIMARY KEY,
    ano INT NOT NULL,
    mes INT NOT NULL,
    nome_mes VARCHAR(20) NOT NULL,
    trimestre INT NOT NULL,
    dia_semana VARCHAR(20) NOT NULL
);

-- 2. Tabelas Fato
CREATE TABLE fato_desempenho_midia (
    id_fato_midia SERIAL PRIMARY KEY,
    data DATE REFERENCES dim_tempo(data),
    id_plataforma INT REFERENCES dim_plataforma(id_plataforma),
    id_veiculo INT REFERENCES dim_veiculo(id_veiculo),
    impressoes INT NOT NULL,
    cliques INT NOT NULL,
    custo_brl NUMERIC(10, 2) NOT NULL,
    leads INT NOT NULL
);

CREATE TABLE fato_funil_crm (
    id_lead VARCHAR(20) PRIMARY KEY,
    data DATE REFERENCES dim_tempo(data),
    id_plataforma INT REFERENCES dim_plataforma(id_plataforma),
    id_veiculo INT REFERENCES dim_veiculo(id_veiculo),
    test_drive BOOLEAN NOT NULL,
    venda_concluida BOOLEAN NOT NULL,
    valor_venda NUMERIC(10, 2) DEFAULT 0.00
);