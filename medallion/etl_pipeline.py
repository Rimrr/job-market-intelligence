from datalake.minio_client import read_all_bronze
from medallion.silver import transform_to_silver
from medallion.gold import build_gold_tables
from warehouse.loader import load_to_warehouse
from ingestion.batch_loader import upload_to_silver, upload_to_gold   


def run_etl():
    print("\n=== DÉMARRAGE ETL ===")

    # EXTRACT depuis Bronze (MinIO)
    raw = read_all_bronze()
    if not raw:
        print("❌ Aucune donnée dans Bronze !")
        return

    print(f"E: {len(raw)} offres extraites du Data Lake")

    # TRANSFORM → Silver
    df_silver = transform_to_silver(raw)
    upload_to_silver(df_silver, source="all")

    # TRANSFORM → Gold
    gold_tables = build_gold_tables(df_silver)
    upload_to_gold(gold_tables)

    # LOAD → PostgreSQL
    load_to_warehouse(df_silver, gold_tables)

    print("=== ETL TERMINÉ ✅ ===\n")

if __name__ == "__main__":
    run_etl()