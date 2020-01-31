from airflow.models import DagBag


def test_dag_loads_with_no_errors(tmpdir):
    tmp_directory = str(tmpdir)
    dag_bag = DagBag(dag_folder=tmp_directory, include_examples=False)
    dag_bag.process_file('wikimedia_workflow.py')
    assert len(dag_bag.import_errors) == 0
    assert len(dag_bag.dags) == 1
