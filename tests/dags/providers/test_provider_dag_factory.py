from providers import provider_dag_factory


def test_create_day_partitioned_ingestion_dag_with_single_layer_dependencies():
    dag = provider_dag_factory.create_day_partitioned_ingestion_dag(
        "test_dag",
        print,
        [[1, 2]],
    )
    today_id = "ingest_0"
    wait0_id = "wait_L0"
    ingest1_id = "ingest_1"
    ingest2_id = "ingest_2"
    today_task = dag.get_task(today_id)
    assert today_task.upstream_task_ids == set()
    assert today_task.downstream_task_ids == {wait0_id}
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == {wait0_id}
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == {wait0_id}


def test_create_day_partitioned_ingestion_dag_with_multi_layer_dependencies():
    dag = provider_dag_factory.create_day_partitioned_ingestion_dag(
        "test_dag",
        print,
        [[1, 2], [3, 4, 5]],
    )
    today_id = "ingest_0"
    wait0_id = "wait_L0"
    ingest1_id = "ingest_1"
    ingest2_id = "ingest_2"
    wait1_id = "wait_L1"
    ingest3_id = "ingest_3"
    ingest4_id = "ingest_4"
    ingest5_id = "ingest_5"
    today_task = dag.get_task(today_id)
    assert today_task.upstream_task_ids == set()
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == {wait0_id}
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == {wait0_id}
    ingest3_task = dag.get_task(ingest3_id)
    assert ingest3_task.upstream_task_ids == {wait1_id}
    ingest4_task = dag.get_task(ingest4_id)
    assert ingest4_task.upstream_task_ids == {wait1_id}
    ingest5_task = dag.get_task(ingest5_id)
    assert ingest5_task.upstream_task_ids == {wait1_id}
