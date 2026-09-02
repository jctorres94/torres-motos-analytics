-- Aggregate each fact table at the requested grain before joining them.
-- Joining the raw facts directly would create a many-to-many fanout.
WITH midia AS (
    SELECT
        id_plataforma,
        SUM(impressoes) AS total_impressoes,
        SUM(cliques) AS total_cliques,
        SUM(custo_brl) AS investimento_total,
        SUM(leads) AS total_leads
    FROM fato_desempenho_midia
    GROUP BY id_plataforma
),
crm AS (
    SELECT
        id_plataforma,
        COUNT(*) FILTER (WHERE test_drive) AS total_test_drives,
        COUNT(*) FILTER (WHERE venda_concluida) AS total_vendas,
        SUM(valor_venda) AS receita_total
    FROM fato_funil_crm
    GROUP BY id_plataforma
)
SELECT
    p.nome_plataforma,
    COALESCE(m.total_impressoes, 0) AS total_impressoes,
    COALESCE(m.total_cliques, 0) AS total_cliques,
    COALESCE(m.investimento_total, 0) AS investimento_total,
    COALESCE(m.total_leads, 0) AS total_leads,
    COALESCE(c.total_test_drives, 0) AS total_test_drives,
    COALESCE(c.total_vendas, 0) AS total_vendas,
    COALESCE(c.receita_total, 0) AS receita_total,
    ROUND(c.receita_total / NULLIF(m.investimento_total, 0), 2) AS roas,
    ROUND(m.investimento_total / NULLIF(m.total_leads, 0), 2) AS custo_por_lead,
    ROUND(100.0 * c.total_vendas / NULLIF(m.total_leads, 0), 2) AS conversao_venda_pct
FROM dim_plataforma AS p
LEFT JOIN midia AS m USING (id_plataforma)
LEFT JOIN crm AS c USING (id_plataforma)
ORDER BY p.nome_plataforma;
