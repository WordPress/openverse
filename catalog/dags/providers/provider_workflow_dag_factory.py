"""
# Provider Workflow DAG Factory

This file iterates over the configurations defined in PROVIDER_WORKFLOWS
and generates a provider workflow DAG in Airflow for each.
"""

from providers.provider_dag_factory import create_provider_api_workflow_dag
from providers.provider_workflows import PROVIDER_WORKFLOWS


for provider_workflow in PROVIDER_WORKFLOWS:
    globals()[provider_workflow.dag_id] = create_provider_api_workflow_dag(
        provider_workflow
    )
