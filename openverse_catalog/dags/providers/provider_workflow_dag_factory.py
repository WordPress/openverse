""""
# Provider Workflow Dag Factory

This file iterates over the configurations defined in PROVIDER_WORKFLOWS
and generates a provider workflow DAG in Airflow for each.
"""

import importlib

from providers.provider_dag_factory import create_provider_api_workflow
from providers.provider_workflows import PROVIDER_WORKFLOWS


for provider_workflow in PROVIDER_WORKFLOWS:
    provider_script = importlib.import_module(
        f"providers.provider_api_scripts.{provider_workflow.provider_script}"
    )

    # Use the ingester class if it exists, or fall back to the `main` method
    ingestion_callable = provider_workflow.ingester_class or provider_script.main

    globals()[provider_workflow.dag_id] = create_provider_api_workflow(
        provider_workflow.dag_id,
        ingestion_callable,
        provider_workflow.default_args,
        provider_workflow.start_date,
        provider_workflow.max_active_runs,
        provider_workflow.max_active_tasks,
        provider_workflow.schedule_string,
        provider_workflow.dated,
        provider_workflow.day_shift,
        provider_workflow.pull_timeout,
        provider_workflow.load_timeout,
        provider_script.__doc__,
        provider_workflow.media_types,
        provider_workflow.preingestion_task_creator,
        provider_workflow.postingestion_task_creator,
    )
