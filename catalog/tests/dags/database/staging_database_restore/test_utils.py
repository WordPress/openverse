import pytest
from airflow.providers.amazon.aws.hooks.rds import RdsHook

from database.staging_database_restore import constants, utils


def test_setup_rds_hook():
    @utils.setup_rds_hook
    def test_func(rds_hook: RdsHook = None):
        assert isinstance(rds_hook, RdsHook)

    test_func()


def test_setup_rds_hook_uses_existing():
    shim_hook = object()

    @utils.setup_rds_hook
    def test_func(rds_hook: RdsHook = None):
        assert rds_hook is shim_hook

    test_func(rds_hook=shim_hook)


def test_setup_rds_hook_fails_without_kwargs():
    @utils.setup_rds_hook
    def test_func():
        pass

    with pytest.raises(
        TypeError,
        match="got an unexpected keyword argument 'rds_hook'",
    ):
        test_func()


@pytest.mark.parametrize(
    "db_identifier",
    [
        *sorted(constants.SAFE_TO_MUTATE),
        pytest.param(
            constants.PROD_IDENTIFIER, marks=pytest.mark.raises(exception=ValueError)
        ),
        pytest.param(
            "completely_unacceptable", marks=pytest.mark.raises(exception=ValueError)
        ),
    ],
)
def test_ensure_mutate_allowed(db_identifier):
    utils.ensure_mutate_allowed(db_identifier)
