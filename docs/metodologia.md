# Metodologia — Atlas Econômico do Vale do Paraíba

## 1. Desenho da pesquisa

### 1.1 Tipo de estudo

Estudo observacional longitudinal com análise de painel de dados municipais. O período de análise é 2015–2024, com marco estrutural em novembro de 2017 (entrada em vigor da Lei 13.467/2017 — Reforma Trabalhista).

A escolha do recorte temporal tem justificativa econométrica: 2015 é o ano anterior à crise de 2015–2016 (que confunde o efeito da reforma se usarmos 2016 como baseline), e 2024 permite observar sete anos pós-reforma com dados suficientes para análise de tendência.

### 1.2 Unidade de análise

A unidade de análise primária é o par **município × setor (divisão CNAE 2.0) × ano**. Quando a pergunta de pesquisa exige agregação (ranking de municípios pelo IDE, por exemplo), os dados são agregados a partir dessa unidade granular.

### 1.3 Seleção de municípios

Os 12 municípios foram selecionados pelos seguintes critérios:

1. Pertencer à Região Imediata de São José dos Campos ou à Região Imediata de Taubaté-Pindamonhangaba (IBGE, 2017).
2. Ter histórico de emprego formal no CAGED suficiente para calcular o IPP (mínimo de 500 vínculos ativos em qualquer setor em qualquer ano do período).
3. Garantir variabilidade no perfil produtivo: pelo menos dois municípios industriais pesados, dois de serviços sofisticados, dois de perfil misto e dois de contraste (pequeno porte, turismo ou agropecuária).

---

## 2. Índice de Dinamismo Econômico (IDE)

### 2.1 Fundamentos teóricos

O IDE é inspirado metodologicamente em duas tradições:

**Complexidade econômica (Hidalgo & Hausmann, 2009):** A ideia central é que a riqueza de uma região não depende apenas do quanto ela produz, mas do *quão diversificado e sofisticado* é seu aparato produtivo. Regiões com alta diversificação têm maior capacidade de absorver choques e de gerar empregos de qualidade. Adaptamos a intuição do ECI para o nível municipal usando emprego formal como proxy de vantagem comparativa revelada — metodologia validada por Gomes et al. (2022) para municípios brasileiros.

**Indicadores compostos de desenvolvimento local:** Seguimos as boas práticas do OCDE (2008) para construção de índices compostos: normalização min-max por componente, definição de pesos com justificativa teórica, e testes de robustez com pesos alternativos.

### 2.2 Componentes e pesos

#### Componente 1 — Crescimento do PIB per capita (peso: 35%)

**Dado:** PIB municipal a preços correntes (IBGE — Produto Interno Bruto dos Municípios), deflacionado pelo IPCA anual médio (IBGE — IPCA).

**Cálculo:**
```
PIB_pc_real(m,t) = PIB_nominal(m,t) / Pop(m,t) / Deflator(t)
C1(m) = [PIB_pc_real(m,2021) / PIB_pc_real(m,2015)] - 1
```

**Normalização:**
```
C1_norm(m) = [C1(m) - min(C1)] / [max(C1) - min(C1)] × 100
```

**Limitação:** dados disponíveis apenas até 2021 sem abertura setorial para anos recentes. Não penaliza municípios por diferenças de tamanho absoluto — relevante para comparar SJC (~R$ 61 bi PIB) com Roseira (~R$ 0.4 bi).

#### Componente 2 — Saldo líquido de emprego formal (peso: 30%)

**Dado:** CAGED — saldo anual de admissões menos desligamentos, por município.

**Cálculo:**
```
Saldo_acum(m) = Σ(t=2015..2024) Saldo_CAGED(m,t)
C2(m) = Saldo_acum(m) / PIA(m)
```
Onde PIA é a População em Idade Ativa (15–64 anos) do Censo 2022.

