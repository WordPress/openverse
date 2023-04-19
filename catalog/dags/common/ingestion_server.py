import logging
import os
from datetime import timedelta
from urllib.parse import urlparse

from airflow.exceptions import AirflowException
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from requests import Response

from common.constants import XCOM_PULL_TEMPLATE


logger = logging.getLogger(__name__)


POKE_INTERVAL = int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60 * 15))


def response_filter_stat(response: Response) -> str:
    """
    Handle the response for the `get_current_index` task.

    This is used to extract the name of the current index that the concerned alias
    points to. This index name will be available via XCom in the downstream tasks.
    """
    index_name = response.json()["alt_names"]
    # Indices are named as '<media type>-<suffix>', so everything after the first
    # hyphen '-' is the suffix.
    _, index_suffix = index_name.split("-", maxsplit=1)
    return index_suffix


def response_filter_status_check_endpoint(response: Response) -> str:
    """
    Handle the response for `trigger_task` task.

    This is used to grab the endpoint needed to poll for the status of the triggered
    data refresh. This information will then be available via XCom in the downstream
    tasks.
    """
    status_check_url = response.json()["status_check"]
    return urlparse(status_check_url).path


def response_check_wait_for_completion(response: Response) -> bool:
    """
    Handle the response for `wait_for_completion` Sensor.

    Processes the response to determine whether the task can complete.
    """
    data = response.json()

    if data["active"]:
        # The data refresh is still running. Poll again later.
        return False

    if data["error"]:
        raise AirflowException(
            "Ingestion server encountered an error during data refresh."
        )

    logger.info(f"Data refresh done with {data['progress']}% completed.")
    return True


def get_current_index(target_alias: str) -> SimpleHttpOperator:
    return SimpleHttpOperator(
        task_id="get_current_index",
        http_conn_id="data_refresh",
        endpoint=f"stat/{target_alias}",
        method="GET",
        response_check=lambda response: response.status_code == 200,
        response_filter=response_filter_stat,
    )


def trigger_task(
    action: str,
    model: str,
    data: dict | None = None,
) -> SimpleHttpOperator:
    data = {
        **(data or {}),
        "model": model,
        "action": action.upper(),
    }
    return SimpleHttpOperator(
        task_id=f"trigger_{action.lower()}",
        http_conn_id="data_refresh",
        endpoint="task",
        data=data,
        response_check=lambda response: response.status_code == 202,
        response_filter=response_filter_status_check_endpoint,
    )


def wait_for_task(
    action: str,
    task_trigger: SimpleHttpOperator,
    timeout: timedelta,
    poke_interval: int = POKE_INTERVAL,
) -> HttpSensor:
    return HttpSensor(
        task_id=f"wait_for_{action.lower()}",
        http_conn_id="data_refresh",
        endpoint=XCOM_PULL_TEMPLATE.format(task_trigger.task_id, "return_value"),
        method="GET",
        response_check=response_check_wait_for_completion,
        mode="reschedule",
        poke_interval=poke_interval,
        timeout=timeout.total_seconds(),
    )


def trigger_and_wait_for_task(
    action: str,
    model: str,
    timeout: timedelta,
    data: dict | None = None,
    poke_interval: int = POKE_INTERVAL,
) -> tuple[SimpleHttpOperator, HttpSensor]:
    trigger = trigger_task(action, model, data)
    waiter = wait_for_task(action, trigger, timeout, poke_interval)
    trigger >> waiter
    return trigger, waiter
