from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import NamedTuple

from airflow.exceptions import AirflowSkipException

from common.slack import send_message


logger = logging.getLogger(__name__)


# Shamelessly lifted from:
# https://gist.github.com/borgstrom/936ca741e885a1438c374824efb038b3
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


class RecordMetrics(NamedTuple):
    upserted: int | None
    missing_columns: int | None
    foreign_id_dup: int | None
    url_dup: int | None

    def _add_counts(self, a, b):
        return (a or 0) + (b or 0)

    def __add__(self, other):
        if other is None:
            return self
        return RecordMetrics(
            self._add_counts(self.upserted, other.upserted),
            self._add_counts(self.missing_columns, other.missing_columns),
            self._add_counts(self.foreign_id_dup, other.foreign_id_dup),
            self._add_counts(self.url_dup, other.url_dup),
        )


MediaTypeRecordMetrics = dict[str, RecordMetrics]


def humanize_time_duration(seconds: float | int) -> str:
    if seconds == 0:
        return "inf"
    elif seconds < 1:
        return "less than 1 sec"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f"{amount} {unit}{'' if amount == 1 else 's'}")
    return ", ".join(parts)


def clean_duration(duration: float | list[float] | None) -> str | None:
    # If a list of duration values is provided, get the sum of all non-None values
    if isinstance(duration, list):
        duration = sum(x for x in duration if x)

    # Truncate the duration value if it's provided
    if isinstance(duration, (float, int)):
        duration = humanize_time_duration(duration)

    return duration


def clean_record_counts(
    record_counts_by_media_type: MediaTypeRecordMetrics | list[MediaTypeRecordMetrics],
    media_types: Sequence[str],
) -> MediaTypeRecordMetrics:
    # If a list of record_counts dicts is provided, sum all of the individual values
    if isinstance(record_counts_by_media_type, list):
        return {
            media_type: sum(
                (x[media_type] for x in record_counts_by_media_type),
                RecordMetrics(0, 0, 0, 0),
            )
            for media_type in media_types
        }
    return record_counts_by_media_type


def skip_report_completion(
    duration: str | None,
    record_counts_by_media_type: MediaTypeRecordMetrics,
) -> bool:
    """
    Detect if report_completion should be skipped by determining if there was
    an upstream failure that prevented rows from being ingested; in this case, the
    error will have already been reported to Slack instead.
    """
    return (
        # Duration must be provided and be a value greater than 1 second
        duration is None or duration in ("inf", "less than 1 sec")
    ) and (
        # Record counts by media type must be provided and at least one value must
        # be truthy (i.e. not None). Note that if there was no error during
        # ingestion, and the provider simply ingested 0 records, this
        # condition will not be True.
        not record_counts_by_media_type
        or all([val is None for val in record_counts_by_media_type.values()])
    )


def detect_missing_records(
    dated: bool,
    record_counts_by_media_type: MediaTypeRecordMetrics,
) -> bool:
    """
    Detect when a DAG unexpectedly upserts 0 records, and may require further
    investigation. This is used to detect cases where a DAG may break silently,
    preventing records from being ingested but not causing any Airflow errors.

    Presently, this detects the simple case where a non-dated DAG (which should
    be ingesting _all_ records for its provider) upserts 0 records.
    """
    return not dated and all(
        [
            not count or not count.upserted
            for count in record_counts_by_media_type.values()
        ]
    )


def report_completion(
    dag_id: str,
    media_types: Sequence[str],
    duration: float | str | list[float] | None,
    record_counts_by_media_type: MediaTypeRecordMetrics | list[MediaTypeRecordMetrics],
    dated: bool = False,
    date_range_start: str | None = None,
    date_range_end: str | None = None,
    is_reingestion_workflow: bool = False,
) -> str:
    """
    Send a Slack notification when the load_data task has completed.
    Messages are only sent out in production and if a Slack connection is defined.
    In all cases the data is logged.

    The following data is reported:
        - `duration`: The time the pull data task took to complete. This value is
          "No data" in cases where the pull data task failed.
        - `missing_columns`: The number of records that were removed after the data was
          loaded into a temporary table due to missing data in required columns.
        - `foreign_id_dup`: The number of records that were removed after the data was
          loaded into a temporary table due to multiple records having the same
          provider & foreign ID.
        - `url_dup`: The number of records that have unique provider & foreign IDs,
          but are duplicated across URL. This can occur when a provider makes multiple,
          discrete references to the same source media within their API.
        - `upserted`: The final number of records that made it into the media table
          within the catalog database.
        - `date_range`: The range of time this ingestion covers. If the ingestion covers
          the entire provided dataset, "all" is provided

    If the DAG is a non-dated DAG and yet upserted 0 records, an error is raised.
    """
    is_aggregate_duration = isinstance(duration, list)

    duration = clean_duration(duration)
    record_counts_by_media_type = clean_record_counts(
        record_counts_by_media_type, media_types
    )
    if skip_report_completion(duration, record_counts_by_media_type):
        raise AirflowSkipException(
            "An upstream failure occurred and no rows were loaded"
        )

    # List record count per media type
    media_type_reports = ""
    for media_type, counts in record_counts_by_media_type.items():
        if counts is None or not counts.upserted:
            upserted_human_readable = "_No data_"
        else:
            upserted_human_readable = f"{counts.upserted:,}"
        media_type_reports += f"  - `{media_type}`: {upserted_human_readable}"
        if counts is None or any(count is None for count in counts):
            # Can't make calculation without data
            continue
        extras = []
        if counts.missing_columns:
            extras.append(f"{counts.missing_columns:,} missing columns")
        if counts.foreign_id_dup:
            extras.append(f"{counts.foreign_id_dup:,} duplicate foreign IDs")
        if counts.url_dup:
            extras.append(f"{counts.url_dup:,} duplicate URLs")
        if extras:
            media_type_reports += f" _({', '.join(extras)})_"
        media_type_reports += "\n"

    date_range = "_all_"
    if dated:
        date_range = f"{date_range_start} -> {date_range_end}"
    if is_reingestion_workflow:
        date_range = "_multi-time period spread_"

    # Collect data into a single message
    message = f"""
*DAG*: `{dag_id}`
*Date range*: {date_range}
*Duration of data pull tasks*: {duration or "_No data_"}
*Number of records upserted per media type*:
{media_type_reports}"""

    if is_aggregate_duration:
        # Add disclaimer about duration for aggregate data
        message += (
            "\n_Duration is the sum of the duration for each data pull task."
            " It does not include loading time and does not account for data"
            " pulls that may happen concurrently._"
        )

    # Raise an error to alert maintainers of a possible broken DAG, if non-dated
    # and 0 records were upserted. We raise an error only after building the message,
    # so that duplicate counts/etc are available in the logs.
    if detect_missing_records(dated, record_counts_by_media_type):
        raise ValueError("No records were ingested.")

    send_message(message, dag_id=dag_id, username="Airflow DAG Load Data Complete")
    return message
