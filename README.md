# Torres Motos Analytics

Projeto de engenharia e análise de dados para simular o funil comercial de uma concessionária de motocicletas. O pipeline gera dados sintéticos e reproduzíveis de mídia e CRM, valida regras de negócio, carrega um modelo estrela no PostgreSQL e disponibiliza indicadores para análise no Power BI.

> Os dados deste repositório são totalmente simulados e não representam clientes ou operações reais.

## Arquitetura

```mermaid
flowchart LR
    A[Gerador Python] --> B[CSV de mídia e CRM]
    B --> C[Validações de qualidade]
    C --> D[ETL transacional]
    D --> E[(PostgreSQL)]
    E --> F[Power BI]
```

O modelo estrela possui três dimensões (`dim_tempo`, `dim_plataforma` e `dim_veiculo`) e duas tabelas fato (`fato_desempenho_midia` e `fato_funil_crm`).

## Indicadores

- Impressões, cliques, CTR e investimento em mídia
- Leads e custo por lead
- Test drives e taxa de avanço no funil
- Vendas, receita e ticket médio
- ROAS por plataforma
- Conversão de leads em vendas
- Desempenho por modelo de motocicleta e período

O cálculo de ROAS agrega cada tabela fato antes do `JOIN`, evitando multiplicação de valores em relações muitos-para-muitos.

## Tecnologias

- Python 3.12, Pandas e NumPy
- SQLAlchemy e psycopg2
- PostgreSQL 16
- Power BI
- Docker Compose
- Pytest e GitHub Actions

## Como executar

### 1. Preparar o ambiente

```bash
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\activate
```

No macOS ou Linux:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Configurar o PostgreSQL

Copie `.env.example` para `.env`, altere a senha e exporte `DATABASE_URL`. Para iniciar o banco com Docker:

```bash
docker compose up -d
```

O arquivo `database/schema.sql` é executado automaticamente na primeira criação do volume.

### 3. Gerar os dados

```bash
python -m src.etl.extract_transform
```

É possível alterar período, semente e pasta de saída:

```bash
python -m src.etl.extract_transform --start-date 2026-01-01 --end-date 2026-03-31 --seed 42
```

### 4. Carregar o banco

Linux/macOS:

```bash
export DATABASE_URL="postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/torres_motos_db"
python -m src.etl.load_to_db
```

PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/torres_motos_db"
python -m src.etl.load_to_db
```

A carga é um *full refresh* transacional: uma nova execução substitui o snapshot anterior sem duplicar registros. Em caso de falha, a transação é revertida.

### 5. Validar e testar

```bash
psql -h localhost -U postgres -d torres_motos_db -f database/queries_validation.sql
pytest
```

## Qualidade dos dados

O projeto verifica automaticamente que:

- Cliques não ultrapassem impressões
- Leads não ultrapassem cliques
- A quantidade de registros no CRM corresponda ao total de leads
- Uma venda só aconteça após um test drive
- Apenas vendas concluídas tenham valor positivo
- Chaves de plataforma e veículo sejam mapeadas antes da carga
- Uma segunda execução não duplique o snapshot no banco

O schema também aplica essas regras com `CHECK`, `NOT NULL`, chaves estrangeiras, índices e unicidade no grão diário de mídia.

## Estrutura

```text
torres-motos-analytics/
├── .github/workflows/ci.yml
├── data/raw/
├── database/
│   ├── create_db.py
│   ├── queries_validation.sql
│   └── schema.sql
├── src/etl/
│   ├── extract_transform.py
│   └── load_to_db.py
├── tests/
├── .env.example
├── docker-compose.yml
├── powerbi.pbix
├── requirements.txt
└── README.md
```

## Power BI

O arquivo `powerbi.pbix` contém o dashboard do projeto. Para facilitar a avaliação do portfólio, uma próxima evolução recomendada é adicionar em `docs/` capturas das páginas do dashboard, o diagrama do modelo e um catálogo das medidas DAX.

## Autor

Jose Carlos Torres

- [LinkedIn](https://www.linkedin.com/in/josecarlos-dados)
- [GitHub](https://github.com/jctorres94)
