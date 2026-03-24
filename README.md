# Lab01 — Arquitetura Medallion: Hábitos e Desempenho de Estudantes

**Dataset:** [College Students Habits and Performance](https://www.kaggle.com/datasets/sharmajicoder/college-students-habits-and-performance)
**Linhas:** 1.000.000 | **Colunas:** 42 | **Fonte:** Kaggle (sintético)

---

## 1. Arquitetura

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│   Kaggle    │────►│   Camada RAW     │────►│   Camada SILVER     │────►│   Camada GOLD        │
│  (Fonte)    │     │  PostgreSQL      │     │   Arquivo Parquet   │     │  PostgreSQL           │
│             │     │  tabela:students │     │  students_silver    │     │  Star Schema          │
└─────────────┘     └──────────────────┘     └─────────────────────┘     └──────────────────────┘
      │                     │                         │                            │
  kagglehub            ingestion_raw.py          ingestion_silver.py        ingestion_gold.py
  download             inserção bruta            limpeza + parquet          tabelas dim + fato
```

**Fluxo:**
`Kaggle API` → `Python (kagglehub)` → `Tabela raw no PostgreSQL` → `Parquet (Silver)` → `Star Schema no PostgreSQL (Gold)`

---

## 2. Documentação dos Scripts

### `data/raw/ingestion_raw.py` — Camada Raw
Faz o download do dataset do Kaggle via `kagglehub` e insere todas as linhas sem transformação na tabela `students` do PostgreSQL.

### `data/silver/ingestion_silver.py` — Camada Silver
Lê a tabela `students` do PostgreSQL e aplica:
- Padronização de nomes de colunas para `snake_case`
- Remoção de duplicatas
- Imputação de valores ausentes (mediana para numéricos, `"unknown"` para categóricos)
- Detecção automática e conversão de colunas de data
- Salva o resultado em `data/silver/students_silver.parquet`

### `data/silver/report_silver.py` — Relatório Silver
Lê o Parquet da camada silver e gera [`data/silver/students_silver_report.txt`](data/silver/students_silver_report.txt) com:
- Contagem de linhas e colunas
- Tipos de cada coluna
- Contagem de nulos por coluna
- Estatísticas descritivas (média, desvio padrão, mínimo, máximo)

### `data/silver/chart_silver.py` — Gráficos Silver
Gera 5 gráficos de análise salvos em `data/silver/charts/`.
Análise completa disponível em [`data/silver/analysis_silver.md`](data/silver/analysis_silver.md):

| Gráfico | Descrição |
|---------|-----------|
| Distribuição do GPA | Histograma dos valores de GPA com linha da média |
| Nível de Performance | Gráfico de barras — quantidade de alunos por nível (Low/Medium/High) |
| Horas de Estudo vs GPA | Scatter colorido por nível de performance |
| Estresse vs GPA | Scatter — impacto do estresse no desempenho acadêmico |
| Mapa de Correlação | Correlações de Pearson entre 10 features principais |

### `data/gold/ingestion_gold.py` — Camada Gold (Star Schema)
Lê o Parquet silver e carrega um Star Schema no PostgreSQL:

```
fact_student_performance
  ├── dim_performance   (nível de desempenho)
  ├── dim_student       (dados demográficos: renda, moradia, escolaridade dos pais)
  ├── dim_lifestyle     (sono, estresse, tempo de tela, redes sociais...)
  └── dim_academic      (horas de estudo, frequência, pendências, procrastinação...)
```

### `data/gold/report_gold.py` — Perguntas de Negócio
5 funções Python que consultam o Star Schema para responder perguntas de negócio. Resultados salvos em [`data/gold/business_report_gold.txt`](data/gold/business_report_gold.txt).

---

## 3. Dicionário de Dados

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `study_hours` | float | Horas diárias dedicadas ao estudo |
| `attendance` | float | Percentual de presença nas aulas (0–100) |
| `assignment_completion` | float | Percentual de tarefas concluídas (0–100) |
| `midterm_score` | float | Nota da prova de meio de semestre (0–100) |
| `final_score` | float | Nota da prova final (0–100) |
| `project_score` | float | Nota do projeto (0–100) |
| `backlogs` | int | Número de matérias reprovadas/pendentes |
| `sleep_hours` | float | Média de horas de sono por noite |
| `stress` | float | Nível de estresse autorrelatado (1–10) |
| `anxiety` | float | Pontuação de ansiedade (0–100) |
| `depression` | float | Pontuação de depressão (0–100) |
| `motivation` | float | Pontuação de motivação (1–10) |
| `concentration` | float | Capacidade de concentração (1–10) |
| `time_management` | float | Gestão do tempo (1–10) |
| `self_discipline` | float | Autodisciplina (1–10) |
| `social_media_hours` | float | Horas diárias em redes sociais |
| `gaming_hours` | float | Horas diárias jogando |
| `netflix_hours` | float | Horas diárias assistindo streaming |
| `screen_time` | float | Tempo total diário de tela (horas) |
| `physical_activity` | float | Horas semanais de atividade física |
| `junk_food_frequency` | float | Consumo de junk food por semana |
| `caffeine_mg` | float | Consumo diário de cafeína em mg |
| `late_night_frequency` | float | Frequência semanal de madrugadas acordado |
| `procrastination_score` | float | Tendência à procrastinação (1–10) |
| `family_income` | float | Renda familiar anual |
| `parental_education_level` | int | Nível de escolaridade dos pais (0=nenhum → 5=pós-graduação) |
| `internet_quality` | float | Qualidade da internet (1–10) |
| `library_visits` | float | Visitas à biblioteca por semana |
| `online_courses_completed` | int | Número de cursos online concluídos |
| `part_time_hours` | float | Horas semanais em trabalho part-time |
| `peer_study_group` | int | Participa de grupo de estudos (0=Não, 1=Sim) |
| `relationship_status` | int | Está em um relacionamento (0=Não, 1=Sim) |
| `hostel_student` | int | Mora em república/alojamento (0=Não, 1=Sim) |
| `extracurricular_hours` | float | Horas semanais em atividades extracurriculares |
| `phone_unlocks_per_day` | float | Número de desbloqueios do celular por dia |
| `previous_gpa` | float | GPA do semestre anterior (0–10) |
| `class_participation` | float | Participação em sala de aula (1–10) |
| `weekly_study_sessions` | float | Sessões de estudo dedicadas por semana |
| `group_study_hours` | float | Horas semanais de estudo em grupo |
| `financial_stress` | float | Nível de estresse financeiro (1–10) |
| `gpa` | float | GPA atual (escala 0–2) |
| `performance_level` | str | Categoria de desempenho acadêmico (Low / Medium / High) |

---

## 4. Qualidade de Dados

Problemas identificados durante o processamento da camada silver (`data/silver/students_silver_report.txt`):

| Problema | Detalhe | Resolução |
|----------|---------|-----------|
| **Valores ausentes** | 1.558 linhas com `performance_level = null` | Imputado como `"unknown"` (fallback categórico) |
| **Duplicatas** | Nenhuma detectada em 1.000.000 linhas | — |
| **Nomes de colunas** | Colunas originais em mixed case com espaços | Padronizados para `snake_case` |
| **Consistência de tipos** | Todas as colunas numéricas já em float/int | Nenhuma conversão necessária |
| **Escala do GPA** | Mín = 0.0, Máx = 2.009 (não 0–10 como descrito) | Mantido como está; escala real é 0–2 |
| **Ansiedade/Depressão** | Pontuadas de 0–100 enquanto demais métricas usam 1–10 | Escalas diferentes registradas; mantido como está |

> Os 1.558 registros `unknown` apresentam sinais claros de baixo desempenho: GPA médio de 0.0, 48,6% de presença e escore de procrastinação de 7,56 — provavelmente lacunas de preenchimento dos alunos com pior rendimento.

---

## 5. Perguntas de Negócio (Camada Gold)

Resultados completos em [`data/gold/business_report_gold.txt`](data/gold/business_report_gold.txt).

**Q1 — GPA Médio por Nível de Performance**
Alunos de baixo desempenho têm GPA médio de 0,83 e nota final de 64,9. O grupo `unknown` (1.558 alunos) apresenta GPA 0,0, confirmando serem casos extremos.

**Q2 — Impacto do Estilo de Vida no GPA**
Alunos de baixo desempenho têm estresse médio de 3,21 e 6,50h de sono; o grupo `unknown` apresenta estresse de 5,05 e apenas 5,76h de sono — maior estresse e menos sono correlacionam com piores resultados.

**Q3 — Hábitos Acadêmicos por Nível de Performance**
Alunos de baixo desempenho estudam 4,05h/dia com 74,9% de presença; o grupo `unknown` estuda apenas 0,42h/dia com 48,6% de presença e escore de procrastinação de 7,56.

**Q4 — Renda Familiar vs GPA**
O grupo de renda tem impacto mínimo no GPA. O nível de escolaridade dos pais é o fator mais forte: nível 0 → GPA médio 0,68; nível 5 → GPA médio 0,98, independente da faixa de renda.

**Q5 — Perfil do Top 10% vs Bottom 10%**

| Métrica | Top 10% | Bottom 10% |
|---------|---------|------------|
| GPA Médio | 1,35 | 0,32 |
| Horas de estudo/dia | 7,33 | 1,11 |
| Presença | 93,2% | 56,3% |
| Procrastinação | 3,33 | 6,65 |
| Motivação | 7,09 | 4,89 |

---

## 6. Instruções de Execução

### Pré-requisitos
- Python 3.10+
- PostgreSQL rodando localmente na porta 5432
- Banco de dados `students` já criado
- Conta no Kaggle com token de API

### Configuração

```bash
# Clonar o repositório
git clone https://github.com/daniely-luz/Lab01_PART1_13775103
cd Lab01_PART1_13775103

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install 'kagglehub[pandas-datasets]' pandas sqlalchemy psycopg2-binary \
            python-dotenv pyarrow matplotlib
```

### Credenciais

Crie um arquivo `.env` na raiz do projeto:

```
KAGGLE_API_TOKEN=seu_token_kaggle_aqui
```

### Ordem de execução

```bash
# 1. Camada Raw — download do Kaggle e inserção no PostgreSQL
python data/raw/ingestion_raw.py

# 2. Camada Silver — limpeza dos dados e geração do Parquet
python data/silver/ingestion_silver.py

# 3. Relatório Silver — contagem de nulos, tipos e estatísticas
python data/silver/report_silver.py

# 4. Gráficos Silver — gerar 5 gráficos de análise + markdown
python data/silver/chart_silver.py

# 5. Camada Gold — construir Star Schema no PostgreSQL
python data/gold/ingestion_gold.py

# 6. Relatório Gold — responder 5 perguntas de negócio
python data/gold/report_gold.py
```