**Justificativa da normalização pela PIA:** sem normalização, SJC dominaria o ranking pelo tamanho absoluto. Dividindo pela PIA, medimos a *intensidade* de geração de emprego relativa à força de trabalho local.

#### Componente 3 — Diversificação setorial (peso: 20%)

**Dado:** RAIS — estoque de empregos por divisão CNAE 2.0, por município e ano.

**Cálculo:**
```
HHI(m,t) = Σ_s [emp(s,m,t) / emp_total(m,t)]²
Diversificação(m) = média[HHI(m,t)] para t = 2015..2022
C3(m) = 1 - Diversificação_norm(m)
```

O inverso do HHI garante que municípios mais diversificados recebam score mais alto. HHI = 1 significa monopólio de um setor; HHI → 0 significa distribuição perfeitamente uniforme.

**Referência:** Ferraz et al. (2024) usam metodologia similar para medir relatedness entre setores em microrregiões brasileiras.

#### Componente 4 — Dinamismo recente (peso: 15%)

**Dado:** CAGED — saldo mensal, 2020–2024.

**Cálculo:**
```
Saldo_recente(m) = Σ(últimos 24 meses) Saldo_CAGED(m)
Saldo_histórico(m) = média anual × 2 (para comparar mesma janela)
C4(m) = Saldo_recente(m) / Saldo_histórico(m) - 1
```

Captura se o município está acelerando ou desacelerando em relação à sua própria tendência histórica.

### 2.3 Pesos e testes de robustez

Os pesos (35/30/20/15) refletem a prioridade teórica: estrutura produtiva de longo prazo (PIB + diversificação = 55%) pesa mais que métricas conjunturais (emprego + dinamismo = 45%).

Serão realizados testes de robustez com três configurações alternativas:
- Pesos iguais (25/25/25/25)
- Prioridade emprego (20/40/20/20)
- Sem dinamismo recente (35/35/30/0)

Rankings que não se alteram entre configurações têm maior robustez.

---

## 3. Índice de Pressão de Pejotização (IPP)

### 3.1 Fundamentos e hipótese

A hipótese central é que a pejotização se manifesta empiricamente como a combinação simultânea de:
1. **Queda no saldo de emprego CLT** em um setor-município (CAGED negativo)
2. **Crescimento do estoque de MEIs** no mesmo setor-município (dados CNPJ/Receita Federal)

Quando ambas as condições se verificam, é razoável inferir substituição de vínculos — não desemprego puro nem empreendedorismo puro. Essa abordagem segue a lógica dos estudos que usam correlação negativa entre emprego formal e abertura de MEIs como evidência de pejotização (ver Torbitoni et al., 2026, seção 3.2).

**Limitação reconhecida:** a correlação não é causalidade. Um trabalhador demitido que abre um MEI pode ser pejotização ou pode ser empreendedorismo genuíno. O IPP mede pressão, não confirma fraude. Essa distinção é explicitada em todas as análises.

### 3.2 Cálculo formal

Para cada tripla (setor `s`, município `m`, ano `t`):

```python
delta_clt = saldo_caged(s, m, t)           # positivo = mais CLT; negativo = menos CLT
delta_mei = estoque_mei(s, m, t) - estoque_mei(s, m, t-1)

if delta_clt < 0 and delta_mei > 0:
    IPP(s, m, t) = delta_mei / abs(delta_clt)
else:
    IPP(s, m, t) = 0
```

**Interpretação:**
- IPP = 0: sem pressão de substituição (crescimento conjunto, queda conjunta, ou crescimento CLT)
- IPP = 1: para cada CLT perdido, um MEI foi aberto no mesmo setor
- IPP > 1: mais MEIs abertos do que CLTs perdidos (sinal mais forte de substituição)
- IPP muito alto: pode indicar outras dinâmicas (crescimento do setor para autônomos)

### 3.3 Agregação para análise

