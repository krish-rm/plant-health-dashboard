import os
import logging
import io
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from google.cloud import bigquery, storage
from google.cloud.exceptions import NotFound
from airflow.models import Variable

# Environment Variables
PROJECT_ID = os.getenv("PROJECT_ID")  # Required
REGION = os.getenv("REGION")          # Optional (used by GCP clients implicitly)
ENV_NAME = os.getenv("ENV_NAME")      # Optional (for logging/debugging)

# Airflow Variables
BQ_TABLE_NAME = Variable.get("BQ_TABLE_NAME")  # Format: your-project.dataset.table
PROCESSED_DATA_PATH = Variable.get("PROCESSED_DATA_PATH")  # Parquet file path in GCS

# Derived
GCS_URI = PROCESSED_DATA_PATH
bucket_name = PROCESSED_DATA_PATH.split("/")[2]
blob_name = "/".join(PROCESSED_DATA_PATH.split("/")[3:])
CORRECTED_BLOB_NAME = blob_name.replace("cleaned_", "corrected_")
GCS_CORRECTED_URI = f"gs://{bucket_name}/{CORRECTED_BLOB_NAME}"


def write_parquet_to_gcs(df, bucket_name, destination_blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        parquet_buffer = io.BytesIO()
        pq.write_table(pa.Table.from_pandas(df), parquet_buffer)
        blob.upload_from_string(parquet_buffer.getvalue(), content_type="application/octet-stream")

        logging.info(f"✅ Uploaded corrected Parquet to gs://{bucket_name}/{destination_blob_name}")
    except Exception as e:
        logging.error(f"❌ Error writing corrected Parquet to GCS: {e}")
        raise


def load_parquet_to_bq():
    try:
        bq_client = bigquery.Client(project=PROJECT_ID)

        schema = [
            bigquery.SchemaField("Timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("Plant_ID", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("Soil_Moisture", "FLOAT"),
            bigquery.SchemaField("Ambient_Temperature", "FLOAT"),
            bigquery.SchemaField("Soil_Temperature", "FLOAT"),
            bigquery.SchemaField("Humidity", "FLOAT"),
            bigquery.SchemaField("Light_Intensity", "FLOAT"),
            bigquery.SchemaField("Soil_pH", "FLOAT"),
            bigquery.SchemaField("Nitrogen_Level", "FLOAT"),
            bigquery.SchemaField("Phosphorus_Level", "FLOAT"),
            bigquery.SchemaField("Potassium_Level", "FLOAT"),
            bigquery.SchemaField("Chlorophyll_Content", "FLOAT"),
            bigquery.SchemaField("Electrochemical_Signal", "FLOAT"),
            bigquery.SchemaField("Plant_Health_Status", "STRING"),
        ]

        try:
            bq_client.get_table(BQ_TABLE_NAME)
            logging.info(f"✅ Table exists: {BQ_TABLE_NAME}")
        except NotFound:
            table = bigquery.Table(BQ_TABLE_NAME, schema=schema)
            table.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field="Timestamp")
            bq_client.create_table(table)
            logging.info(f"✅ Created table: {BQ_TABLE_NAME}")

        df = pd.read_parquet(GCS_URI)
        if df.empty:
            logging.warning("⚠️ No data found in Parquet file.")
            return

        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df = df.dropna(subset=["Timestamp"])
        df = df[(df["Timestamp"] >= pd.Timestamp("2000-01-01")) & (df["Timestamp"] <= pd.Timestamp("2100-12-31"))]
        df["Timestamp"] = df["Timestamp"].astype("datetime64[us]")

        write_parquet_to_gcs(df, bucket_name, CORRECTED_BLOB_NAME)

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        load_job = bq_client.load_table_from_uri(GCS_CORRECTED_URI, BQ_TABLE_NAME, job_config=job_config)
        load_job.result()

        logging.info(f"🚀 Successfully loaded data into BigQuery: {BQ_TABLE_NAME}")

    except Exception as e:
        logging.error(f"❌ Error in load_parquet_to_bq: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_parquet_to_bq()
