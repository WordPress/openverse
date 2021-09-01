import datetime
import time

import pytest
from airflow.models import TaskInstance
from airflow.operators.dummy import DummyOperator
from util.loader import paths


TEST_ID = "testing"

ti = TaskInstance(
    task=DummyOperator(task_id="op_no_dag"),
    execution_date=datetime.datetime(2016, 1, 1),
)


def test_stage_oldest_tsv_file_finds_tsv_file(tmpdir):
    tmp_directory = str(tmpdir)
    identifier = TEST_ID
    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write("")
    tsv_found = paths.stage_oldest_tsv_file(
        tmp_directory,
        identifier,
        0,
        ti,
    )

    assert tsv_found


def test_stage_oldest_tsv_file_stages_tsv_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write("")
    paths.stage_oldest_tsv_file(tmp_directory, identifier, 0, ti)
    staged_path = tmpdir.join(staging_subdirectory, identifier, test_tsv)

    assert staged_path.check(file=1)


def test_stage_oldest_tsv_file_removes_staged_file_from_output_dir(tmpdir):
    tmp_directory = str(tmpdir)
    identifier = TEST_ID
    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write("")
    paths.stage_oldest_tsv_file(tmp_directory, identifier, 0, ti)

    assert path.check(file=0)


def test_stage_oldest_tsv_file_stages_older_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_one_tsv = "test1.tsv"
    test_two_tsv = "test2.tsv"
    path_one = tmpdir.join(test_one_tsv)
    path_one.write("")
    time.sleep(0.01)
    path_two = tmpdir.join(test_two_tsv)
    path_two.write("")
    paths.stage_oldest_tsv_file(tmp_directory, identifier, 0, ti)
    staged_path = tmpdir.join(staging_subdirectory, identifier, test_one_tsv)
    assert staged_path.check(file=1)


def test_stage_oldest_tsv_file_ignores_newer_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_one_tsv = "test1.tsv"
    test_two_tsv = "test2.tsv"
    path_one = tmpdir.join(test_one_tsv)
    path_one.write("")
    time.sleep(0.01)
    path_two = tmpdir.join(test_two_tsv)
    path_two.write("")
    paths.stage_oldest_tsv_file(tmp_directory, identifier, 0, ti)
    staged_path_two = tmpdir.join(staging_subdirectory, identifier, test_two_tsv)
    assert staged_path_two.check(file=0)
    assert path_two.check(file=1)


def test_stage_oldest_tsv_file_ignores_non_tsv(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test = "t"
    path = tmpdir.join(test)
    path.write("")
    paths.stage_oldest_tsv_file(tmp_directory, identifier, 0, ti)
    staged_path = tmpdir.join(staging_subdirectory, identifier, test)
    assert staged_path.check(file=0)
    assert path.check(file=1)


def test_stage_oldest_tsv_file_ignores_young_tsv(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write("")
    paths.stage_oldest_tsv_file(tmp_directory, identifier, 5, ti)
    staged_path = tmpdir.join(staging_subdirectory, identifier, test_tsv)

    assert staged_path.check(file=0)
    assert path.check(file=1)


def test_delete_staged_file_deletes_staged_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = "test.tsv"
    staged_path = tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_tsv)
    staged_path.write("")
    paths.delete_staged_file(tmp_directory, identifier)

    assert staged_path.check(file=0)


def test_delete_staged_file_deletes_all_files_from_staging_dir(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = "test.tsv"
    staged_path = tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_tsv)
    test_non_tsv = "test.tsv.backup"
    staged_non_tsv_path = (
        tmpdir.join(staging_subdirectory).join(identifier).join(test_non_tsv)
    )
    staged_path.write("")
    staged_non_tsv_path.write("")
    paths.delete_staged_file(tmp_directory, identifier)

    assert staged_path.check(file=0)
    assert staged_non_tsv_path.check(file=0)


def test_delete_staged_file_ignores_unidentified_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    nonidentifier = "abcd"
    test_tsv = "test.tsv"
    staged_path = tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_tsv)
    staged_path.write("")
    unidentified_path = (
        tmpdir.join(staging_subdirectory).mkdir(nonidentifier).join(test_tsv)
    )
    unidentified_path.write("")
    paths.delete_staged_file(tmp_directory, identifier)

    assert unidentified_path.check(file=1)


def test_delete_staged_file_ignores_nonstaged_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    other_subdirectory = "abcd"
    identifier = TEST_ID
    test_tsv = "test.tsv"
    staged_path = tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_tsv)
    staged_path.write("")
    nonstaged_path = tmpdir.mkdir(other_subdirectory).mkdir(identifier).join(test_tsv)
    nonstaged_path.write("")
    paths.delete_staged_file(tmp_directory, identifier)

    assert nonstaged_path.check(file=1)


def test_move_staged_files_handles_nonexistent_failure_directory(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    failure_subdirectory = paths.FAILURE_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = "test.tsv"
    staged_path = tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_tsv)
    staged_path.write("")
    failure_path = tmpdir.join(failure_subdirectory).join(identifier).join(test_tsv)
    paths.move_staged_files_to_failure_directory(tmp_directory, identifier)

    assert failure_path.check(file=1)


def test_move_staged_files_handles_existing_failure_directory(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    failure_subdirectory = paths.FAILURE_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = "test.tsv"
    staged_path = tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_tsv)
    staged_path.write("")
    failure_path = tmpdir.mkdir(failure_subdirectory).join(identifier).join(test_tsv)
    paths.move_staged_files_to_failure_directory(tmp_directory, identifier)

    assert failure_path.check(file=1)


def test_move_staged_files_handles_multiple_staged_files(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    failure_subdirectory = paths.FAILURE_SUBDIRECTORY
    identifier = TEST_ID
    test_one_tsv = "test1.tsv"
    test_two_tsv = "test2.tsv"
    staged_path_one = (
        tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_one_tsv)
    )
    staged_path_one.write("")
    staged_path_two = (
        tmpdir.join(staging_subdirectory).join(identifier).join(test_two_tsv)
    )
    staged_path_two.write("")
    failure_path_one = (
        tmpdir.mkdir(failure_subdirectory).join(identifier).join(test_one_tsv)
    )
    failure_path_two = (
        tmpdir.join(failure_subdirectory).join(identifier).join(test_two_tsv)
    )
    paths.move_staged_files_to_failure_directory(tmp_directory, identifier)

    assert failure_path_one.check(file=1)
    assert failure_path_two.check(file=1)


def test_get_staged_file_finds_staged_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = "test.tsv"
    staged_path = tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_tsv)
    staged_path.write("")
    staged_file = paths.get_staged_file(tmp_directory, identifier)

    assert staged_file == str(staged_path)


def test_get_staged_file_throws_error_for_multiple_staged_files(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = paths.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_one_tsv = "test1.tsv"
    test_two_tsv = "test2.tsv"
    staged_path_one = (
        tmpdir.mkdir(staging_subdirectory).mkdir(identifier).join(test_one_tsv)
    )
    staged_path_one.write("")
    staged_path_two = (
        tmpdir.join(staging_subdirectory).join(identifier).join(test_two_tsv)
    )
    staged_path_two.write("")
    with pytest.raises(AssertionError):
        paths.get_staged_file(tmp_directory, identifier)
