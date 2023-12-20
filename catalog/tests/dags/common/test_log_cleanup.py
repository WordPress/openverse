from datetime import datetime, timedelta
from pathlib import Path

from common import log_cleanup


TEST_LOGS_FOLDER = Path(__file__).parent / "test_resources" / "logs"
# Total number of logs in the `logs_folder` created
INITIAL_LOG_FILE_COUNT = 13
# Number of logs folders in the `test_resources/logs_folder`
# that are older than August 20
OLD_LOG_FOLDER_COUNT = 2
# 1 log file (`dag_process_manager.log`) is not deleted
NON_DELETED_FILE_COUNT = 1
ENABLE_DELETE = False

OLD_TIMESTAMP = datetime.fromisoformat("2021-08-10")
RECENT_TIMESTAMP = datetime.fromisoformat("2021-08-20")

logs_folder = Path(__file__).parent / "test_resources" / "logs"


def is_older_than_cutoff_by_name(file_or_folder: Path, cutoff: int):
    fname = file_or_folder.name
    last_modified_dt = datetime.fromisoformat(fname[:10])
    last_modified = last_modified_dt.timestamp()
    cutoff_time = datetime.now() - timedelta(days=cutoff)
    return datetime.fromtimestamp(last_modified) <= cutoff_time


def calculate_cutoffs():
    NOW = datetime.now()
    one_day_before = OLD_TIMESTAMP - timedelta(days=1)
    one_day_after = OLD_TIMESTAMP + timedelta(days=1)
    delta_before = (NOW - one_day_before).days
    delta_after = (NOW - one_day_after).days
    return delta_before, delta_after


# Normally, the age of log file or folder is detected using the
# system modification date. However, it is difficult to do that
# in CI, so in tests, the log folder name (which is a timestamp)
# is used.
log_cleanup.is_older_than_cutoff = is_older_than_cutoff_by_name
cutoffs_in_days = calculate_cutoffs()


def test_log_cleaner_leaves_new_files():
    """
    If all the log files are newer than the maxLogAgeInDays,
    no log files are deleted
    """
    log_files_count = len(list(Path.glob(logs_folder, "**/*.log")))
    assert log_files_count == INITIAL_LOG_FILE_COUNT

    deleted_folders = log_cleanup.clean_up(
        logs_folder, cutoffs_in_days[0], ENABLE_DELETE
    )
    deleted_count = len(deleted_folders)
    expected_count = 0

    assert deleted_count == expected_count


def test_log_cleaner_deletes_only_old_files():
    """
    Log cleaner deletes all the log files that are older than
    maxLogAgeInDays, but leaves the files that are newer
    """
    deleted_folders = log_cleanup.clean_up(
        logs_folder, cutoffs_in_days[1], ENABLE_DELETE
    )
    deleted_count = len(deleted_folders)

    expected_log_count = OLD_LOG_FOLDER_COUNT

    print(f"Deleted folders: {deleted_folders}\ncutoff: {cutoffs_in_days[1]}")
    assert deleted_count == expected_log_count


def test_log_cleaner_deletes_all_but_one_files_if_max_is_minus_1():
    """If maxLogAgeInDays is set to -1, all log files except for
    `dag_processor_manager.log` are deleted
    Need to find out if the `dag_processor_manager.log` is recreated every day,
    or it just uses single log file for all time.
    """

    deleted_folders = log_cleanup.clean_up(logs_folder, -1, ENABLE_DELETE)
    deleted_folder_count = len(deleted_folders)
    expected_count = 4

    assert deleted_folder_count == expected_count
