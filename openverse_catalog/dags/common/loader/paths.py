import logging
import os
import re
from datetime import datetime, timedelta
from typing import Optional

from airflow.models import TaskInstance
from common.loader.ingestion_column import _fix_ingestion_column


FAILURE_SUBDIRECTORY = "db_loader_failures"
STAGING_SUBDIRECTORY = "db_loader_staging"
SUPPORTED_MEDIA_TYPES = {"audio", "image"}
LEGACY_TSV_VERSION = "000"

logger = logging.getLogger(__name__)


def stage_oldest_tsv_file(
    output_dir: str,
    identifier: str,
    minimum_file_age_minutes: int,
    ti: TaskInstance,
) -> bool:
    """
    Selects the oldest tsv file from the output directory.
    If the file hasn't changed in `minimum_file_age_minutes`,
    moves the file to `staging_directory`, and sends an Airflow
    xcom message with file media_type extracted from the filename.
    :param output_dir: Directory where temporary tsv files are
    stored.
    :param identifier: File identifier, usually timestamp with
    the time when ingestion for provider started.
    :param minimum_file_age_minutes: If the file has not been
    updated in this time, it is safe to assume that ingestion
    has finished, and we can save the data to the database.
    :param ti: Airflow Task Instance, used to sent the media_type to
    downstream tasks
    :return: True if tsv file was staged, false otherwise
    """
    staging_directory = _get_staging_directory(output_dir, identifier)
    tsv_file_name = _get_oldest_tsv_file(output_dir, minimum_file_age_minutes)
    tsv_found = tsv_file_name is not None
    if tsv_found:
        tsv_version = _get_tsv_version(tsv_file_name)
        should_fix_ingestion_type = False
        if tsv_version == LEGACY_TSV_VERSION:
            should_fix_ingestion_type = True
            logger.info(f"Will move and fix ingestion type: {tsv_version}")
        _move_file(tsv_file_name, staging_directory, should_fix_ingestion_type)
        media_type = _extract_media_type(tsv_file_name)
        ti.xcom_push(key="media_type", value=media_type)
        ti.xcom_push(key="tsv_version", value=tsv_version)
    return tsv_found


def delete_staged_file(output_dir: str, identifier: str) -> None:
    staging_directory = _get_staging_directory(output_dir, identifier)
    staging_directory_files = os.listdir(staging_directory)
    logger.debug(f"Files in staging directory: {staging_directory_files}")
    for file_name in staging_directory_files:
        file_path = os.path.join(staging_directory, file_name)
        logger.info(f"Deleting {file_path}")
        os.remove(file_path)
    logger.info(f"Deleting {staging_directory}")
    os.rmdir(staging_directory)


def move_staged_files_to_failure_directory(output_dir: str, identifier: str) -> None:
    staging_directory = _get_staging_directory(output_dir, identifier)
    failure_directory = _get_failure_directory(output_dir, identifier)
    staged_file_list = _get_full_tsv_paths(staging_directory)
    for file_path in staged_file_list:
        _move_file(file_path, failure_directory)
    logger.info(f"Deleting {staging_directory}")
    os.rmdir(staging_directory)


def get_staged_file(
    output_dir: str,
    identifier: str,
) -> str:
    staging_directory = _get_staging_directory(output_dir, identifier)
    path_list = _get_full_tsv_paths(staging_directory)
    assert len(path_list) == 1
    return path_list[0]


def _get_staging_directory(
    output_dir: str,
    identifier: str,
    staging_subdirectory: Optional[str] = STAGING_SUBDIRECTORY,
):
    return os.path.join(output_dir, staging_subdirectory, identifier)


def _get_failure_directory(
    output_dir: str,
    identifier: str,
    failure_subdirectory: Optional[str] = FAILURE_SUBDIRECTORY,
):
    return os.path.join(output_dir, failure_subdirectory, identifier)


def _get_oldest_tsv_file(
    directory: str, minimum_file_age_minutes: int
) -> Optional[str]:
    oldest_file_name = None
    logger.info(f"getting files from {directory}")
    path_list = _get_full_tsv_paths(directory)
    logger.info(f"found files:\n{path_list}")
    tsv_last_modified_list = [(p, os.stat(p).st_mtime) for p in path_list]
    logger.info(f"last_modified_list:\n{tsv_last_modified_list}")

    if len(tsv_last_modified_list) == 0:
        return

    oldest_file_modified = min(tsv_last_modified_list, key=lambda t: t[1])
    cutoff_time = datetime.now() - timedelta(minutes=minimum_file_age_minutes)

    if datetime.fromtimestamp(oldest_file_modified[1]) <= cutoff_time:
        oldest_file_name = oldest_file_modified[0]
    else:
        logger.info(f"no file found older than {minimum_file_age_minutes} minutes.")

    return oldest_file_name


def _move_file(file_path, new_directory, should_fix_ingestion_type=False):
    os.makedirs(new_directory, exist_ok=True)
    new_file_path = os.path.join(new_directory, os.path.basename(file_path))
    logger.info(f"Moving {file_path} to {new_file_path}")
    os.rename(file_path, new_file_path)
    if should_fix_ingestion_type:
        _fix_ingestion_column(new_file_path)


def _get_full_tsv_paths(directory):
    return [
        os.path.join(directory, f) for f in os.listdir(directory) if f[-4:] == ".tsv"
    ]


def _extract_media_type(tsv_file_name: Optional[str]) -> str:
    """
    By default, the filename will be:
    `folder/provider_timestamp.tsv` for older version
    `folder/provider_<media_type>_timestamp.tsv` for newer version
    If we cannot extract `media_type`, we return `image`.
    :param tsv_file_name:
    :return: media type of the staged file, one of
    SUPPORTED_MEDIA_TYPES
    """
    try:
        media_type = tsv_file_name.split("/")[-1].split("_")[1]
        if media_type not in SUPPORTED_MEDIA_TYPES:
            media_type = "image"
    # None or no underscores
    except (AttributeError, IndexError):
        media_type = "image"
    return media_type


def _get_tsv_version(tsv_file_name: str) -> str:
    """TSV file version can be deducted from the filename
    v0: without _vN_ in the filename
    v1+: has a _vN in the filename

    >>>_get_tsv_version('/behance_image_20210906130355.tsv')
    '000'
    >>> _get_tsv_version('/jamendo_audio_v005_20210906130355.tsv')
    '005'
    """

    version_pattern = re.compile(r"_v(\d+)_")
    if match := re.search(version_pattern, tsv_file_name):
        return match.group(1)
    return "000"
