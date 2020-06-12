import unittest.mock as mock
import numbers
from util.popularity.sql import select_percentiles


def test_select_percentiles():
    hook_namespace = 'airflow.hooks.postgres_hook.PostgresHook.get_records'
    with mock.patch(hook_namespace) as get_records:
        get_records.return_value = [[1, 10]]
        percentiles = select_percentiles(
            None, ['global_usage_count', 'views'], 0.85
        )
        assert isinstance(percentiles['global_usage_count'], numbers.Number)
        assert isinstance(percentiles['views'], numbers.Number)
