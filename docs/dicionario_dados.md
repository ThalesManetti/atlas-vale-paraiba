# Dicionário de Dados — Atlas Econômico do Vale do Paraíba

## Camada Gold (tabelas analíticas para consumo)

---

### `gold_vale_paraiba.mart_ide_municipal`

Índice de Dinamismo Econômico por município e ano. Tabela principal para o ranking comparativo.

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_id` | STRING | Código IBGE do município (7 dígitos) |
| `municipio_nome` | STRING | Nome do município |
| `ano` | INTEGER | Ano de referência |
| `ide_score` | FLOAT | Score IDE final (0–100) |
| `c1_pib_per_capita` | FLOAT | Componente 1 normalizado: crescimento PIB pc |
| `c2_saldo_emprego` | FLOAT | Componente 2 normalizado: saldo emprego formal |
| `c3_diversificacao` | FLOAT | Componente 3 normalizado: diversificação setorial |
| `c4_dinamismo_recente` | FLOAT | Componente 4 normalizado: dinamismo recente |
| `hhi_bruto` | FLOAT | HHI não normalizado (para referência) |
| `pib_per_capita_real` | FLOAT | PIB per capita em R$ de 2022 |
| `saldo_caged_acumulado` | INTEGER | Saldo CAGED acumulado desde 2015 |
| `confianca_flag` | STRING | 'ALTA', 'MEDIA' ou 'BAIXA' (qualidade dos dados) |
| `updated_at` | TIMESTAMP | Timestamp de última atualização |

---

### `gold_vale_paraiba.mart_ipp_setor_municipio`

Índice de Pressão de Pejotização por setor, município e ano.

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_id` | STRING | Código IBGE do município |
| `municipio_nome` | STRING | Nome do município |
| `cnae_divisao` | STRING | Divisão CNAE 2.0 (2 dígitos) |
| `cnae_descricao` | STRING | Descrição da divisão CNAE |
| `ano` | INTEGER | Ano de referência |
| `delta_clt` | INTEGER | Saldo CAGED do setor no município no ano |
| `delta_mei` | INTEGER | Variação no estoque de MEIs ativos |
| `ipp_score` | FLOAT | Índice de Pressão de Pejotização (0 ou positivo) |
| `pressao_detectada` | BOOLEAN | TRUE quando IPP > 0 |
| `serie_confiavel` | BOOLEAN | FALSE quando fator de ligação CAGED é outlier |
| `updated_at` | TIMESTAMP | Timestamp de última atualização |

---

### `gold_vale_paraiba.mart_serie_emprego_mensal`

Série histórica de emprego formal por município e setor. Base para análises de tendência.

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_id` | STRING | Código IBGE do município |
| `cnae_divisao` | STRING | Divisão CNAE 2.0 |
| `ano` | INTEGER | Ano |
| `mes` | INTEGER | Mês (1–12) |
| `admissoes` | INTEGER | Total de admissões no mês |
| `desligamentos` | INTEGER | Total de desligamentos no mês |
| `saldo` | INTEGER | Admissões − desligamentos |
| `estoque_mei_ativo` | INTEGER | MEIs ativos no setor-município no final do mês |
| `fonte_caged` | STRING | 'CAGED_ANTIGO' (2015–2019) ou 'NOVO_CAGED' (2020+) |
| `fator_ligacao` | FLOAT | Fator de ajuste de série (1.0 = sem ajuste) |
| `updated_at` | TIMESTAMP | Timestamp de última atualização |

---

### `gold_vale_paraiba.mart_kpis_municipio`

KPIs consolidados por município para o dashboard executivo (Power BI).

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_id` | STRING | Código IBGE do município |
| `municipio_nome` | STRING | Nome do município |
| `populacao_2022` | INTEGER | População Censo 2022 |
| `pib_total_2021` | FLOAT | PIB total em R$ mil (2021, último dado disponível) |
| `pib_per_capita_2021` | FLOAT | PIB per capita em R$ |
| `pib_industria_pct` | FLOAT | Participação da indústria no PIB (%) |
| `pib_servicos_pct` | FLOAT | Participação dos serviços no PIB (%) |
| `empregos_formais_2024` | INTEGER | Estoque estimado de empregos CLT (2024) |
| `saldo_caged_2024` | INTEGER | Saldo CAGED acumulado Jan–Dez 2024 |
| `mei_ativos_2024` | INTEGER | MEIs ativos (total, todos os setores) |
| `razao_mei_clt` | FLOAT | Razão MEIs / empregos CLT — proxy de informalidade |
| `ide_score_ultimo` | FLOAT | IDE do último ano calculado |
| `ide_ranking` | INTEGER | Posição no ranking (1 = mais dinâmico) |
| `ipp_medio_setores_foco` | FLOAT | IPP médio nos setores-foco (pejotização) |
| `updated_at` | TIMESTAMP | Timestamp de última atualização |

