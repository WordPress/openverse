from datetime import datetime, timedelta, timezone
from typing import Literal

from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from airflow.operators.python import ShortCircuitOperator
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from airflow.utils.trigger_rule import TriggerRule

from common.slack import send_message


# The name of the Airflow Variable used to track the in-alarm status.
ELASTICSEARCH_HEALTH_IN_ALARM_VAR = "elasticsearch_health_in_alarm"
# Time to wait before re-notifying about a continuous failure.
ALERT_THROTTLE_WINDOW = timedelta(hours=6)

_DAG_ID = "{env}_elasticsearch_health_check"
_SCHEDULE = "*/15 * * * *"  # Every 15 minutes

_SHARED_DAG_ARGS = {
    "schedule": _SCHEDULE,
    "start_date": datetime(2024, 1, 1),
    "catchup": False,
    "doc_md": """
    ### Elasticsearch Health Check

    This DAG checks the health of the Elasticsearch cluster every 15 minutes.

    On a failure, it sends a Slack alert. To prevent alert fatigue, it uses an
    Airflow Variable to throttle alerts, only sending a new one if the last
    was more than 6 hours ago.

    On success, it clears the 'in-alarm' Variable.
    """,
    "tags": ["elasticsearch", "maintenance", "monitoring"],
}


# Helper functions for the throttling logic
def _check_if_throttled() -> bool:
    """
    Check if an alert for a failing cluster should be sent.

    An alert is throttled if an 'in-alarm' variable exists and was set within the
    ALERT_THROTTLE_WINDOW.

    :return: True if the alert should be sent (not throttled), False otherwise.
    """
    last_alert_str = Variable.get(ELASTICSEARCH_HEALTH_IN_ALARM_VAR, default_var=None)

    if not last_alert_str:
        # No variable exists, this is the first failure. Alert is not throttled.
        print("No existing alarm Variable. Alerting.")
        return True

    last_alert_ts = datetime.fromisoformat(last_alert_str)
    time_since_last_alert = datetime.now(timezone.utc) - last_alert_ts

    if time_since_last_alert > ALERT_THROTTLE_WINDOW:
        # It's been long enough, send another alert. Not throttled.
        print(
            f"Last alert was at {last_alert_ts}. Throttling window has passed. "
            "Alerting."
        )
        return True
    else:
        # It's too soon, do not send another alert. Throttled.
        print(f"Last alert was at {last_alert_ts}. Alert is throttled.")
        return False


def _set_alarm_variable():
    """
    Set the 'in-alarm' variable with the current UTC timestamp.

    This is called after a failure alert is sent to begin the throttling window.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    Variable.set(ELASTICSEARCH_HEALTH_IN_ALARM_VAR, now_iso)
    print(f"Set {ELASTICSEARCH_HEALTH_IN_ALARM_VAR} to {now_iso}.")


def _clear_alarm_variable():
    """
    Delete the 'in-alarm' variable.

    This is called when the cluster health check succeeds, resetting the alert mechanism.
    """
    Variable.delete(ELASTICSEARCH_HEALTH_IN_ALARM_VAR)
    print(f"Cleared {ELASTICSEARCH_HEALTH_IN_ALARM_VAR}.")


def create_es_health_check_dag(env: Literal["prod", "staging"]):
    """Create the Elasticsearch health check DAG for a given environment."""

    @dag(dag_id=_DAG_ID.format(env=env), **_SHARED_DAG_ARGS)
    def es_health_check_dag():
        # This is the primary task. It will fail if the ES cluster is unhealthy.
        @task
        def check_es_health():
            hook = ElasticsearchPythonHook(
                elasticsearch_conn_id=f"elasticsearch_http_{env}"
            )
            health = hook.get_conn().cluster.health()
            print(health)
            if health["status"] not in ("green", "yellow"):
                raise AirflowFailException(f"ES cluster status was {health['status']}!")

        # Create an instance of the main health check task.
        health_check = check_es_health()

        # Success path: If the health check succeeds, clear the alarm variable.
        # This task uses the default trigger_rule=TriggerRule.ALL_SUCCESS
        clear_alarm = task(python_callable=_clear_alarm_variable)
        clear_alarm_task = clear_alarm()

        # Failure path: These tasks only run if the health check fails.
        # 1. Check if we should send an alert or if it's throttled.
        check_throttle = ShortCircuitOperator(
            task_id="check_if_throttled",
            python_callable=_check_if_throttled,
            trigger_rule=TriggerRule.ALL_FAILED,  # Only run on failure of upstream
        )

        # 2. Send the actual Slack alert.
        @task
        def notify_failure():
            send_message(
                f"❌ {env.title()} Elasticsearch cluster health check failed.",
                dag_id=_DAG_ID.format(env=env),
            )

        notify_failure_task = notify_failure()

        # 3. Set the alarm variable to start the throttling window.
        set_alarm = task(python_callable=_set_alarm_variable)
        set_alarm_task = set_alarm()

        # Define task dependencies
        health_check >> clear_alarm_task
        health_check >> check_throttle >> notify_failure_task >> set_alarm_task

    return es_health_check_dag()


# Generate the DAG for each environment
for env_name in ("prod", "staging"):
    create_es_health_check_dag(env_name)
