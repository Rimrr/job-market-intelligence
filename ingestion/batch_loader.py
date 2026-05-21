"""
minio_loader.py
Fonctions d'upload vers les buckets Bronze / Silver / Gold de MinIO.
À placer dans : ingestion/batch_loader.py  (ou importer depuis ici)
"""

import io
import json
import datetime
import pandas as pd
from minio import Minio
from minio.error import S3Error

# ──────────────────────────────────────────────
# Configuration MinIO  →  adapte ces valeurs
# ──────────────────────────────────────────────
MINIO_ENDPOINT   = "localhost:9000"   # ex: "minio:9000" si Docker Compose
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_SECURE     = False              # True si HTTPS

BUCKET_BRONZE = "bronze"
BUCKET_SILVER = "silver"
BUCKET_GOLD   = "gold"

# ──────────────────────────────────────────────
# Client singleton
# ──────────────────────────────────────────────
def _get_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def _ensure_bucket(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        print(f"✅ Bucket créé : {bucket}")


# ──────────────────────────────────────────────
# Helpers génériques
# ──────────────────────────────────────────────
def _upload_json(client: Minio, bucket: str, object_name: str, data: list | dict) -> None:
    payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    client.put_object(
        bucket,
        object_name,
        io.BytesIO(payload),
        length=len(payload),
        content_type="application/json",
    )
    print(f"📤 Uploadé → {bucket}/{object_name}  ({len(payload):,} bytes)")


def _upload_parquet(client: Minio, bucket: str, object_name: str, df: pd.DataFrame) -> None:
    buf = io.BytesIO()
    df.to_parquet(buf, index=False, engine="pyarrow")
    buf.seek(0)
    size = buf.getbuffer().nbytes
    client.put_object(
        bucket,
        object_name,
        buf,
        length=size,
        content_type="application/octet-stream",
    )
    print(f"📤 Uploadé → {bucket}/{object_name}  ({size:,} bytes, {len(df)} lignes)")


# ──────────────────────────────────────────────
# Bronze  –  données brutes JSON
# ──────────────────────────────────────────────
def upload_to_bronze(offers: list, source: str) -> None:
    """Sauvegarde les offres brutes dans bronze/<source>/<timestamp>.json"""
    client = _get_client()
    _ensure_bucket(client, BUCKET_BRONZE)

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    object_name = f"{source}/{ts}.json"
    _upload_json(client, BUCKET_BRONZE, object_name, offers)


# ──────────────────────────────────────────────
# Silver  –  DataFrame nettoyé → Parquet
# ──────────────────────────────────────────────
def upload_to_silver(df: pd.DataFrame, source: str) -> None:
    """
    Sauvegarde le DataFrame Silver dans silver/<source>/<timestamp>.parquet

    Appel typique :
        from ingestion.batch_loader import upload_to_silver
        upload_to_silver(df_clean, source="linkedin")
    """
    client = _get_client()
    _ensure_bucket(client, BUCKET_SILVER)

    # Les listes (skills) ne sont pas sérialisables en Parquet → on les convertit en string
    df_safe = df.copy()
    if "skills" in df_safe.columns:
        df_safe["skills"] = df_safe["skills"].apply(
            lambda x: ",".join(x) if isinstance(x, list) else (x or "")
        )

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    object_name = f"{source}/{ts}.parquet"
    _upload_parquet(client, BUCKET_SILVER, object_name, df_safe)


# ──────────────────────────────────────────────
# Gold  –  tables agrégées → Parquet (1 fichier par table)
# ──────────────────────────────────────────────
def upload_to_gold(gold_tables: dict, run_label: str = None) -> None:
    """
    Sauvegarde chaque table du dictionnaire Gold dans gold/<table_name>/<timestamp>.parquet

    Appel typique :
        from ingestion.batch_loader import upload_to_gold
        upload_to_gold(gold_dict, run_label="2026-05-15")

    gold_tables : dict retourné par build_gold_tables()
        {
          "top_skills":       pd.DataFrame,
          "offers_by_city":   pd.DataFrame,
          "salary_by_city":   pd.DataFrame,
          "offers_by_source": pd.DataFrame,
          "offers_over_time": pd.DataFrame,
        }
    """
    client = _get_client()
    _ensure_bucket(client, BUCKET_GOLD)

    ts = run_label or datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    for table_name, df in gold_tables.items():
        if df is None or df.empty:
            print(f"⚠️  Gold [{table_name}] vide — ignoré")
            continue
        object_name = f"{table_name}/{ts}.parquet"
        _upload_parquet(client, BUCKET_GOLD, object_name, df)