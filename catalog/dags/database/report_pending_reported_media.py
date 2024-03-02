"""
# Report Pending Reported Media DAG
This DAG checks for any user-reported media pending manual review, and alerts
via Slack.

Media may be reported for mature content or copyright infringement, for
example. Once reported, these require manual review through the Django Admin to
determine whether further action (such as deindexing the record) needs to be
taken. If a record has been reported multiple times, it only needs to be
reviewed once and so is only counted once in the reporting by this DAG.
"""

import logging
import os
from textwrap import dedent
from urllib.parse import urljoin

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator, TaskInstance
from airflow.operators.python import PythonOperator

from common import slack
from common.constants import (
    DAG_DEFAULT_ARGS,
    MEDIA_TYPES,
    OPENLEDGER_API_CONN_ID,
    XCOM_PULL_TEMPLATE,
)
from common.sql import PostgresHook


logger = logging.getLogger(__name__)

DAG_ID = "report_pending_reported_media"
ADMIN_URL = os.getenv("DJANGO_ADMIN_URL", "http://localhost:8000/admin")

REPORTS_TABLES = {
    "image": "nsfw_reports",
    "audio": "nsfw_reports_audio",
}

# Column name constants
URL = "identifier"
STATUS = "status"
REASON = "reason"

ReportCountsByReason = dict[str, int]
MediaTypeReportCounts = dict[str, ReportCountsByReason]


def get_pending_report_counts(
    db_conn_id: str, media_type: str, ti: TaskInstance, task: BaseOperator
) -> ReportCountsByReason:
    """
    Build a dict of pending report counts grouped by report reason for a media type.

    Required Arguments:

    db_conn_id: Connection ID for the API database
    media_type: Media type for which to look up reports
    ti:         Running task instance
    """
    postgres = PostgresHook(
        postgres_conn_id=db_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    report_counts_by_reason = {}

    if media_type not in REPORTS_TABLES:
        raise AirflowException(f"{media_type} has no Reports table configured.")

    query = dedent(
        f"""
        SELECT
        COUNT(DISTINCT {URL}), {REASON}
        FROM {REPORTS_TABLES[media_type]}
        WHERE {STATUS}='pending_review'
        GROUP BY {REASON}
        """
    )
    for count, reason in postgres.get_records(query):
        report_counts_by_reason[reason] = count

    logger.info(f"{report_counts_by_reason} records require manual review")

    return report_counts_by_reason


def report_actionable_records(
    report_counts_by_media_type: MediaTypeReportCounts,
) -> None:
    """
    Build a report detailing pending reports for all media types, and alert to Slack.

    Required Arguments:

    report_counts_by_media_type: dict containing report counts per media type, per
                                 report reason
    """
    if all(len(reports) == 0 for reports in report_counts_by_media_type.values()):
        slack.send_message(
            "No records require review at this time :tada:",
            username="Reported Media Check-In",
        )
        return

    media_type_reports = ""
    for media_type, distinct_report_counts in report_counts_by_media_type.items():
        if not distinct_report_counts:
            continue

        admin_review_link = urljoin(
            ADMIN_URL, f"api/{media_type}report/?status__exact=pending_review"
        )
        total_report_count = 0
        counts_by_reason = []

        for reason, count in distinct_report_counts.items():
            total_report_count += count
            counts_by_reason.append(f"{count} {reason}")

        media_type_reports += (
            f"  - *<{admin_review_link}|{media_type}: {total_report_count}>*"
        )
        media_type_reports += f" _({', '.join(counts_by_reason)})_"
        media_type_reports += "\n"

    message = f"""
The following media have been reported and require manual review:
{media_type_reports}
"""

    slack.send_alert(message, dag_id=DAG_ID, username="Reported Media Requires Review")


def create_dag():
    dag = DAG(
        dag_id=DAG_ID,
        default_args=DAG_DEFAULT_ARGS,
        schedule="@weekly",
        catchup=False,
        tags=["database"],
        doc_md=__doc__,
        render_template_as_native_obj=True,
    )

    with dag:
        get_reports_tasks = []
        report_counts_by_media_type = {}

        for media_type in MEDIA_TYPES:
            get_reports = PythonOperator(
                task_id=f"get_pending_{media_type}_reports",
                python_callable=get_pending_report_counts,
                op_kwargs={
                    "db_conn_id": OPENLEDGER_API_CONN_ID,
                    "media_type": media_type,
                },
            )

            report_counts_by_media_type[media_type] = XCOM_PULL_TEMPLATE.format(
                get_reports.task_id, "return_value"
            )
            get_reports_tasks.append(get_reports)

        report_pending_reports = PythonOperator(
            task_id="report_pending_media_reports",
            python_callable=report_actionable_records,
            op_kwargs={"report_counts_by_media_type": report_counts_by_media_type},
        )

        get_reports_tasks >> report_pending_reports

    return dag


globals()[DAG_ID] = create_dag()
