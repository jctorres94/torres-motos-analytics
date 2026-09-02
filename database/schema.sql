CREATE TABLE IF NOT EXISTS dim_plataforma (
    id_plataforma SERIAL PRIMARY KEY,
    nome_plataforma VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_veiculo (
    id_veiculo SERIAL PRIMARY KEY,
    modelo_veiculo VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL DEFAULT 'Motocicleta'
);

CREATE TABLE IF NOT EXISTS dim_tempo (
    data DATE PRIMARY KEY,
    ano SMALLINT NOT NULL CHECK (ano >= 2000),
    mes SMALLINT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    nome_mes VARCHAR(20) NOT NULL,
    trimestre SMALLINT NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    dia_semana VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_desempenho_midia (
    id_fato_midia BIGSERIAL PRIMARY KEY,
    data DATE NOT NULL REFERENCES dim_tempo(data),
    id_plataforma INT NOT NULL REFERENCES dim_plataforma(id_plataforma),
    id_veiculo INT NOT NULL REFERENCES dim_veiculo(id_veiculo),
    impressoes INT NOT NULL CHECK (impressoes >= 0),
    cliques INT NOT NULL CHECK (cliques BETWEEN 0 AND impressoes),
    custo_brl NUMERIC(12, 2) NOT NULL CHECK (custo_brl >= 0),
    leads INT NOT NULL CHECK (leads BETWEEN 0 AND cliques),
    UNIQUE (data, id_plataforma, id_veiculo)
);

CREATE TABLE IF NOT EXISTS fato_funil_crm (
    id_lead VARCHAR(20) PRIMARY KEY,
    data DATE NOT NULL REFERENCES dim_tempo(data),
    id_plataforma INT NOT NULL REFERENCES dim_plataforma(id_plataforma),
    id_veiculo INT NOT NULL REFERENCES dim_veiculo(id_veiculo),
    test_drive BOOLEAN NOT NULL,
    venda_concluida BOOLEAN NOT NULL,
    valor_venda NUMERIC(12, 2) NOT NULL DEFAULT 0,
    CHECK (test_drive OR NOT venda_concluida),
    CHECK (
        (venda_concluida AND valor_venda > 0)
        OR (NOT venda_concluida AND valor_venda = 0)
    )
);

CREATE INDEX IF NOT EXISTS idx_midia_data ON fato_desempenho_midia(data);
CREATE INDEX IF NOT EXISTS idx_midia_plataforma ON fato_desempenho_midia(id_plataforma);
CREATE INDEX IF NOT EXISTS idx_crm_data ON fato_funil_crm(data);
CREATE INDEX IF NOT EXISTS idx_crm_plataforma ON fato_funil_crm(id_plataforma);
CREATE INDEX IF NOT EXISTS idx_crm_veiculo ON fato_funil_crm(id_veiculo);
