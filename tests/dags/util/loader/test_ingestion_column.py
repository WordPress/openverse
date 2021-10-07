import logging
from pathlib import Path

from util.loader import ingestion_column as ic


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)
RESOURCES = Path(__file__).parent.resolve() / "test_resources"


def test_check_and_fix_file_adds_column_to_provider_api_tsv(tmpdir):
    old_tsv_file_path = RESOURCES / "old_columns_papis.tsv"
    new_tsv_file_path = RESOURCES / "new_columns_papis.tsv"
    with open(old_tsv_file_path) as f:
        old_tsv_data = f.read()
    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    backup_path = tmpdir.join(test_tsv + ".old")
    path.write(old_tsv_data)
    ic._fix_ingestion_column(path.strpath)
    actual_tsv_data = path.read()
    with open(new_tsv_file_path) as f:
        expect_tsv_data = f.read()
    assert expect_tsv_data == actual_tsv_data
    assert backup_path.read() == old_tsv_data


def test_check_and_fix_file_adds_column_to_common_crawl_tsv(tmpdir):
    old_tsv_file_path = RESOURCES / "old_columns_crawl.tsv"
    new_tsv_file_path = RESOURCES / "new_columns_crawl.tsv"
    with open(old_tsv_file_path) as f:
        old_tsv_data = f.read()
    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    backup_path = tmpdir.join(test_tsv + ".old")
    path.write(old_tsv_data)
    ic._fix_ingestion_column(path.strpath)
    actual_tsv_data = path.read()
    with open(new_tsv_file_path) as f:
        expect_tsv_data = f.read()
    assert expect_tsv_data == actual_tsv_data
    assert backup_path.read() == old_tsv_data


def test_check_and_fix_file_leaves_unchanged_when_enough_columns_tsv(tmpdir):
    tsv_file_path = RESOURCES / "new_columns_papis.tsv"
    with open(tsv_file_path) as f:
        tsv_data = f.read()
    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    backup_path = tmpdir.join(test_tsv + ".old")
    path.write(tsv_data)
    ic._fix_ingestion_column(path.strpath)
    actual_tsv_data = path.read()
    assert tsv_data == actual_tsv_data
    assert not backup_path.check()
