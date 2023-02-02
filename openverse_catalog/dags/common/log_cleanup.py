import argparse
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path


logger = logging.getLogger(__name__)

MAX_LOG_AGE_IN_DAYS = 7
ENABLE_DELETE = True


def is_older_than_cutoff(file_or_folder: Path, cutoff: int):
    last_modified = file_or_folder.stat().st_mtime
    cutoff_time = datetime.now() - timedelta(days=cutoff)

    return datetime.fromtimestamp(last_modified) <= cutoff_time


def dir_size_in_mb(dir_paths: list[Path] | Path):
    if not isinstance(dir_paths, list):
        dir_paths = [dir_paths]
    size_in_bytes = sum(
        sum(f.stat().st_size for f in folder.glob("**/*") if f.is_file())
        for folder in dir_paths
    )
    return size_in_bytes / (1024 * 1024)


def get_folders_to_delete(dag_log_folder: Path, max_log_age_in_days: int) -> list[Path]:
    """
    Return a list of log folders that are older `than max_log_age_in_days`.

    The folder structure is as follows:
    `{dag_id}/{task_id}/{timestamp}/{try}.log`
    This function iterates over all `{timestamp}` folders, detects the
    ones that are older than the cutoff, and appends them to the result.
    :param dag_log_folder: Log folder for a DAG
    :param max_log_age_in_days: Logs that are older than this will be returned
    :return: List of old log folders that can be deleted
    """
    task_log_folders = [_ for _ in Path.iterdir(dag_log_folder) if Path.is_dir(_)]
    folders_to_delete = []
    for task_log_folder in task_log_folders:
        run_log_folders_to_delete = [
            folder
            for folder in Path.iterdir(task_log_folder)
            if (
                Path.is_dir(folder)
                and is_older_than_cutoff(folder, max_log_age_in_days)
            )
        ]
        folders_to_delete.extend(run_log_folders_to_delete)
    return folders_to_delete


def delete_folders(folders_to_delete: list[Path]) -> None:
    for dag_log_folder in folders_to_delete:
        logger.info(f"Deleting {dag_log_folder}")
        shutil.rmtree(dag_log_folder)


def get_params(
    log_age: int | str, enable_delete: bool | str, params: dict
) -> tuple[int, bool]:
    if not isinstance(log_age, int):
        log_age_param = params.get("maxLogAgeInDays")
        try:
            log_age = int(log_age_param)
            logger.info(
                f"Maximum log age overwritten with the dag run "
                f"parameter of {log_age_param} days"
            )
        except TypeError:
            log_age = MAX_LOG_AGE_IN_DAYS
    if not isinstance(enable_delete, bool):
        enable_delete_param = params.get("enableDelete", ENABLE_DELETE)
        if isinstance(enable_delete_param, bool):
            enable_delete = enable_delete_param
        else:
            enable_delete = {"true": True, "false": False}.get(
                enable_delete_param.lower(), ENABLE_DELETE
            )

    return log_age, enable_delete


def clean_up(
    base_log_folder: str | Path,
    max_log_age_in_days: int | str,
    should_delete: bool | str,
    **kwargs,
) -> list[Path]:
    """
    Find and delete all log folders that were modified more than `max_log_age_in_days`.

    Deletion only happens if `should_delete` is True, otherwise they are logged
    (e.g. if `should_delete` is False).

    :param base_log_folder: the folder in which dag log folders
    are located.
    :param max_log_age_in_days: Logs older than this number of
    days will be cleaned up. Can be set manually, or be 'None',
    in which case the default value is used.
    :param should_delete: Will delete the old log folders if True, and
    only log the folders that need to be deleted if set to False.
    Can be set manually, or be 'None', in which case the default value
    is used.
    """
    log_base = Path(base_log_folder)

    max_log_age_in_days, should_delete = get_params(
        max_log_age_in_days, should_delete, kwargs.get("params", {})
    )
    logger.info(
        f"Cleaning up log files, using parameters:"
        f"\nBASE_LOG_FOLDER: {base_log_folder}"
        f"\nMAX_LOG_AGE_IN_DAYS: {max_log_age_in_days}"
        f"\nENABLE_DELETE: {should_delete}"
    )
    log_folders = [item for item in Path.iterdir(log_base) if Path.is_dir(item)]
    size_before = dir_size_in_mb(log_base)
    folders_to_delete = []
    for dag_log_folder in log_folders:
        if dag_log_folder.name == "dag_processor_manager":
            continue
        elif dag_log_folder.name == "scheduler":
            # Scheduler creates a folder for each date, and keeps
            # schedule logs for each dag in a separate file
            scheduler_log_folders_to_delete = [
                date_log_dir
                for date_log_dir in Path.iterdir(dag_log_folder)
                if (
                    Path.is_dir(date_log_dir)
                    and not Path.is_symlink(date_log_dir)
                    and is_older_than_cutoff(date_log_dir, max_log_age_in_days)
                )
            ]
            folders_to_delete.extend(scheduler_log_folders_to_delete)
        else:
            task_log_folders_to_delete = get_folders_to_delete(
                dag_log_folder, max_log_age_in_days
            )
            folders_to_delete.extend(task_log_folders_to_delete)
    size_to_delete = dir_size_in_mb(folders_to_delete)
    if should_delete:
        delete_folders(folders_to_delete)
        size_after = dir_size_in_mb(log_base)
        logger.info(
            f"Deleted {size_to_delete:.2f}MB in "
            f"{len(folders_to_delete)} folders\n"
            f"Log directory size before: {size_before:.2f}MB, "
            f"after: {size_after:.2f} MB"
        )
    else:
        logger.info(
            f"Found {len(folders_to_delete)} log folders to delete: "
            f"{[str(folder) for folder in folders_to_delete]}"
            f"\nRun this DAG with ENABLE_DELETE set to True "
            f"to free {size_to_delete:.2f} MB."
        )
    return folders_to_delete


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Cleanup Job", add_help=True)
    parser.add_argument(
        "--maxLogAgeInDays",
        help="Logs older than maxLogAgeInDays days will be deleted. " "Default is 7.",
    )
    parser.add_argument(
        "--enableDelete",
        help="Will only log the folders that need to be deleted if "
        "set to False. Default is True",
    )
    args = parser.parse_args()
    if args.maxLogAgeInDays:
        log_age_in_days_arg = args.maxLogAgeInDays
    else:
        log_age_in_days_arg = 7
    if args.enableDelete:
        enable_delete = args.enableDelete
    else:
        enable_delete = True
    log_folder = Path(__file__).parent / "test_resources" / "logs"
    Path.mkdir(log_folder, parents=True, exist_ok=True)
    clean_up(log_folder, log_age_in_days_arg, enable_delete)
