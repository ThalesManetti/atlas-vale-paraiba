"""Collector de dados CAGED via Base dos Dados (dataset público no BigQuery).

Fonte: https://basedosdados.org/dataset/br-me-caged
Tabelas:
  - basedosdados.br_me_caged.microdados_antigos      → CAGED antigo (2015–2019)
  - basedosdados.br_me_caged.microdados_movimentacao → Novo CAGED (2020–2024)

IMPORTANTE: As consultas são cobradas ao projeto GCP configurado (~5-15 GB por consulta).
O custo fica dentro do free tier do BigQuery (1 TB/mês) para uso de pesquisa normal.
"""
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from google.cloud import bigquery

from .base import BaseCollector

# Tabelas públicas no projeto Base dos Dados
# Verificar nomes atuais em: https://basedosdados.org/dataset/br-me-caged
_BDD_CAGED_ANTIGO = "basedosdados.br_me_caged.microdados_antigos"
_BDD_NOVO_CAGED = "basedosdados.br_me_caged.microdados_movimentacao"


class CagedCollector(BaseCollector):
    """Coleta dados CAGED agrupados por município × setor × mês via Base dos Dados."""

    def collect_all(
        self,
        start_year: int = 2015,
        end_year: int = 2024,
    ) -> dict[str, str]:
        """Coleta ambas as séries em paralelo e retorna dict {nome: gs_uri}."""
        with ThreadPoolExecutor(max_workers=2) as executor:
            fut_antigo = executor.submit(self.collect_caged_antigo, start_year=start_year)
            fut_novo = executor.submit(self.collect_novo_caged, end_year=end_year)
        return {
            "caged_antigo": fut_antigo.result(),
            "novo_caged": fut_novo.result(),
        }

    def collect_caged_antigo(
        self, start_year: int = 2015, end_year: int = 2019
    ) -> str:
        self.logger.info(f"Consultando CAGED antigo {start_year}–{end_year} no BDD…")
        df = self._run_query(self._sql_caged_antigo(start_year, end_year))
        df["fonte_caged"] = "CAGED_ANTIGO"
        df["_ingested_at"] = pd.Timestamp.now(tz="UTC").isoformat()

        gcs_path = f"raw/caged/bq_export/caged_antigo_{start_year}_{end_year}.parquet"
        uri = self.upload_dataframe(df, gcs_path, fmt="parquet")
        self.logger.success(f"CAGED antigo: {len(df):,} linhas → {uri}")
        return uri

    def collect_novo_caged(
        self, start_year: int = 2020, end_year: int = 2024
    ) -> str:
        self.logger.info(f"Consultando Novo CAGED {start_year}–{end_year} no BDD…")
        df = self._run_query(self._sql_novo_caged(start_year, end_year))
        df["fonte_caged"] = "NOVO_CAGED"
        df["_ingested_at"] = pd.Timestamp.now(tz="UTC").isoformat()

        gcs_path = f"raw/caged/bq_export/novo_caged_{start_year}_{end_year}.parquet"
        uri = self.upload_dataframe(df, gcs_path, fmt="parquet")
        self.logger.success(f"Novo CAGED: {len(df):,} linhas → {uri}")
        return uri

    # -------------------------------------------------------------------------
    # SQL
    # -------------------------------------------------------------------------

    def _sql_caged_antigo(self, start_year: int, end_year: int) -> str:
        muns = ", ".join(f"'{m}'" for m in self.municipality_ids)
        return f"""
        -- CAGED antigo: saldo_movimentacao = 1 (admissão) ou -1 (desligamento)
        -- Agrupado em município × CNAE-divisão × ano × mês
        SELECT
            id_municipio                                                    AS municipio_id,
            LEFT(LPAD(CAST(cnae_2_subclasse AS STRING), 7, '0'), 2)        AS cnae_divisao,
            ano,
            mes,
            COUNTIF(saldo_movimentacao > 0)                                 AS admissoes,
            COUNTIF(saldo_movimentacao < 0)                                 AS desligamentos,
            SUM(saldo_movimentacao)                                         AS saldo
        FROM `{_BDD_CAGED_ANTIGO}`
        WHERE id_municipio IN ({muns})
          AND ano BETWEEN {start_year} AND {end_year}
        GROUP BY municipio_id, cnae_divisao, ano, mes
        ORDER BY municipio_id, cnae_divisao, ano, mes
        """

    def _sql_novo_caged(self, start_year: int, end_year: int) -> str:
        muns = ", ".join(f"'{m}'" for m in self.municipality_ids)
        return f"""
        -- Novo CAGED: saldo_movimentacao = +1 (admissão) ou -1 (desligamento) por linha
        -- Agrupado em município × CNAE-divisão × ano × mês
        SELECT
            id_municipio                                                    AS municipio_id,
            LEFT(LPAD(CAST(cnae_2_subclasse AS STRING), 7, '0'), 2)        AS cnae_divisao,
            ano,
            mes,
            COUNTIF(saldo_movimentacao > 0)                                 AS admissoes,
            COUNTIF(saldo_movimentacao < 0)                                 AS desligamentos,
            SUM(saldo_movimentacao)                                         AS saldo
        FROM `{_BDD_NOVO_CAGED}`
        WHERE id_municipio IN ({muns})
          AND ano BETWEEN {start_year} AND {end_year}
        GROUP BY municipio_id, cnae_divisao, ano, mes
        ORDER BY municipio_id, cnae_divisao, ano, mes
        """

    # -------------------------------------------------------------------------
    # BigQuery
    # -------------------------------------------------------------------------

    def _run_query(self, sql: str) -> pd.DataFrame:
        job_config = bigquery.QueryJobConfig(use_query_cache=True)
        job = self.bq.query(sql, job_config=job_config)
        return job.to_dataframe(progress_bar_type=None)
