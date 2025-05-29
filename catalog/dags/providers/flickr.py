# catalog/dags/providers/flickr.py

from airflow import DAG
from datetime import datetime
from providers.shared import ingest_flickr_data  # assume you have this

with DAG(
    dag_id="ingest_flickr_data",
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["ingestion", "flickr"]
) as dag:
    ingest_task = ingest_flickr_data()
