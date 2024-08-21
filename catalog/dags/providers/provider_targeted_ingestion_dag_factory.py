"""
# Provider Targeted Ingestion Workflow DAG Factory

This file iterates over the configurations defined in PROVIDER_TARGETED_INGESTION_WORKFLOWS
and generates a targeted ingestion workflow DAG for each.
"""

from providers.provider_dag_factory import create_targeted_ingestion_dag
from providers.provider_targeted_ingestion_workflows import (
    PROVIDER_TARGETED_INGESTION_WORKFLOWS,
)


for provider_workflow in PROVIDER_TARGETED_INGESTION_WORKFLOWS:
    globals()[provider_workflow.dag_id] = create_targeted_ingestion_dag(
        provider_workflow
    )
