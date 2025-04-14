from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import os
import logging

current_date = datetime.today()

GCS_BUCKET_NAME = Variable.get("GCS_BUCKET_NAME", default_var="your-bucket")
BQ_PROJECT_ID = Variable.get("GCP_PROJECT_ID", default_var="your-project-id")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RAW_CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "plant_health_data.csv")
logging.info(f"Resolved raw CSV path: {RAW_CSV_PATH}")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": current_date,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "plant_health_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Orchestrates ingest → clean → load for plant health data",
) as dag:

    ingest_task = BashOperator(
        task_id="ingest_data",
        bash_command="python /home/airflow/gcs/dags/ingest_data.py",
    )

    clean_task = BashOperator(
        task_id="clean_data",
        bash_command="python /home/airflow/gcs/dags/clean_data.py",
    )

    bq_task = BashOperator(
        task_id="load_to_bigquery",
        bash_command="python /home/airflow/gcs/dags/load_to_bigquery.py",
    )

    ingest_task >> clean_task >> bq_task