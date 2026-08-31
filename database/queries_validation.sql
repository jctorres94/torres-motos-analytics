-- VALIDAÇÃO DO FUNIL DE VENDAS E ROI POR PLATAFORMA (TORRES MOTORS)
SELECT 
    p.nome_plataforma,
    SUM(m.custo_brl) AS investimento_total,
    SUM(m.leads) AS total_leads,
    COUNT(c.id_lead) FILTER (WHERE c.test_drive = TRUE) AS total_test_drives,
    COUNT(c.id_lead) FILTER (WHERE c.venda_concluida = TRUE) AS total_vendas,
    SUM(c.valor_venda) AS receita_total,
    ROUND((SUM(c.valor_venda) / NULLIF(SUM(m.custo_brl), 0)), 2) AS roas
FROM dim_plataforma p
LEFT JOIN fato_desempenho_midia m ON p.id_plataforma = m.id_plataforma
LEFT JOIN fato_funil_crm c ON p.id_plataforma = c.id_plataforma
GROUP BY p.nome_plataforma;