---

## Camada Silver (dados limpos)

### `silver_vale_paraiba.stg_pib_municipal`

PIB municipal limpo e deflacionado.

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_id` | STRING | Código IBGE (7 dígitos) |
| `ano` | INTEGER | Ano |
| `pib_corrente_mil` | FLOAT | PIB a preços correntes em R$ mil |
| `va_agropecuaria_mil` | FLOAT | Valor adicionado — agropecuária |
| `va_industria_mil` | FLOAT | Valor adicionado — indústria |
| `va_servicos_mil` | FLOAT | Valor adicionado — serviços |
| `va_admin_publica_mil` | FLOAT | Valor adicionado — administração pública |
| `impostos_mil` | FLOAT | Impostos líquidos de subsídios |
| `populacao` | INTEGER | População estimada IBGE |
| `pib_per_capita` | FLOAT | PIB per capita corrente |
| `deflator_ipca` | FLOAT | Deflator IPCA (base 2022 = 1.0) |
| `pib_per_capita_real` | FLOAT | PIB per capita em R$ de 2022 |

### `silver_vale_paraiba.stg_caged_mensal`

Saldo CAGED mensal por município e setor, com série ligada.

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_id` | STRING | Código IBGE |
| `cnae_divisao` | STRING | Divisão CNAE 2.0 (2 dígitos) |
| `ano` | INTEGER | Ano |
| `mes` | INTEGER | Mês |
| `admissoes` | INTEGER | Admissões |
| `desligamentos` | INTEGER | Desligamentos |
| `saldo_bruto` | INTEGER | Saldo sem ajuste |
| `saldo_ajustado` | INTEGER | Saldo com fator de ligação aplicado |
| `fonte` | STRING | 'CAGED_ANTIGO' ou 'NOVO_CAGED' |
| `fator_ligacao` | FLOAT | Fator de ajuste (NULL = sem ajuste necessário) |
| `ligacao_confiavel` | BOOLEAN | TRUE se fator de ligação entre 0.7 e 1.3 |

### `silver_vale_paraiba.stg_cnpj_mei_mensal`

Estoque de MEIs ativos por município e setor, filtrado para municípios do Vale.

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_id` | STRING | Código IBGE |
| `cnae_divisao` | STRING | Divisão CNAE 2.0 |
| `ano` | INTEGER | Ano |
| `mes` | INTEGER | Mês |
| `mei_ativos` | INTEGER | Contagem de MEIs com situação cadastral 'Ativa' |
| `mei_abertos_mes` | INTEGER | MEIs com data_inicio_atividade no mês |
| `mei_encerrados_mes` | INTEGER | MEIs com data_situacao_cadastral no mês e situação de encerramento |
| `data_extracao` | DATE | Data do arquivo CNPJ usado como fonte |

> **Nota de privacidade:** Esta tabela contém apenas contagens agregadas por município-setor. Nenhum dado individual de CNPJ (razão social, sócio, endereço) é armazenado ou versionado.

---

## Camada Bronze (dados brutos)

As tabelas bronze contêm os dados exatamente como vieram da fonte, com coluna `_ingested_at`. Não são documentadas em detalhe aqui por refletirem diretamente os schemas das fontes originais. Consulte a documentação de cada fonte:

- IBGE PIB Municípios: https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9088
- CAGED/Novo CAGED: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/empregabilidade/caged
- CNPJ Dados Abertos: https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj
- CEMPRE: https://www.ibge.gov.br/estatisticas/economicas/industria/9016
