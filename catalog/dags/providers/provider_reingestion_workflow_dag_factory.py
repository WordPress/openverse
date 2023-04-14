"""
# Ingestion Workflow Dag Factory

This file iterates over the configurations defined in PROVIDER_INGESTION_WORKFLOWS
and generates a day-partitioned ingestion workflow DAG in Airflow for each.

These DAGs generate a list of `reingestion_days` for which to run the `main`
function from the provided `provider_script`, and run the function. Currently,
this will only pull data for each of the given days and create the tsv; the
loading step is not yet wired up.
"""

from common.helpers import IngestionInput, get_partitioned_reingestion_days
from providers.provider_dag_factory import create_day_partitioned_reingestion_dag
from providers.provider_reingestion_workflows import PROVIDER_REINGESTION_WORKFLOWS


for config in PROVIDER_REINGESTION_WORKFLOWS:
    partitioned_reingestion_days = get_partitioned_reingestion_days(
        [
            IngestionInput(1, config.daily_list_length),
            IngestionInput(7, config.weekly_list_length),
            IngestionInput(15, config.fortnightly_list_length),
            IngestionInput(30, config.one_month_list_length),
            IngestionInput(90, config.three_month_list_length),
            IngestionInput(180, config.six_month_list_length),
        ]
    )

    globals()[config.dag_id] = create_day_partitioned_reingestion_dag(
        config, partitioned_reingestion_days
    )
