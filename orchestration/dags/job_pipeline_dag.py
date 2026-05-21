# DAG Airflow — orchestration du pipeline complet
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, "/opt/airflow/project")

from ingestion.batch_loader import run_batch
from medallion.etl_pipeline import run_etl
from quality.expectations import run_quality_checks

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="job_market_pipeline",
    default_args=default_args,
    description="Pipeline Job Market Intelligence",
    schedule_interval="@hourly",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["job-market", "scraping", "etl"],
) as dag:

    t1 = PythonOperator(
        task_id="scrape_and_ingest_batch",
        python_callable=run_batch,
    )

    t2 = PythonOperator(
        task_id="etl_bronze_to_gold",
        python_callable=run_etl,
    )

    t3 = PythonOperator(
        task_id="quality_checks",
        python_callable=run_quality_checks,
    )

    t1 >> t2 >> t3