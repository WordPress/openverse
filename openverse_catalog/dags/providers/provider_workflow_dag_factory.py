""""
# Provider Workflow Dag Factory

This file iterates over the configurations defined in PROVIDER_WORKFLOWS
and generates a provider workflow DAG in Airflow for each.
"""

import importlib

from common.provider_dag_factory import create_provider_api_workflow
from providers.provider_workflows import PROVIDER_WORKFLOWS


for provider_workflow in PROVIDER_WORKFLOWS:
    provider_script = importlib.import_module(
        f"providers.provider_api_scripts.{provider_workflow.provider_script}"
    )

    globals()[provider_workflow.dag_id] = create_provider_api_workflow(
        provider_workflow.dag_id,
        provider_script.main,
        provider_workflow.default_args,
        provider_workflow.start_date,
        provider_workflow.max_active_runs,
        provider_workflow.max_active_tasks,
        provider_workflow.schedule_string,
        provider_workflow.dated,
        provider_workflow.day_shift,
        provider_workflow.execution_timeout,
        provider_script.__doc__,
        provider_workflow.media_types,
    )
