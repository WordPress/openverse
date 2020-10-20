import os
from airflow.models import DagBag

FILE_DIR = os.path.abspath(os.path.dirname(__file__))


def test_dag_loads_with_no_errors(tmpdir):
    tmp_directory = str(tmpdir)
    print(tmp_directory)
    dag_bag = DagBag(dag_folder=tmp_directory, include_examples=False)
    dag_bag.process_file(
        os.path.join(FILE_DIR, 'cleaner_workflow.py')
    )
    print(dag_bag.dags)
    assert len(dag_bag.import_errors) == 0
    assert len(dag_bag.dags) == 1
