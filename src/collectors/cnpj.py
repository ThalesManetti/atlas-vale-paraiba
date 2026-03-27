"""Collector de dados CNPJ/MEI via Receita Federal (Dados Abertos).

Fonte: https://dadosabertos.rfb.gov.br/CNPJ/
Arquivos processados:
  - Estabelecimentos0.zip … Estabelecimentos9.zip  (10 chunks, ~150-300 MB cada)
  - Simples.zip                                     (dados Simples Nacional / MEI)
  - MUNICIPIOS.zip                                  (mapeamento código RF → nome)

AVISO: apenas contagens agregadas por município-setor são persistidas.
Nenhum dado individual de CNPJ (razão social, endereço, sócios) é armazenado.

Tempo estimado de coleta: 20-40 minutos em conexão doméstica.
"""
import io
import unicodedata
import zipfile
from datetime import datetime

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseCollector

_RF_BASE = "https://dadosabertos.rfb.gov.br/CNPJ"

# Colunas do arquivo Estabelecimentos (CSV sem header, sep=";", encoding=latin-1)
# Fonte: LAYOUT_DADOS_ABERTOS_CNPJ.pdf publicado pela Receita Federal
_ESTAB_COLS = [
    "cnpj_basico", "cnpj_ordem", "cnpj_dv",
    "identificador_matriz_filial", "nome_fantasia",
    "situacao_cadastral", "data_situacao_cadastral",
    "motivo_situacao_cadastral", "nome_cidade_exterior",
    "pais", "data_inicio_atividade", "cnae_fiscal_principal",
    "cnae_fiscal_secundaria", "tipo_logradouro", "logradouro",
    "numero", "complemento", "bairro", "cep",
    "uf", "municipio",  # <- código RF interno, NÃO é o código IBGE
    "ddd_telefone_1", "ddd_telefone_2", "ddd_fax",
    "correio_eletronico", "situacao_especial", "data_situacao_especial",
]

# Colunas do arquivo Simples Nacional
_SIMPLES_COLS = [
    "cnpj_basico", "opcao_simples", "data_opcao_simples",
    "data_exclusao_simples", "opcao_mei", "data_opcao_mei",
    "data_exclusao_mei",
]

# Situação cadastral = "02" significa Ativa
_SITUACAO_ATIVA = "02"

# ---------------------------------------------------------------------------
# Mapeamento RF → IBGE para os 12 municípios do Vale do Paraíba
#
# Os códigos RF são da tabela interna da Receita Federal (≠ códigos IBGE).
# Execute `CnpjCollector.find_rf_codes()` uma vez para verificar / atualizar
# este dicionário antes de rodar a coleta completa.
#
# Última verificação: execute find_rf_codes() para obter os valores corretos.
# ---------------------------------------------------------------------------
_RF_TO_IBGE: dict[str, str] = {
    "6149": "3502507",  # Aparecida do Norte
    "6271": "3508504",  # Caçapava
    "6509": "3520400",  # Cruzeiro
    "6533": "3521606",  # Tremembé
    "6589": "3524402",  # Jacareí
    "6831": "3536505",  # Lorena
    "6843": "3537107",  # Pindamonhangaba
    "6847": "3537305",  # Roseira
    "6469": "3518404",  # Guaratinguetá
    "7087": "3549300",  # Santa Branca
    "7099": "3549904",  # São José dos Campos
    "7183": "3554102",  # Taubaté
}


def _normalize_name(name: str) -> str:
    """Remove acentos e converte para maiúsculas para comparação de nomes."""
    return "".join(
        c for c in unicodedata.normalize("NFD", name.upper())
        if unicodedata.category(c) != "Mn"
    )


