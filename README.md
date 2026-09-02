# Torres Motors Analytics

Projeto de engenharia e análise de dados que simula o funil comercial de uma concessionária de motocicletas. O pipeline gera dados sintéticos e reproduzíveis de mídia e CRM, valida regras de negócio, carrega um modelo estrela no PostgreSQL e disponibiliza um dashboard profissional no Power BI.

> Os dados deste repositório são simulados e não representam clientes ou operações reais.

## Arquitetura

```mermaid
flowchart LR
    A[Gerador Python] --> B[CSV de mídia e CRM]
    B --> C[Validações de qualidade]
    C --> D[ETL transacional]
    D --> E[(PostgreSQL)]
    B --> F[Power BI]
```

O modelo estrela possui três dimensões (`dim_tempo`, `dim_plataforma` e `dim_veiculo`) e duas tabelas fato (`fato_desempenho_midia` e `fato_funil_crm`).

## Indicadores

- Impressões, cliques, CTR e investimento em mídia
- Leads, CPC e custo por lead
- Test drives e taxa de avanço no funil
- Vendas, receita, CAC e ticket médio
- ROAS por plataforma
- Conversão de leads em vendas
- Desempenho por modelo de motocicleta e período

O cálculo de ROAS agrega cada tabela fato antes do `JOIN`, evitando multiplicação de valores em relações muitos-para-muitos.

## Dashboard Power BI

A versão editável e recomendada está em [`powerbi/Torres_Motors_Analytics.pbip`](powerbi/Torres_Motors_Analytics.pbip). Ela inclui:

- duas páginas integradas de visão executiva e detalhamento;
- filtros sincronizados de mês, plataforma e modelo;
- navegação entre páginas;
- cartões de KPI, gráficos comparativos, tendências e matriz;
- identidade visual própria da Torres Motors;
- modelo semântico versionável em TMDL;
- 15 medidas DAX organizadas por área de negócio.

Para abrir corretamente:

1. Clone ou baixe o repositório completo.
2. Abra `powerbi/Torres_Motors_Analytics.pbip` no Power BI Desktop.
3. Em **Página Inicial > Transformar dados > Gerenciar parâmetros**, confira o parâmetro `DataRoot`.
4. Aponte-o para a pasta local `data\raw` deste repositório.
5. Clique em **Atualizar** e depois em **Aplicar alterações**.

O valor inicial de `DataRoot` é `C:\TorresMotors\data\raw`. Ele é propositalmente genérico para que caminhos pessoais da máquina não sejam publicados no GitHub.

O arquivo `powerbi.pbix` na raiz foi mantido como versão legada. O projeto PBIP é a fonte oficial porque permite auditar no Git as medidas, consultas, relacionamentos e definições dos visuais. Depois de abrir e atualizar o PBIP, use **Arquivo > Salvar como** para gerar um PBIX único e atualizado.

Consulte também [`powerbi/LEIA-ME.txt`](powerbi/LEIA-ME.txt).

## Tecnologias

- Python 3.12, Pandas e NumPy
- SQLAlchemy e psycopg2
- PostgreSQL 16
- Power BI Project (PBIP/PBIR/TMDL)
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
export DATABASE_URL="postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/torres_motors_db"
python -m src.etl.load_to_db
```

PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/torres_motors_db"
python -m src.etl.load_to_db
```

A carga é um *full refresh* transacional: uma nova execução substitui o snapshot anterior sem duplicar registros. Em caso de falha, a transação é revertida.

### 5. Validar e testar

```bash
psql -h localhost -U postgres -d torres_motors_db -f database/queries_validation.sql
pytest
```

## Qualidade dos dados

O projeto verifica automaticamente que:

- cliques não ultrapassem impressões;
- leads não ultrapassem cliques;
- a quantidade de registros no CRM corresponda ao total de leads;
- uma venda só aconteça após um test drive;
- apenas vendas concluídas tenham valor positivo;
- chaves de plataforma e veículo sejam mapeadas antes da carga;
- uma segunda execução não duplique o snapshot no banco.

O schema também aplica essas regras com `CHECK`, `NOT NULL`, chaves estrangeiras, índices e unicidade no grão diário de mídia.

## Estrutura

```text
torres-motos-analytics/
├── .github/workflows/ci.yml
├── data/raw/
├── database/
├── powerbi/
│   ├── Torres_Motors_Analytics.pbip
│   ├── Torres_Motors_Analytics.Report/
│   └── Torres_Motors_Analytics.SemanticModel/
├── src/etl/
├── tests/
├── docker-compose.yml
├── powerbi.pbix
├── requirements.txt
└── README.md
```

## Autor

Jose Carlos Torres

- [LinkedIn](https://www.linkedin.com/in/josecarlos-dados)
- [GitHub](https://github.com/jctorres94)
