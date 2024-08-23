"""
# Create and Promote Index

This file contains TaskGroups related to creating and populating the filtered Elasticsearch indices
as part of the Data Refresh.

TODO: We'll swap out the create and populate filtered index DAG to use this instead
of the one defined in the legacy_data_refresh.
"""

import logging

from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.utils.trigger_rule import TriggerRule
from requests import Response


logger = logging.getLogger(__name__)
SENSITIVE_TERMS_CONN_ID = "sensitive_terms"


def response_filter_sensitive_terms_endpoint(response: Response) -> list[str]:
    logger.info(response.text)
    return response.text


def get_sensitive_terms() -> HttpOperator | PythonOperator:
    return HttpOperator(
        task_id="get_sensitive_terms",
        http_conn_id=SENSITIVE_TERMS_CONN_ID,
        method="GET",
        response_check=lambda response: response.status_code == 200,
        response_filter=response_filter_sensitive_terms_endpoint,
        trigger_rule=TriggerRule.NONE_FAILED,
    )
