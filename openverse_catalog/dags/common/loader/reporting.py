from __future__ import annotations

import logging
from typing import NamedTuple, Optional

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
    upserted: Optional[int]
    missing_columns: Optional[int]
    foreign_id_dup: Optional[int]
    url_dup: Optional[int]


MediaTypeRecordMetrics = dict[str, RecordMetrics]


def humanize_time_duration(seconds: float) -> str:
    if seconds == 0:
        return "inf"
    elif seconds < 1:
        return "less than 1 sec"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


def report_completion(
    provider_name: str,
    duration: float | str | None,
    record_counts_by_media_type: MediaTypeRecordMetrics,
    dated: bool = False,
    date_range_start: str | None = None,
    date_range_end: str | None = None,
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
    """
    # Truncate the duration value if it's provided
    if isinstance(duration, float):
        duration = humanize_time_duration(duration)

    # List record count per media type
    media_type_reports = ""
    for media_type, counts in record_counts_by_media_type.items():
        if counts is None or not counts.upserted:
            upserted_human_readable = "_No data_"
        else:
            upserted_human_readable = f"{counts.upserted:,}"
        media_type_reports += f"  - `{media_type}`: {upserted_human_readable}"
        if counts is None or any([count is None for count in counts]):
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

    # Collect data into a single message
    message = f"""
*Provider*: `{provider_name}`
*Date range*: {date_range}
*Duration of data pull task*: {duration or '_No data_'}
*Number of records upserted per media type*:
{media_type_reports}"""
    send_message(message, username="Airflow DAG Load Data Complete")
    logger.info(message)
    return message
