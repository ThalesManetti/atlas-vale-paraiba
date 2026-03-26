# Atlas Econômico do Vale do Paraíba

**Pesquisa empírica sobre dinamismo econômico, mercado de trabalho formal e precarização do vínculo empregatício em 12 municípios da Região Metropolitana do Vale do Paraíba e Litoral Norte (SP) — 2015–2024**

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![BigQuery](https://img.shields.io/badge/BigQuery-GCP-4285F4)](https://cloud.google.com/bigquery)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Data: Público](https://img.shields.io/badge/Dados-100%25%20Públicos-brightgreen)](#fontes-de-dados)

---

## Visão geral

O Vale do Paraíba paulista é um dos eixos industriais mais relevantes do Brasil — abriga a Embraer, General Motors, Petrobras, Johnson & Johnson e o maior complexo aeroespacial da América Latina. Ainda assim, a região apresenta heterogeneidade econômica marcante entre seus municípios: São José dos Campos concentra alta tecnologia e serviços sofisticados, enquanto cidades como Guaratinguetá e Lorena mantêm perfil industrial mais tradicional, e Aparecida vive da economia religiosa e do turismo.

Este projeto responde três perguntas de pesquisa:

1. **Qual município do Vale tem o mercado de trabalho mais dinâmico**, considerando crescimento do emprego formal, diversificação setorial e resiliência a choques?
2. **A reforma trabalhista de 2017 acelerou a substituição de vínculos CLT por contratos PJ** nos municípios da região? A pressão de pejotização é homogênea ou concentrada em setores e cidades específicas?
3. **Existe correlação entre complexidade econômica e resistência à precarização** do vínculo de trabalho?

---

## Fundamentação teórica

O projeto se apoia em três correntes da literatura econômica:

**Sobre dinamismo e complexidade econômica regional**

- Hidalgo & Hausmann (2009) — *The Building Blocks of Economic Complexity*, PNAS. Propõem que a diversidade produtiva de uma região é proxy da quantidade de conhecimento produtivo acumulado. Adaptamos a metodologia do *Economic Complexity Index* (ECI) para o nível municipal usando dados de emprego formal (RAIS/CAGED) como proxy de vantagem comparativa revelada.
- Gomes et al. (2022) — *Economic Complexity and Regional Economic Development: Evidence from Brazil*, ANPEC. Demonstra que a complexidade econômica calculada com dados de emprego tem correlação significativa com PIB per capita e emprego formal per capita em municípios brasileiros.
- Ferraz et al. (2024) — *Related Industries, Economic Complexity, and Regional Diversification*, ScienceDirect. Analisa 558 microrregiões brasileiras de 2006 a 2016, mostrando que novas indústrias tendem a surgir onde há relatedness tecnológico com setores já existentes.

**Sobre pejotização e precarização do trabalho**

- Torbitoni et al. (2026) — *Pejotização e seus impactos na precarização das relações de trabalho no Brasil*, Observatório da Economia Latino-americana. Revisão sistemática dos mecanismos pelos quais a pejotização fragiliza direitos trabalhistas.
- Remédio & Doná (2018) — *A Pejotização do Contrato de Trabalho e a Reforma Trabalhista*, Index Law Journals. Analisa as alterações da Lei 13.467/2017 que viabilizaram a terceirização da atividade-fim.
- Castro (2013) — *Afogados em contratos: o impacto da flexibilização do trabalho nas trajetórias dos profissionais de TI*, Tese de Doutorado, UNICAMP. Estudo de caso em setor com alta prevalência de pejotização — relevante para o perfil de SJC.

**Sobre reforma trabalhista e evidências empíricas**

- Anpec (2022) — *A reforma trabalhista de 2017 teve efeito sobre a taxa de desemprego?* Usando controle sintético com 11 países latino-americanos, não encontra efeito estatisticamente significativo da reforma sobre o desemprego, sugerindo que a mudança estrutural foi qualitativa (tipo de vínculo), não quantitativa (número de postos).

---

## Metodologia

### Municípios estudados

Os 12 municípios foram selecionados pelo critério de relevância econômica na Calha do Vale (eixo da Via Dutra), garantindo variabilidade no perfil produtivo:

| Município | Cód. IBGE | Perfil dominante |
|---|---|---|
| São José dos Campos | 3549904 | Tecnologia, aeroespacial, serviços |
| Taubaté | 3554102 | Indústria automotiva, serviços |
| Jacareí | 3524402 | Indústria diversificada |
| Caçapava | 3299606 | Indústria siderúrgica |
| Pindamonhangaba | 3537107 | Indústria, comércio regional |
| Guaratinguetá | 3517303 | Indústria, turismo religioso |
| Lorena | 3536505 | Química, educação |
| Cruzeiro | 3520400 | Indústria metalúrgica |
| Tremembé | 3521606 | Serviços, logística |
| Santa Branca | 3549300 | Agropecuária, pequeno porte |
| Aparecida | 3472203 | Turismo religioso |
| Roseira | 3537305 | Agropecuária, turismo |

> Os dois últimos municípios (Santa Branca, Aparecida, Roseira) servem como grupos de contraste para municípios de perfil não-industrial.

### Índice de Dinamismo Econômico (IDE)

Índice composto com quatro componentes, todos normalizados em escala 0–100:

```
IDE = 0.35 × Crescimento_PIB_pc + 0.30 × Saldo_Emprego_Formal + 0.20 × Diversificação_Setorial + 0.15 × Dinamismo_Recente
```

- **Crescimento do PIB per capita** (peso 35%): variação percentual real, deflacionada pelo IPCA, no período 2015–2021 (último dado IBGE disponível com abertura setorial).
- **Saldo líquido de emprego formal** (peso 30%): saldo acumulado CAGED 2015–2024, normalizado pela população em idade ativa.
- **Diversificação setorial** (peso 20%): inverso do Índice Herfindahl-Hirschman (HHI) calculado sobre a distribuição de emprego por divisão CNAE 2.0. Maior score = menor concentração = maior diversificação.
- **Dinamismo recente** (peso 15%): variação do saldo de emprego nos últimos 24 meses vs. média histórica — captura aceleração ou desaceleração recente.

Os pesos foram definidos com base na literatura de complexidade econômica regional, priorizando estrutura produtiva (PIB + diversificação) sobre métricas conjunturais puras.

### Índice de Pressão de Pejotização (IPP)

Métrica por setor-município-ano que captura substituição de vínculos CLT por PJ:

```
IPP(s,m,t) = ΔMEI(s,m,t) / |ΔCLT(s,m,t)| , quando ΔCLT < 0 e ΔMEI > 0
IPP(s,m,t) = 0 , nos demais casos
```

Onde:
- `s` = setor (divisão CNAE 2.0)
- `m` = município
- `t` = ano
- `ΔMEI` = variação no estoque de MEIs ativos no setor
- `ΔCLT` = saldo CAGED (admissões − desligamentos) no setor

O IPP só é calculado quando as duas condições se verificam simultaneamente — queda no emprego CLT e crescimento de MEIs no mesmo setor e município. Crescimento genuíno (ambos sobem) não ativa o indicador.

**Setores-foco** (maior exposição à pejotização, conforme literatura):

| CNAE | Setor |
|---|---|
| 62 | Atividades dos serviços de tecnologia da informação |
| 71 | Serviços de arquitetura e engenharia |
| 73 | Publicidade e pesquisa de mercado |
| 74 | Outras atividades profissionais, científicas e técnicas |
| 82 | Serviços de escritório e apoio administrativo |
| 86 | Atividades de atenção à saúde humana |

---

## Fontes de dados

Todos os dados utilizados são **públicos, abertos e gratuitos**. Nenhum dado identificável de pessoas físicas é coletado, armazenado ou publicado.

| Fonte | Dataset | Granularidade | Período | Acesso |
|---|---|---|---|---|
| IBGE — PIB Municípios | PIB e VA por setor | Município × ano | 2002–2021 | API SIDRA / download |
| IBGE — Censo 2022 | População, IDH | Município | 2022 | API IBGE |
| MTE — CAGED (Novo CAGED) | Admissões e desligamentos por setor | Município × setor × mês | 2020–2024 | FTP gov.br |
| MTE — RAIS | Estoque de empregos, salário médio | Município × setor × ano | 2015–2022 | Base dos Dados / download |
| Receita Federal — CNPJ | MEIs e empresas abertas por CNAE | Município × setor | Mensal | dados.gov.br (arquivo público) |
| IBGE — CEMPRE | Pessoal ocupado total vs. assalariado | Município × setor × ano | 2006–2022 | SIDRA |
| IBGE — Malha Municipal | Geometrias dos municípios SP | Município | 2022 | geoftp.ibge.gov.br |
| SEADE | Indicadores regionais SP | Município × ano | 2010–2023 | repositorio.seade.gov.br |

> **Nota sobre o arquivo CNPJ da Receita Federal:** O arquivo completo tem ~3 GB comprimido e contém todos os CNPJs cadastrados. Para este projeto, filtramos apenas os municípios do Vale do Paraíba usando o código IBGE do município. Os dados brutos NÃO são versionados no Git — apenas o script de filtragem e os dados já filtrados no BigQuery.

---

## Arquitetura

```
Fontes públicas → Python (coleta) → GCS (data lake) → BigQuery (warehouse)
                                                              ↓
                                          dbt (bronze → silver → gold)
                                                              ↓
                               ┌──────────────────────────────────────────┐
                               │  Power BI  │  GitHub Pages  │  Notebook  │
                               └──────────────────────────────────────────┘
```

**Camadas do data warehouse:**

- `bronze_vale_paraiba` — dados brutos, exatamente como vieram da fonte, com timestamp de ingestão
- `silver_vale_paraiba` — dados limpos, tipados, padronizados, enriquecidos com geometrias
- `gold_vale_paraiba` — tabelas analíticas: IDE por município-ano, IPP por setor-município-ano, série histórica de emprego

**Stack:**

| Camada | Tecnologia |
|---|---|
| Coleta | Python 3.11, requests, pandas |
| Data Lake | Google Cloud Storage |
| Warehouse | Google BigQuery |
| Transformação | dbt + Python |
| Geoespacial | GeoPandas, Folium |
| Visualização BI | Power BI Desktop |
| App web | GitHub Pages (HTML/JS + Folium) |

---

## Estrutura do repositório

```
atlas-vale-paraiba/
├── .env.example              ← Template de variáveis de ambiente (sem segredos)
├── .gitignore                ← Dados brutos e credenciais excluídos
├── README.md
├── LICENSE
├── requirements.txt
├── environment.yml
│
├── config/
│   ├── municipalities.yaml   ← Lista de municípios e códigos IBGE
│   └── cnae_sectors.yaml     ← Setores-foco para análise de pejotização
│
├── src/
│   ├── collectors/           ← Scripts de coleta de cada fonte
│   │   ├── ibge_api.py
│   │   ├── caged_collector.py
│   │   ├── cnpj_filter.py    ← Filtra arquivo CNPJ da Receita para municípios-alvo
│   │   └── seade_collector.py
│   ├── transformers/         ← Scripts dbt e transformações Python
│   ├── analysis/             ← Cálculo do IDE e do IPP
│   │   ├── ide_calculator.py
│   │   └── ipp_calculator.py
│   └── visualization/        ← Geração do app web e mapas
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_ide_methodology.ipynb
│   ├── 03_pejotizacao_analysis.ipynb
│   └── 04_final_report.ipynb
│
├── docs/
│   ├── plano_implementacao.md
│   ├── metodologia.md
│   └── dicionario_dados.md
│
├── tests/
│   └── ...
│
└── data/
    ├── processed/            ← Dados processados versionáveis (pequenos, anonimizados)
    └── external/
        └── shapefiles/       ← Geometrias municipais (baixadas via script)
```

---

## Reprodutibilidade

### Pré-requisitos

- Python 3.11+
- Conta GCP com BigQuery e Cloud Storage habilitados
- gcloud CLI instalado e autenticado

### Setup

```bash
# 1. Clonar o repositório
git clone https://github.com/SEU_USUARIO/atlas-vale-paraiba.git
cd atlas-vale-paraiba

# 2. Criar ambiente conda
conda env create -f environment.yml
conda activate atlas-vale

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais GCP

# 4. Executar coleta de dados (pode levar 30-60 minutos na primeira vez)
python src/collectors/run_all.py

# 5. Executar transformações dbt
cd dbt && dbt run && dbt test

# 6. Calcular índices
python src/analysis/ide_calculator.py
python src/analysis/ipp_calculator.py
```

> **Custo estimado de infraestrutura GCP:** < US$ 5 para execução completa, dentro do free tier para contas novas.

---

## Resultados preliminares

*(Seção atualizada à medida que a análise avança)*

---

## Limitações

1. **Identificação imperfeita da pejotização:** o IPP é um proxy — não há como distinguir MEI genuinamente empreendedor de MEI criado para mascarar relação de emprego usando apenas dados administrativos. A literatura reconhece essa limitação (Torbitoni et al., 2026; Castro, 2013).
2. **PIB municipal:** dados disponíveis apenas até 2021 (IBGE), sem abertura setorial para 2022–2023. Para o período recente, usamos emprego formal como proxy de atividade econômica.
3. **CAGED novo vs. antigo:** a série histórica do CAGED foi descontinuada e substituída em 2020. A metodologia de ligação de séries segue o procedimento do próprio MTE (nota técnica disponível em `/docs/metodologia.md`).
4. **Arquivo CNPJ:** atualização mensal com defasagem de ~45 dias. Análises mensais usam dados com esse lag.

---

## Licença

MIT — veja [LICENSE](LICENSE).

Os dados utilizados são públicos e distribuídos conforme as licenças de cada fonte (IBGE, MTE, Receita Federal). Nenhum dado de pessoa física é redistribuído neste repositório.

---

## Referências

- FERRAZ, D. et al. *Related industries, economic complexity, and regional diversification: An application for Brazilian microregions*. Research Policy, 2024.
- GOMES, L. et al. *Economic complexity and regional economic development: evidence from Brazil*. ANPEC, 2022.
- HIDALGO, C.; HAUSMANN, R. *The building blocks of economic complexity*. PNAS, v.106, n.26, 2009.
- MORAIS, M.; SWART, J.; JORDAAN, J. *Economic Complexity and Inequality: Does Regional Productive Structure Affect Income Inequality in Brazilian States?* Sustainability, MDPI, 2021.
- REMÉDIO, J.; DONÁ, S. *A pejotização do contrato de trabalho e a reforma trabalhista*. Rev. Direito do Trabalho e Meio Ambiente do Trabalho, v.4, n.2, 2018.
- TORBITONI, G. et al. *Pejotização e seus impactos na precarização das relações de trabalho no Brasil*. Observatório da Economia Latino-americana, v.24, n.1, 2026.
- VIANA, F. et al. *A reforma trabalhista de 2017 teve efeito sobre a taxa de desemprego?* ANPEC, 2022.
