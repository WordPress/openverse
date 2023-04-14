# This line is required so tests behave as expected - Airflow alters the sys.path
# by adding the DAGs, plugins, and config directories. That includes modules we're
# expecting to be available for import during these tests. So in order to keep the
# tests deterministic, we import Airflow explicitly here.
import airflow  # noqa: F401
