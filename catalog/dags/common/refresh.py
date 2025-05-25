# catalog/dags/common/refresh.py

from airflow.operators.python import PythonOperator

def refresh_provider_data(provider_name):
    def _refresh():
        print(f"Refreshing data for provider: {provider_name}")
        # TODO: actual refresh logic (reuse from old ingestion file)

    return PythonOperator(
        task_id=f"refresh_{provider_name}_data",
        python_callable=_refresh
    )