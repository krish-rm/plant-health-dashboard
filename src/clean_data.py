import pandas as pd
import gcsfs
import logging
from airflow.models import Variable

INGESTED_DATA_PATH = Variable.get("INGESTED_DATA_PATH")
PROCESSED_DATA_PATH = Variable.get("PROCESSED_DATA_PATH")

def clean_data():
    try:
        logging.info(f"Reading ingested raw data from: {INGESTED_DATA_PATH}")
        fs = gcsfs.GCSFileSystem()

        with fs.open(INGESTED_DATA_PATH, 'rt') as f:
            df = pd.read_csv(f)

        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        df.dropna(subset=["Timestamp"], inplace=True)

        logging.info(f"Saving cleaned data to: {PROCESSED_DATA_PATH}")
        with fs.open(PROCESSED_DATA_PATH, 'wb') as f:
            df.to_parquet(f, index=False, engine='pyarrow')

        logging.info("✅ Data cleaning completed.")
    except Exception as e:
        logging.error(f"❌ Error during cleaning: {e}")
        raise

if __name__ == "__main__":
    clean_data()
