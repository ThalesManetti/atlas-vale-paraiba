# Política de Segurança e Privacidade

## Princípios

Este projeto trata exclusivamente de **dados públicos agregados**. Nenhum dado de pessoa física identificável é coletado, armazenado, versionado ou publicado.

## O que NÃO está neste repositório

| Tipo de dado | Motivo da exclusão |
|---|---|
| Credenciais GCP (service account JSON) | Risco de acesso não autorizado ao projeto GCP |
| Arquivo CNPJ completo da Receita Federal | ~3 GB; contém dados de empresas individuais |
| Microdados RAIS brutos | Podem conter informações individuais de trabalhadores |
| Microdados CAGED brutos | Idem |
| Variáveis de ambiente (`.env`) | Contém IDs de projeto e credenciais |

Todos esses dados ficam exclusivamente no Google Cloud Storage e BigQuery, acessíveis apenas com as credenciais do service account — que nunca são commitadas.

## O que está neste repositório

- Código-fonte (scripts Python, modelos dbt, notebooks)
- Dados agregados processados de pequeno volume (ex: tabelas com 12 linhas — uma por município)
- Documentação e metodologia
- Configurações sem segredos (`.env.example`, `municipalities.yaml`)

## Reprodução segura

Para reproduzir este projeto:

1. **Nunca commite o arquivo `.env`** — ele está no `.gitignore` por design.
2. **Nunca commite o arquivo JSON da service account** — todos os arquivos `*.json` estão no `.gitignore`, exceto `package.json`.
3. **Revise o `.gitignore`** antes de qualquer `git add .`.
4. **Use `git diff --staged`** para inspecionar o que será commitado antes de cada commit.

## Tratamento do arquivo CNPJ

O arquivo de dados abertos CNPJ da Receita Federal contém informações de todos os CNPJs cadastrados no Brasil. Embora seja dado público, o arquivo completo (~3 GB) não é redistribuído neste repositório. O script `src/collectors/cnpj_filter.py` faz o download, filtra apenas os municípios do Vale do Paraíba, e carrega apenas contagens agregadas por município-setor no BigQuery. Os arquivos brutos são descartados após o processamento.

## Relatório de vulnerabilidades

Se você identificar que algum dado sensível foi acidentalmente commitado, abra uma issue privada ou contate o mantenedor diretamente. Em caso de vazamento de credenciais GCP:

1. Revogue imediatamente a chave no Console GCP: IAM → Service Accounts → Chaves → Excluir
2. Gere uma nova chave
3. Use `git filter-repo` para remover o arquivo do histórico

## Conformidade

Os dados utilizados neste projeto são distribuídos sob as seguintes licenças/termos:

- **IBGE:** dados públicos, uso livre com citação da fonte
- **MTE (CAGED/RAIS):** dados públicos, uso livre com citação da fonte
- **Receita Federal (CNPJ):** dados abertos, licença CC BY 4.0
- **SEADE:** dados públicos do Estado de SP, uso livre com citação