**Por município-ano:** `IPP_municipal(m,t)` = média ponderada do IPP dos setores-foco, com peso proporcional ao emprego do setor no município.

**Por setor-regional:** `IPP_setor(s,t)` = média do IPP do setor em todos os 12 municípios — identifica quais setores têm pressão mais generalizada.

**Índice de aceleração pós-reforma:** diferença entre `IPP_médio(2018..2024)` e `IPP_médio(2015..2017)` por município e setor. Testa se a Reforma Trabalhista de 2017 acelerou o fenômeno.

---

## 4. Ligação de séries CAGED

O CAGED passou por uma ruptura metodológica em janeiro de 2020, quando foi substituído pelo Novo CAGED (com base no eSocial). As séries não são diretamente comparáveis.

O procedimento de ligação adotado segue a nota técnica do MTE (2020):

1. Para o período 2015–2019: usar série histórica CAGED original.
2. Para o período 2020–2024: usar Novo CAGED.
3. Calcular o fator de ajuste `k(m,s)` como a razão entre as médias anuais dos últimos 12 meses do CAGED antigo e os primeiros 12 meses do Novo CAGED, por município e setor.
4. Aplicar `k(m,s)` retroativamente à série 2015–2019 para torná-la comparável.

Quando `k(m,s)` for muito distante de 1 (ex: > 1.3 ou < 0.7), a série daquele setor-município é marcada como de baixa confiança e excluída da análise do IPP inter-período.

---

## 5. Controle de qualidade dos dados

### Regras de validação implementadas em dbt

| Regra | Tabela | Tipo |
|---|---|---|
| PIB per capita > 0 | `silver_pib_municipal` | not_null + range |
| Saldo CAGED entre -50.000 e +50.000 por mês-município | `silver_caged_mensal` | range |
| Código IBGE existe na tabela de municípios | Todas as silver | relationship |
| CNAE de 2 dígitos entre 01 e 99 | `silver_cnpj_mei` | accepted_values |
| Não há duplicatas de município × setor × mês | `silver_caged_mensal` | unique |
| Estoque de MEIs nunca negativo | `silver_cnpj_mei` | range |

### Tratamento de valores ausentes

- **PIB municipal:** anos com dados ausentes são interpolados linearmente. Se mais de 2 anos consecutivos estão ausentes, o município é excluído daquele componente do IDE.
- **CAGED:** meses com ausência de dados (raros, geralmente municípios muito pequenos) são tratados como saldo zero — conservador e documentado.
- **MEIs:** ausência de registro no arquivo CNPJ para um município-setor-mês é tratada como zero MEIs — pode subestimar levemente o IPP em municípios pequenos.

---

## 6. Software e pacotes

| Pacote | Versão | Uso |
|---|---|---|
| Python | 3.11 | Base |
| pandas | 2.x | Manipulação de dados |
| geopandas | 0.14 | Dados geoespaciais |
| folium | 0.15 | Mapas interativos |
| dbt-bigquery | 1.7+ | Transformações no warehouse |
| google-cloud-bigquery | 3.x | Conexão BigQuery |
| scipy | 1.12 | Cálculos estatísticos |
| matplotlib / seaborn | latest | Visualizações exploratórias |

---

## Referências metodológicas

- HIDALGO, C.; HAUSMANN, R. The building blocks of economic complexity. *PNAS*, v.106, n.26, 2009.
- HAUSMANN, R. et al. *The Atlas of Economic Complexity*. MIT Press, 2014.
- GOMES, L. et al. Economic complexity and regional economic development: evidence from Brazil. *ANPEC*, 2022.
- OECD. *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publishing, 2008.
- MTE. *Nota técnica: metodologia de ligação das séries CAGED e Novo CAGED*. Ministério do Trabalho e Emprego, 2020.
- TORBITONI, G. et al. Pejotização e seus impactos na precarização das relações de trabalho no Brasil. *Observatório da Economia Latino-americana*, v.24, n.1, 2026.
