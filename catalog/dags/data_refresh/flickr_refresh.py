# catalog/dags/data_refresh/flickr_refresh.py

from airflow import DAG
from datetime import datetime, timedelta
from common.refresh import refresh_provider_data

with DAG(
    dag_id="refresh_flickr_data",
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["refresh", "flickr"]
) as dag:
    refresh_task = refresh_provider_data("flickr")
