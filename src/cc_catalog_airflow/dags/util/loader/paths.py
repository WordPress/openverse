from datetime import datetime, timedelta
import logging
import os

FAILURE_SUBDIRECTORY = 'db_loader_failures'
STAGING_SUBDIRECTORY = 'db_loader_staging'

logger = logging.getLogger(__name__)


def stage_oldest_tsv_file(
        output_dir,
        identifier,
        minimum_file_age_minutes
):
    staging_directory = _get_staging_directory(output_dir, identifier)
    tsv_file_name = _get_oldest_tsv_file(output_dir, minimum_file_age_minutes)
    tsv_found = tsv_file_name is not None
    if tsv_found:
        _move_file(tsv_file_name, staging_directory)
    return tsv_found


def delete_old_file(output_dir, identifier):
    tsv_file_name = get_staged_file(output_dir, identifier)
    staging_directory = _get_staging_directory(output_dir, identifier)
    logger.info(f'Deleting {tsv_file_name}')
    os.remove(tsv_file_name)
    logger.info(f'Deleting {staging_directory}')
    os.rmdir(staging_directory)


def move_staged_files_to_failure_directory(
        output_dir,
        identifier
):
    staging_directory = _get_staging_directory(output_dir, identifier)
    failure_directory = _get_failure_directory(output_dir, identifier)
    staged_file_list = _get_full_tsv_paths(staging_directory)
    for file_path in staged_file_list:
        _move_file(file_path, failure_directory)
    logger.info(f'Deleting {staging_directory}')
    os.rmdir(staging_directory)


def get_staged_file(output_dir, identifier):
    staging_directory = _get_staging_directory(output_dir, identifier)
    path_list = _get_full_tsv_paths(staging_directory)
    assert len(path_list) == 1
    return path_list[0]


def _get_staging_directory(
        output_dir,
        identifier,
        staging_subdirectory=STAGING_SUBDIRECTORY,
):
    return os.path.join(output_dir, staging_subdirectory, identifier)


def _get_failure_directory(
        output_dir,
        identifier,
        failure_subdirectory=FAILURE_SUBDIRECTORY,
):
    return os.path.join(output_dir, failure_subdirectory, identifier)


def _get_oldest_tsv_file(
        directory,
        minimum_file_age_minutes
):
    oldest_file_name = None
    logger.info(f'getting files from {directory}')
    path_list = _get_full_tsv_paths(directory)
    logger.info(f'found files:\n{path_list}')
    tsv_last_modified_list = [(p, os.stat(p).st_mtime) for p in path_list]
    logger.info(f'last_modified_list:\n{tsv_last_modified_list}')

    if len(tsv_last_modified_list) == 0:
        return

    oldest_file_modified = min(tsv_last_modified_list, key=lambda t: t[1])
    cutoff_time = datetime.now() - timedelta(minutes=minimum_file_age_minutes)

    if datetime.fromtimestamp(oldest_file_modified[1]) <= cutoff_time:
        oldest_file_name = oldest_file_modified[0]
    else:
        logger.info(
            f'no file found older than {minimum_file_age_minutes} minutes.'
        )

    return oldest_file_name


def _move_file(file_path, new_directory):
    os.makedirs(new_directory, exist_ok=True)
    new_file_path = os.path.join(new_directory, os.path.basename(file_path))
    logger.info(f'Moving {file_path} to {new_file_path}')
    os.rename(file_path, new_file_path)


def _get_full_tsv_paths(directory):
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f[-4:] == '.tsv'
    ]
