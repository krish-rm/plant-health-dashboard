import os
import pandas as pd
import gcsfs
import logging
from airflow.models import Variable

# Load variables
RAW_CSV_PATH = Variable.get("RAW_CSV_PATH")
INGESTED_DATA_PATH = Variable.get("INGESTED_DATA_PATH")

def ingest_data():
    try:
        logging.info(f"Reading raw CSV from: {RAW_CSV_PATH}")
        df = pd.read_csv(RAW_CSV_PATH)

        logging.info(f"Saving ingested data to: {INGESTED_DATA_PATH}")
        fs = gcsfs.GCSFileSystem()
        with fs.open(INGESTED_DATA_PATH, 'wt') as f:
            df.to_csv(f, index=False)

        logging.info("✅ Ingestion completed.")
    except Exception as e:
        logging.error(f"❌ Error during ingestion: {e}")
        raise

if __name__ == "__main__":
    ingest_data()
