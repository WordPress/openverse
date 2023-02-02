import logging
import time
from collections.abc import Sequence
from datetime import datetime

from airflow.models import DagRun, TaskInstance
from airflow.utils.dates import cron_presets
from common.constants import MediaType
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


def generate_tsv_filenames(
    ingester_class: type[ProviderDataIngester],
    media_types: list[MediaType],
    ti: TaskInstance,
    dag_run: DagRun,
    args: Sequence = None,
) -> None:
    """
    Calculate the output directories for each media store to XComs. Output locations
    are pushed under keys with the format `<media-type>_tsv`. This is a temporary
    workaround due to the nature of the current provider scripts. Once
    https://github.com/WordPress/openverse-catalog/issues/229 is addressed and the
    provider scripts are refactored into classes, we can alter the process by which
    MediaStores create/set their output directory so that they are always expected
    to receive it.
    """
    args = args or []
    logger.info("Pushing available store paths to XComs")

    # Initialize the ProviderDataIngester class, which will initialize the
    # DelayedRequester and appropriate media stores.
    logger.info(
        f"Initializing ProviderIngester {ingester_class.__name__} in"
        f"order to generate store filenames."
    )
    ingester = ingester_class(dag_run.conf, dag_run.dag_id, *args)
    stores = ingester.media_stores

    # Push the media store output paths to XComs.
    for store in stores.values():
        logger.info(
            f"{store.media_type.capitalize()} store location: {store.output_path}"
        )
        ti.xcom_push(key=f"{store.media_type}_tsv", value=store.output_path)


def pull_media_wrapper(
    ingester_class: type[ProviderDataIngester],
    media_types: list[MediaType],
    tsv_filenames: list[str],
    ti: TaskInstance,
    dag_run: DagRun,
    args: Sequence = None,
):
    """
    Run the provided callable after pushing setting the output directories
    for each media store using the provided values. This is a temporary workaround
    due to the nature of the current provider scripts. Once
    https://github.com/WordPress/openverse-catalog/issues/229 is addressed and the
    provider scripts are refactored into classes, this wrapper can either be updated
    or the output filename retrieval/setting process can be altered.
    """
    args = args or []
    if len(media_types) != len(tsv_filenames):
        raise ValueError(
            "Provided media types and TSV filenames don't match: "
            f"{media_types=} {tsv_filenames=}"
        )
    logger.info("Setting media stores to the appropriate output filenames")

    # Initialize the ProviderDataIngester class, which will initialize the
    # media stores and DelayedRequester.
    logger.info(f"Initializing ProviderIngester {ingester_class.__name__}")
    ingester = ingester_class(dag_run.conf, dag_run.dag_id, *args)
    stores = ingester.media_stores

    for store, tsv_filename in zip(stores.values(), tsv_filenames):
        logger.info(
            f"Setting {store.media_type.capitalize()} store location "
            f"to {tsv_filename}"
        )
        store.output_path = tsv_filename

    logger.info("Beginning ingestion")
    start_time = time.perf_counter()
    # Not passing args or kwargs here because Airflow throws a bunch of stuff in
    # there that none of our provider scripts are expecting.
    try:
        data = ingester.ingest_records()
    finally:
        end_time = time.perf_counter()
        # Report duration
        duration = end_time - start_time
        ti.xcom_push(key="duration", value=duration)
    return data


def date_partition_for_prefix(
    schedule: str | None,
    logical_date: datetime,
    reingestion_date: datetime,
) -> str:
    """
    Determine the date partitions based on schedule, logical date, and reingestion date.

    This partition will be used as part of the S3 key prefix for a given TSV.

    Prefix mapping (schedule interval to partition):
        - Hourly -> `year=YYYY/month=MM/day=DD`
        - Daily -> `year=YYYY/month=MM`
        - None/yearly/monthly/weekly/other -> `year=YYYY`

    If a reingestion_date is supplied, it is further partitioned by the reingestion
    date itself to avoid filename collisions.

    Example:
        - Hourly -> `year=YYYY/month=MM/day=DD/reingestion=YYYY-MM-DD`
        - Daily -> `year=YYYY/month=MM/reingestion=YYYY-MM-DD`
        - None/yearly/monthly/weekly/other -> `year=YYYY/reingestion=YYYY-MM-DD`
    """
    hourly_airflow = "@hourly"
    hourly_cron = cron_presets[hourly_airflow]
    daily_airflow = "@daily"
    daily_cron = cron_presets[daily_airflow]

    # Always partition by year
    prefix = f"year={logical_date.year}"

    # Add month in daily/hourly cases
    if schedule in {hourly_airflow, hourly_cron, daily_airflow, daily_cron}:
        prefix += f"/month={logical_date.month:02}"

    # Add day to hourly cases
    if schedule in {hourly_airflow, hourly_cron}:
        prefix += f"/day={logical_date.day:02}"

    # Further partition by reingestion date if supplied
    if reingestion_date is not None:
        prefix += f"/reingestion={reingestion_date}"

    return prefix
