# Plano de Implementação

> Versão 1.0 — Março 2026 · Status atualizado manualmente a cada fase concluída

---

## Visão geral

| Item | Detalhe |
|---|---|
| Período analisado | 2015–2024 |
| Municípios | 12 da RMVPLN (Calha do Vale) |
| Marco estrutural | Nov/2017 (Reforma Trabalhista) |
| Estimativa total | 8 semanas |
| Stack | Python · BigQuery · dbt · GeoPandas · Power BI · GitHub Pages |

---

## Fase 1 — Infraestrutura e Coleta de Dados
**Semanas 1–2**

| ID | Etapa | Entregável | Status |
|---|---|---|---|
| 1.1 | Setup GCP (projeto, APIs, service account) | Projeto GCP ativo, credenciais configuradas | ⬜ A fazer |
| 1.2 | Criação do data lake GCS com estrutura medallion | Bucket com pastas `raw/`, `processed/` | ⬜ A fazer |
| 1.3 | Script coleta IBGE API (PIB, população, geometrias) | Dados IBGE no `bronze_vale_paraiba` | ⬜ A fazer |
| 1.4 | Script coleta CAGED / Novo CAGED (FTP MTE) | Série mensal 2015–2024 no bronze | ⬜ A fazer |
| 1.5 | Script filtragem CNPJ Receita Federal (MEIs) | Contagens MEI por mun-setor-mês no bronze | ⬜ A fazer |

**Checklist de validação da Fase 1:**
- [ ] `bq ls --project_id=SEU_PROJETO` retorna os 3 datasets
- [ ] Todas as 12 cidades presentes em `bronze_caged_mensal`
- [ ] Arquivo CNPJ bruto **não** está no repositório Git
- [ ] `dbt debug` passa sem erros

---

## Fase 2 — Transformações dbt (Silver e Gold)
**Semanas 3–4**

| ID | Etapa | Entregável | Status |
|---|---|---|---|
| 2.1 | Setup projeto dbt + profiles BigQuery | `dbt debug` OK, conexão BigQuery estabelecida | ⬜ A fazer |
| 2.2 | Models silver: limpeza, tipagem, ligação de séries CAGED | 7 models staging com todos os testes passando | ⬜ A fazer |
| 2.3 | Model gold: `mart_serie_emprego_mensal` | Série histórica ligada e validada | ⬜ A fazer |
| 2.4 | Cálculo do IDE — Python + dbt | `mart_ide_municipal` com scores 0–100 | ⬜ A fazer |
| 2.5 | Cálculo do IPP por setor-município | `mart_ipp_setor_municipio` | ⬜ A fazer |
| 2.6 | Model gold: `mart_kpis_municipio` | Tabela consolidada para Power BI | ⬜ A fazer |

**Checklist de validação da Fase 2:**
- [ ] `dbt test` passa com 0 falhas
- [ ] `mart_ide_municipal` tem exatamente 12 linhas no ano mais recente
- [ ] Nenhum `ipp_score` negativo em `mart_ipp_setor_municipio`
- [ ] Fator de ligação CAGED entre 0.7 e 1.3 para todos os municípios principais

---

## Fase 3 — Análise e Notebooks
**Semanas 4–5**

| ID | Etapa | Entregável | Status |
|---|---|---|---|
| 3.1 | Análise exploratória | `01_exploratory_analysis.ipynb` com estatísticas descritivas | ⬜ A fazer |
| 3.2 | Validação metodológica do IDE | `02_ide_methodology.ipynb` com testes de robustez (3 configurações de pesos) | ⬜ A fazer |
| 3.3 | Análise de pejotização | `03_pejotizacao_analysis.ipynb` com IPP pré/pós-2017 | ⬜ A fazer |
| 3.4 | Relatório final | `04_final_report.ipynb` exportado como HTML estático | ⬜ A fazer |

**Checklist de validação da Fase 3:**
- [ ] Notebooks executam sem erros com `jupyter nbconvert --execute`
- [ ] Outputs limpos antes do commit (`jupyter nbconvert --clear-output`)
- [ ] Nenhum dado individual em output de células

---

## Fase 4 — Dashboard Power BI
**Semanas 5–6**

| ID | Etapa | Entregável | Status |
|---|---|---|---|
| 4.1 | Conexão Power BI + BigQuery, modelo de dados | 4 tabelas gold importadas, relacionamentos validados | ⬜ A fazer |
| 4.2 | Página 1: Ranking IDE — comparativo municipal | Barras horizontais + KPI cards + filtros ano/setor | ⬜ A fazer |
| 4.3 | Página 2: Série temporal de emprego | Gráfico de área com decomposição setorial por município | ⬜ A fazer |
| 4.4 | Página 3: Pejotização — heatmap de pressão | IPP × setor × município × ano com drill-down | ⬜ A fazer |

---

## Fase 5 — App Web e Documentação Final
**Semanas 7–8**

| ID | Etapa | Entregável | Status |
|---|---|---|---|
| 5.1 | Mapa coroplético interativo (Folium) | App web público no GitHub Pages com IDE e IPP no mapa | ⬜ A fazer |
| 5.2 | Repositório GitHub profissional | README, SECURITY.md, CI/CD configurado, badges | ⬜ A fazer |
| 5.3 | Publicação do relatório analítico | HTML gerado do notebook no GitHub Pages | ⬜ A fazer |
| 5.4 | Vídeo demo 5 minutos | Gravação no YouTube ou Loom com narração técnica | ⬜ A fazer |

---

## Decisões técnicas e trade-offs

**Por que agregar o arquivo CNPJ em vez de usar API?**
O arquivo de dados abertos CNPJ da Receita Federal (~3 GB comprimido) é atualizado mensalmente e contém todo o cadastro nacional. Usar download direto e filtrar localmente é mais confiável do que depender de APIs de terceiros com rate limits e sem SLA. O script `cnpj_filter.py` faz download, filtra pelos 12 municípios, agrega em contagens e descarta o arquivo bruto.

**Por que usar o inverso do HHI para diversificação?**
O HHI (Herfindahl-Hirschman Index) mede concentração: HHI = 1 é monopólio, HHI → 0 é distribuição perfeita. Invertê-lo (e normalizar) transforma a métrica em "diversificação", onde score alto = mais diversificado. Isso é metodologicamente consistente com a literatura de complexidade econômica (Hidalgo & Hausmann, 2009) que trata diversidade como indicador positivo de capacidade produtiva.

**Por que não usar o ECI puro de Hidalgo & Hausmann?**
O ECI original requer uma matriz de especialização com muitas regiões para ter poder discriminatório. Com apenas 12 municípios, a matriz seria muito esparsa. O IDE usa a intuição do ECI (diversificação como proxy de capacidade produtiva) mas com um cálculo mais robusto para amostras pequenas.

**Por que incluir municípios pequenos como Roseira e Santa Branca?**
Eles servem como âncoras do ranking: ao incluir municípios com perfil radicalmente diferente (agropecuária pura, população < 15 mil), garantimos que o IDE discrimina bem entre os extremos. Se o índice não consegue separar Roseira de São José dos Campos, há algo errado na metodologia.

**Por que os pesos 35/30/20/15 e não iguais?**
A decisão é teórica: estrutura produtiva de longo prazo (PIB + diversificação = 55%) deve pesar mais que dinâmica conjuntural (emprego recente = 45%). O PIB per capita captura acumulação histórica de capital e produtividade — difícil de mudar rapidamente. O dinamismo recente captura tendência de curto prazo — complementa mas não domina. Os testes de robustez na Fase 3 validarão se o ranking muda materialmente com outras configurações de pesos.
