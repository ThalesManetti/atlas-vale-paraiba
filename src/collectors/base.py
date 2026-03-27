import io
import os
from pathlib import Path
from typing import Literal

import pandas as pd
import yaml
from dotenv import load_dotenv
from google.cloud import bigquery, storage
from loguru import logger

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent


class BaseCollector:
    """Classe base para todos os collectors do Atlas Vale Paraíba.

    Gerencia clientes GCS/BigQuery com lazy init e centraliza
    o upload de dados para o bucket bronze.
    """

    def __init__(self) -> None:
        self.project_id: str = os.environ["GCP_PROJECT_ID"]
        self.bucket_name: str = os.environ["GCS_BUCKET"]
        self.raw_prefix: str = os.getenv("GCS_RAW_PREFIX", "raw/")
        self.municipalities: list[dict] = self._load_municipalities()
        self._gcs_client: storage.Client | None = None
        self._bq_client: bigquery.Client | None = None
        self.logger = logger.bind(collector=self.__class__.__name__)

    # -------------------------------------------------------------------------
    # Clientes GCP — lazy init para não criar conexão antes de precisar
    # -------------------------------------------------------------------------

    @property
    def gcs(self) -> storage.Client:
        if self._gcs_client is None:
            # project deve ser passado explicitamente — ADC pode detectar
            # o projeto errado em ambientes Windows sem GOOGLE_CLOUD_PROJECT
            self._gcs_client = storage.Client(project=self.project_id)
        return self._gcs_client

    @property
    def bq(self) -> bigquery.Client:
        if self._bq_client is None:
            self._bq_client = bigquery.Client(project=self.project_id)
        return self._bq_client

    # -------------------------------------------------------------------------
    # Municípios
    # -------------------------------------------------------------------------

    def _load_municipalities(self) -> list[dict]:
        config_path = PROJECT_ROOT / "config" / "municipalities.yaml"
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)["municipalities"]

    @property
    def municipality_ids(self) -> list[str]:
        return [m["id"] for m in self.municipalities]

    # -------------------------------------------------------------------------
    # Upload para GCS
    # -------------------------------------------------------------------------

    def upload_dataframe(
        self,
        df: pd.DataFrame,
        gcs_path: str,
        fmt: Literal["parquet", "json", "csv"] = "parquet",
    ) -> str:
        """Serializa DataFrame e faz upload para GCS. Retorna gs:// URI."""
        if fmt == "parquet":
            buf = io.BytesIO()
            df.to_parquet(buf, index=False)
            data = buf.getvalue()
            content_type = "application/octet-stream"
        elif fmt == "json":
            data = df.to_json(
                orient="records", force_ascii=False
            ).encode("utf-8")
            content_type = "application/json"
        else:
            data = df.to_csv(index=False).encode("utf-8")
            content_type = "text/csv"

        return self.upload_bytes(data, gcs_path, content_type)

    def upload_bytes(
        self,
        data: bytes,
        gcs_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Faz upload de bytes brutos para GCS. Retorna gs:// URI."""
        bucket = self.gcs.bucket(self.bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(data, content_type=content_type)
        uri = f"gs://{self.bucket_name}/{gcs_path}"
        self.logger.info(f"Upload → {uri} ({len(data):,} bytes)")
        return uri
