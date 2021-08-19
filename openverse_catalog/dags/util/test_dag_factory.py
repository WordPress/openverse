import util.dag_factory as df


def test_create_day_partitioned_ingestion_dag_with_single_layer_dependencies():
    dag = df.create_day_partitioned_ingestion_dag(
        'test_dag',
        print,
        [[1, 2]],
    )
    today_id = 'ingest_0'
    wait0_id = 'wait_L0'
    ingest1_id = 'ingest_1'
    ingest2_id = 'ingest_2'
    finish_id = 'test_dag_Finished'
    today_task = dag.get_task(today_id)
    assert today_task.upstream_task_ids == set()
    assert today_task.downstream_task_ids == set([wait0_id, finish_id])
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == set([wait0_id])
    assert ingest1_task.downstream_task_ids == set([finish_id])
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == set([wait0_id])
    assert ingest2_task.downstream_task_ids == set([finish_id])
    finish_task = dag.get_task(finish_id)
    assert finish_task.upstream_task_ids == set(
        [today_id, ingest1_id, ingest2_id]
    )
    assert finish_task.downstream_task_ids == set()


def test_create_day_partitioned_ingestion_dag_with_multi_layer_dependencies():
    dag = df.create_day_partitioned_ingestion_dag(
        'test_dag',
        print,
        [
            [1, 2],
            [3, 4, 5]
        ],
    )
    today_id = 'ingest_0'
    wait0_id = 'wait_L0'
    ingest1_id = 'ingest_1'
    ingest2_id = 'ingest_2'
    wait1_id = 'wait_L1'
    ingest3_id = 'ingest_3'
    ingest4_id = 'ingest_4'
    ingest5_id = 'ingest_5'
    finish_id = 'test_dag_Finished'
    today_task = dag.get_task(today_id)
    assert today_task.upstream_task_ids == set()
    assert today_task.downstream_task_ids == set([wait0_id, finish_id])
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == set([wait0_id])
    assert ingest1_task.downstream_task_ids == set([wait1_id, finish_id])
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == set([wait0_id])
    assert ingest2_task.downstream_task_ids == set([wait1_id, finish_id])
    ingest3_task = dag.get_task(ingest3_id)
    assert ingest3_task.upstream_task_ids == set([wait1_id])
    assert ingest3_task.downstream_task_ids == set([finish_id])
    ingest4_task = dag.get_task(ingest4_id)
    assert ingest4_task.upstream_task_ids == set([wait1_id])
    assert ingest4_task.downstream_task_ids == set([finish_id])
    ingest5_task = dag.get_task(ingest5_id)
    assert ingest5_task.upstream_task_ids == set([wait1_id])
    assert ingest5_task.downstream_task_ids == set([finish_id])
    finish_task = dag.get_task(finish_id)
    assert finish_task.upstream_task_ids == set(
        [today_id, ingest1_id, ingest2_id, ingest3_id, ingest4_id, ingest5_id]
    )
    assert finish_task.downstream_task_ids == set()
