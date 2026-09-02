from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_validation_query_preaggregates_facts() -> None:
    query = (ROOT / "database" / "queries_validation.sql").read_text().lower()
    assert "with midia as" in query
    assert "crm as" in query
    assert "group by id_plataforma" in query
    assert "left join midia" in query
    assert "left join crm" in query


def test_schema_has_core_quality_constraints() -> None:
    schema = (ROOT / "database" / "schema.sql").read_text().lower()
    assert "unique (data, id_plataforma, id_veiculo)" in schema
    assert "cliques between 0 and impressoes" in schema
    assert "leads between 0 and cliques" in schema
    assert "test_drive or not venda_concluida" in schema
