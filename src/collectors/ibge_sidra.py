"""Collector de dados do IBGE para os municípios do Vale do Paraíba.

Fontes:
  - SIDRA tabela 5938: PIB dos Municípios (N6, 2010–2021)
  - municipalities.yaml: população do Censo 2022 (já disponível no config)

Nota sobre estimativas populacionais anuais:
  O IBGE publica estimativas municipais anuais apenas como arquivos Excel,
  sem endpoint SIDRA no nível N6. Para o IDE, usamos o Censo 2022 como âncora.
  Download manual em: https://www.ibge.gov.br/estatisticas/sociais/populacao/9103
"""
import gzip
import json
import time
import urllib.request

import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseCollector, PROJECT_ROOT

_SIDRA_BASE = "https://servicodados.ibge.gov.br/api/v3/agregados"

_MISSING_VALUES = frozenset({"-", "X", "...", "nd", ""})


class IbgeSidraCollector(BaseCollector):
    """Coleta PIB municipal via SIDRA e população via config."""

    TABLES = {
        "pib_municipal": {
            "tabela": 5938,
            "variaveis": "37|498|513|517|6575",
            # Variáveis confirmadas via teste na API (2026-03):
            # 37   = PIB total a preços correntes (Mil Reais)
            # 498  = VA bruto total a preços correntes (Mil Reais)
            # 513  = VA agropecuária a preços correntes (Mil Reais)
            # 517  = VA indústria a preços correntes (Mil Reais)
            # 6575 = VA serviços exc. adm. pública (Mil Reais)
            # Nota: impostos = PIB(37) - VA_total(498); VA_adm_pub = VA_total - setores
            "periodo_max": 2021,  # PIB municipal tem lag de 2-3 anos
            "gcs_dir": "raw/ibge/sidra/pib_municipal",
        },
    }

    def collect_all(self, start_year: int = 2015) -> dict[str, str]:
        """Coleta PIB via SIDRA e população via config. Retorna dict {nome: gs_uri}."""
        uris = {}
        uris["pib_municipal"] = self.collect_pib_municipal(start_year)
        uris["populacao_censo2022"] = self.collect_populacao_from_config()
        return uris

    def collect_pib_municipal(self, start_year: int = 2015) -> str:
        return self._collect_table("pib_municipal", start_year)

    def collect_populacao_from_config(self) -> str:
        """Extrai população do Censo 2022 do municipalities.yaml e sobe para GCS."""
        self.logger.info("Extraindo população Censo 2022 do config…")
        records = [
            {
                "municipio_id": m["id"],
                "municipio_nome": m["name"],
                "periodo": 2022,
                "variavel": "populacao_censo_2022",
                "valor": m["population_2022"],
                "_ingested_at": pd.Timestamp.now(tz="UTC").isoformat(),
            }
            for m in self.municipalities
        ]
        df = pd.DataFrame(records)
        gcs_path = "raw/ibge/populacao/populacao_censo2022.json"
        uri = self.upload_dataframe(df, gcs_path, fmt="json")
        self.logger.success(f"População Censo 2022: {len(df)} municípios → {uri}")
        return uri

    # -------------------------------------------------------------------------
    # Internos
    # -------------------------------------------------------------------------

    def _collect_table(self, name: str, start_year: int) -> str:
        """Busca um município por vez para contornar limite da API SIDRA."""
        cfg = self.TABLES[name]
        end_year = cfg["periodo_max"]
        periodos = "|".join(str(y) for y in range(start_year, end_year + 1))

        self.logger.info(f"Coletando '{name}' do IBGE SIDRA ({len(self.municipalities)} municípios)…")
        frames = []
        for mun in self.municipalities:
            mun_id = mun["id"]
            url = (
                f"{_SIDRA_BASE}/{cfg['tabela']}"
                f"/periodos/{periodos}"
                f"/variaveis/{cfg['variaveis']}"
                f"?localidades=N6[{mun_id}]"
            )
            try:
                raw = self._fetch(url)
                df = self._normalize(raw)
                if not df.empty:
                    frames.append(df)
                    self.logger.debug(f"  {mun['short_name']}: {len(df)} registros")
            except Exception as e:
                self.logger.warning(f"  {mun['short_name']} ({mun_id}): falhou — {e}")

        if not frames:
            raise RuntimeError(f"Nenhum dado coletado para '{name}'")

        result = pd.concat(frames, ignore_index=True)
        result["_ingested_at"] = pd.Timestamp.now(tz="UTC").isoformat()

        gcs_path = f"{cfg['gcs_dir']}/{name}_{start_year}_{end_year}.json"
        uri = self.upload_dataframe(result, gcs_path, fmt="json")
        self.logger.success(f"'{name}': {len(result):,} registros → {uri}")
        return uri

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def _fetch(self, url: str) -> list[dict]:
        """GET na API SIDRA.

        Usa urllib.request em vez de requests para preservar | e [ literais
        na URL — o SIDRA retorna 500 se receber %7C ou %5B.
        """
        time.sleep(0.3)
        self.logger.debug(f"GET {url}")
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
        # O SIDRA às vezes retorna gzip sem informar no Content-Encoding
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = gzip.decompress(raw).decode("utf-8")
        return json.loads(text)

    def _normalize(self, data: list[dict]) -> pd.DataFrame:
        """Transforma resposta aninhada do SIDRA em DataFrame tidy."""
        records = []
        for var_block in data:
            variavel = var_block.get("variavel", "")
            for resultado in var_block.get("resultados", []):
                for serie in resultado.get("series", []):
                    mun_id = serie["localidade"]["id"]
                    mun_nome = serie["localidade"]["nome"]
                    for periodo, valor in serie["serie"].items():
                        records.append({
                            "municipio_id": mun_id,
                            "municipio_nome": mun_nome,
                            "periodo": int(periodo),
                            "variavel": variavel,
                            "valor": None if valor in _MISSING_VALUES else valor,
                        })
        return pd.DataFrame(records)