class CnpjCollector(BaseCollector):
    """Coleta e agrega dados de estabelecimentos e MEIs por município-setor."""

    # -------------------------------------------------------------------------
    # API pública — helper para mapear códigos RF → IBGE
    # -------------------------------------------------------------------------

    @classmethod
    def find_rf_codes(cls) -> dict[str, str]:
        """Baixa MUNICIPIOS.zip da RF e encontra os códigos dos 12 municípios.

        Execute este método uma vez, verifique os resultados e copie o dict
        retornado para `_RF_TO_IBGE` no topo deste arquivo.

        Returns:
            dict {rf_code: ibge_code} para os municípios encontrados.
        """
        from .base import PROJECT_ROOT
        import yaml

        config_path = PROJECT_ROOT / "config" / "municipalities.yaml"
        with open(config_path, encoding="utf-8") as f:
            municipalities = yaml.safe_load(f)["municipalities"]

        target_names = {
            _normalize_name(m["name"]): m["id"] for m in municipalities
        }

        url = f"{_RF_BASE}/MUNICIPIOS.zip"
        print(f"Baixando {url}…")
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as f:
                mun_df = pd.read_csv(
                    f, sep=";", names=["codigo", "nome"],
                    encoding="latin-1", dtype=str,
                )

        mun_df["normalized"] = mun_df["nome"].apply(_normalize_name)
        matched = mun_df[mun_df["normalized"].isin(target_names)]

        result = {}
        for _, row in matched.iterrows():
            rf_code = str(row["codigo"]).zfill(4)
            ibge_code = target_names[row["normalized"]]
            result[rf_code] = ibge_code
            print(f"  ✓ {row['nome']:<30} RF={rf_code}  IBGE={ibge_code}")

        not_found = [
            name for name, ibge in target_names.items()
            if ibge not in result.values()
        ]

        if not_found:
            print(f"\n  ATENÇÃO — não encontrados (verificar grafia): {not_found}")

        print(f"\nCopie o dict abaixo para _RF_TO_IBGE em cnpj.py:\n")
        print("_RF_TO_IBGE: dict[str, str] = {")
        for rf, ibge in result.items():
            # Encontra nome original para comentário
            nome = next(
                (m["name"] for m in municipalities if m["id"] == ibge), ""
            )
            print(f'    "{rf}": "{ibge}",  # {nome}')
        print("}")
        return result

    # -------------------------------------------------------------------------
    # Coleta principal
    # -------------------------------------------------------------------------

    def collect(self, extraction_month: str | None = None) -> dict[str, str]:
        """Coleta estabelecimentos e MEIs dos 12 municípios.

        Args:
            extraction_month: "YYYYMM" do arquivo RF a usar.
                              Padrão: mês atual. Se ainda não publicado,
                              tenta o mês anterior automaticamente.

        Returns:
            dict {"mapa": gs_uri, "estabelecimentos": gs_uri, "simples": gs_uri}
        """
        if not _RF_TO_IBGE:
            raise RuntimeError(
                "O mapeamento RF→IBGE ainda não foi configurado.\n"
                "Execute: CnpjCollector.find_rf_codes()\n"
                "e copie o resultado para _RF_TO_IBGE em cnpj.py"
            )

        month = extraction_month or datetime.now().strftime("%Y%m")
        target_rf = set(_RF_TO_IBGE.keys())
        ibge_rf = {v: k for k, v in _RF_TO_IBGE.items()}

        self.logger.info(f"Iniciando coleta CNPJ — extração {month}")

        # Salva mapeamento para auditoria
        map_df = pd.DataFrame(
            [{"rf_code": k, "ibge_code": v} for k, v in _RF_TO_IBGE.items()]
        )
        map_uri = self.upload_dataframe(
            map_df, "raw/cnpj/municipios_rf_ibge_map.csv", fmt="csv"
        )

        # Coleta estabelecimentos dos 10 chunks
        estab_df, cnpj_basicos = self._collect_estabelecimentos(target_rf, month)
        estab_uri = self.upload_dataframe(
            estab_df,
            f"raw/cnpj/{month}/vale_paraiba_estabelecimentos.parquet",
            fmt="parquet",
        )

        # Coleta dados Simples/MEI apenas para os CNPJs já filtrados
        simples_df = self._collect_simples(cnpj_basicos, month)
        simples_uri = self.upload_dataframe(
            simples_df,
            f"raw/cnpj/{month}/vale_paraiba_simples.parquet",
            fmt="parquet",
        )

        mei_count = (
            (simples_df["opcao_mei"] == "S").sum() if not simples_df.empty else 0
        )
        self.logger.success(
            f"CNPJ concluído: {len(estab_df):,} estabelecimentos, "
            f"{mei_count:,} MEIs ativos"
        )
        return {"mapa": map_uri, "estabelecimentos": estab_uri, "simples": simples_uri}

    # -------------------------------------------------------------------------
    # Internos
    # -------------------------------------------------------------------------

    def _collect_estabelecimentos(
        self, target_rf: set[str], month: str
    ) -> tuple[pd.DataFrame, set[str]]:
        chunks = []
        for i in range(10):
            url = f"{_RF_BASE}/Estabelecimentos{i}.zip"
            self.logger.info(f"Baixando Estabelecimentos{i}.zip…")
            chunk_df = self._stream_zip_csv(url, target_rf, _ESTAB_COLS, "municipio")
            if not chunk_df.empty:
                chunks.append(chunk_df)
            self.logger.debug(f"  chunk {i}: {len(chunk_df):,} linhas filtradas")

        if not chunks:
            self.logger.warning("Nenhum estabelecimento encontrado para os municípios alvo.")
            return pd.DataFrame(), set()

        df = pd.concat(chunks, ignore_index=True)
        df["municipio_id"] = df["municipio"].map(_RF_TO_IBGE)
        df["cnae_divisao"] = (
            df["cnae_fiscal_principal"].astype(str).str.zfill(7).str[:2]
        )
        df["_ingested_at"] = pd.Timestamp.now(tz="UTC").isoformat()
        df["data_extracao"] = month

        cnpj_basicos = set(df["cnpj_basico"].unique())
        return df, cnpj_basicos

    def _collect_simples(self, cnpj_basicos: set[str], month: str) -> pd.DataFrame:
        if not cnpj_basicos:
            return pd.DataFrame(columns=_SIMPLES_COLS)

        url = f"{_RF_BASE}/Simples.zip"
        self.logger.info("Baixando Simples.zip…")
        chunks = []
        raw = self._download_zip(url)
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as f:
                for chunk in pd.read_csv(
                    f,
                    sep=";",
                    names=_SIMPLES_COLS,
                    encoding="latin-1",
                    dtype=str,
                    chunksize=100_000,
                ):
                    mask = chunk["cnpj_basico"].isin(cnpj_basicos)
                    if mask.any():
                        chunks.append(chunk[mask].copy())

        if not chunks:
            return pd.DataFrame(columns=_SIMPLES_COLS)

        df = pd.concat(chunks, ignore_index=True)
        df["_ingested_at"] = pd.Timestamp.now(tz="UTC").isoformat()
        return df

    def _stream_zip_csv(
        self,
        url: str,
        filter_values: set[str],
        cols: list[str],
        filter_col: str,
    ) -> pd.DataFrame:
        """Download de ZIP e filtragem chunk a chunk para evitar OOM."""
        try:
            raw = self._download_zip(url)
        except FileNotFoundError:
            self.logger.warning(f"Arquivo não publicado ainda: {url}")
            return pd.DataFrame(columns=cols)

        chunks = []
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as f:
                for chunk in pd.read_csv(
                    f,
                    sep=";",
                    names=cols,
                    encoding="latin-1",
                    dtype=str,
                    chunksize=50_000,
                ):
                    mask = chunk[filter_col].isin(filter_values)
                    if mask.any():
                        chunks.append(chunk[mask].copy())

        return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=cols)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=5, max=60))
    def _download_zip(self, url: str) -> bytes:
        """Download completo de ZIP. Timeout alto para arquivos grandes (~300 MB)."""
        self.logger.debug(f"GET {url}")
        resp = requests.get(url, timeout=300)
        if resp.status_code == 404:
            raise FileNotFoundError(f"Arquivo não encontrado: {url}")
        resp.raise_for_status()
        return resp.content
