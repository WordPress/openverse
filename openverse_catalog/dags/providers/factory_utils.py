import inspect
import logging
import time
from types import FunctionType
from typing import Callable, Sequence

from airflow.models import TaskInstance
from common.constants import MediaType
from common.storage.media import MediaStore


logger = logging.getLogger(__name__)


def _load_provider_script_stores(
    ingestion_callable: Callable,
    media_types: list[MediaType],
    **kwargs,
) -> dict[str, MediaStore]:
    """
    Load the stores associated with a provided ingestion callable. This callable is
    assumed to be a legacy provider script and NOT a provider data ingestion class.
    """
    # Stores exist at the module level, so in order to retrieve the output values we
    # must first pull the stores from the module.
    module = inspect.getmodule(ingestion_callable)
    stores = {}
    for media_type in media_types:
        store = getattr(module, f"{media_type}_store", None)
        if not store:
            continue
        stores[media_type] = store

    if len(stores) != len(media_types):
        raise ValueError(
            f"Expected stores in {module.__name__} were missing: "
            f"{list(set(media_types) - set(stores))}"
        )
    return stores


def generate_tsv_filenames(
    ingestion_callable: Callable,
    media_types: list[MediaType],
    ti: TaskInstance,
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

    # TODO: This entire branch can be removed when all of the provider scripts have been
    # TODO: refactored to subclass ProviderDataIngester.
    if isinstance(ingestion_callable, FunctionType):
        stores = _load_provider_script_stores(ingestion_callable, media_types)

    else:
        # A ProviderDataIngester class was passed instead. First we initialize the
        # class, which will initialize the media stores and DelayedRequester.
        logger.info(
            f"Initializing ProviderIngester {ingestion_callable.__name__} in"
            f"order to generate store filenames."
        )
        ingester = ingestion_callable(*args)
        stores = ingester.media_stores

    # Push the media store output paths to XComs.
    for store in stores.values():
        logger.info(
            f"{store.media_type.capitalize()} store location: {store.output_path}"
        )
        ti.xcom_push(key=f"{store.media_type}_tsv", value=store.output_path)


def pull_media_wrapper(
    ingestion_callable: Callable,
    media_types: list[MediaType],
    tsv_filenames: list[str],
    ti: TaskInstance,
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

    # TODO: This entire branch can be removed when all of the provider scripts have been
    # TODO: refactored to subclass ProviderDataIngester.
    if isinstance(ingestion_callable, FunctionType):
        # Stores exist at the module level, so in order to set the output values we
        # must first pull the stores from the module.
        stores = _load_provider_script_stores(ingestion_callable, media_types)
        run_func = ingestion_callable
    else:
        # A ProviderDataIngester class was passed instead. First we initialize the
        # class, which will initialize the media stores and DelayedRequester.
        logger.info(f"Initializing ProviderIngester {ingestion_callable.__name__}")
        ingester = ingestion_callable(*args)
        stores = ingester.media_stores
        run_func = ingester.ingest_records
        # args have already been passed into the ingester, we don't need them passed
        # in again to the ingest_records function, so we clear the list
        args = []

    for store, tsv_filename in zip(stores.values(), tsv_filenames):
        logger.info(
            f"Setting {store.media_type.capitalize()} store location "
            f"to {tsv_filename}"
        )
        store.output_path = tsv_filename

    logger.info("Beginning ingestion")
    start_time = time.perf_counter()
    # Not passing kwargs here because Airflow throws a bunch of stuff in there that
    # none of our provider scripts are expecting.
    data = run_func(*args)
    end_time = time.perf_counter()
    # Report duration
    duration = end_time - start_time
    ti.xcom_push(key="duration", value=duration)
    return data
