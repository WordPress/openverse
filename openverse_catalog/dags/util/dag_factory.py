import logging
from copy import deepcopy
from datetime import datetime, timedelta

import util.config as conf
from airflow import DAG
from airflow.models.baseoperator import cross_downstream
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule


logger = logging.getLogger(__name__)


def get_dated_main_runner_operator(
    main_function,
    execution_timeout,
    day_shift=0,
    task_id="pull_image_data",
):
    args_str = f"{{{{ macros.ds_add(ds, -{day_shift}) }}}}"
    return PythonOperator(
        task_id=task_id,
        python_callable=main_function,
        op_args=[args_str],
        execution_timeout=execution_timeout,
        depends_on_past=False,
    )


def create_provider_api_workflow(
    dag_id,
    main_function,
    default_args=conf.DAG_DEFAULT_ARGS,
    start_date=datetime(1970, 1, 1),
    concurrency=1,
    schedule_string="@daily",
    dated=True,
    day_shift=0,
    dagrun_timeout=timedelta(minutes=30),
):
    """
    This factory method instantiates a DAG that will run the given
    `main_function`.

    Required Arguments:

    dag_id:         string giving a unique id of the DAG to be created.
    main_function:  python function to be run. If the optional argument
                    `dated` is True, then the function must take a
                    single parameter (date) which will be a string of
                    the form 'YYYY-MM-DD'. Otherwise, the function
                    should take no arguments.

    Optional Arguments:

    default_args:     dictionary which is passed to the airflow.dag.DAG
                      __init__ method.
    start_date:       datetime.datetime giving the first valid execution
                      date of the DAG.
    concurrency:      integer that sets the number of tasks which can
                      run simultaneously for this DAG, and the number of
                      dagruns of this DAG which can be run in parallel.
                      It's important to keep the rate limits of the
                      Provider API in mind when setting this parameter.
    schedule_string:  string giving the schedule on which the DAG should
                      be run.  Passed to the airflow.dag.DAG __init__
                      method.
    dated:            boolean giving whether the `main_function` takes a
                      string parameter giving a date (i.e., the date for
                      which data should be ingested).
    day_shift:        integer giving the number of days before the
                      current execution date the `main_function` should
                      be run (if `dated=True`).
    dagrun_timeout:   datetime.timedelta giving the total amount of time
                      a given dagrun may take.
    """
    args = deepcopy(default_args)
    args.update(start_date=start_date)
    print(args)
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=concurrency,
        max_active_runs=concurrency,
        dagrun_timeout=dagrun_timeout,
        start_date=start_date,
        schedule_interval=schedule_string,
        catchup=False,
    )

    with dag:
        if dated:
            get_dated_main_runner_operator(
                main_function, dagrun_timeout, day_shift=day_shift
            )
        else:
            PythonOperator(
                task_id="pull_image_data",
                python_callable=main_function,
                depends_on_past=False,
            )

    return dag


def create_day_partitioned_ingestion_dag(
    dag_id,
    main_function,
    reingestion_day_list_list,
    start_date=datetime(1970, 1, 1),
    concurrency=1,
    default_args=conf.DAG_DEFAULT_ARGS,
    dagrun_timeout=timedelta(hours=23),
    ingestion_task_timeout=timedelta(hours=2),
):
    """
    Given a `main_function` and `reingestion_day_list_list`, this
    factory method instantiates a DAG that will run the given
    `main_function`, parameterized by a number of dates, whose
    calculation is described below.

    Required Arguments:

    dag_id:                     string giving a unique id of the DAG to
                                be created.
    main_function:              python function to be run. The
                                function must take a single parameter
                                (date) which will be a string of the
                                form 'YYYY-MM-DD'.
    reingestion_day_list_list:  list of lists of integers. It gives the
                                set of days before the current execution
                                date of the DAG for which the
                                `main_function` should be run, and
                                describes how the calls to the function
                                should be prioritized.

    Optional Arguments:

    start_date:              datetime.datetime giving the
                             first valid execution_date of the DAG.
    concurrency:             integer that sets the number of tasks which
                             can run simultaneously for this DAG. It's
                             important to keep the rate limits of the
                             Provider API in mind when setting this
                             parameter.
    default_args:            dictionary which is passed to the
                             airflow.dag.DAG __init__ method.
    dagrun_timeout:          datetime.timedelta giving the total amount
                             of time a given dagrun may take.
    ingestion_task_timeout:  datetime.timedelta giving the amount of
                             time a call to the `main_function` is
                             allowed to take.

    Calculation of ingestion dates:

    The `reingestion_day_list_list` should have the form
        [
            [int, ..., int],
            [int, ..., int],
            ...,
            [int, ..., int]
        ]
    It's not necessary for the inner lists to be the same length. The
    DAG instantiated by this factory method will first run the
    `main_function` for the current execution_date, then for the current
    date minus the number of days given by integers in the first list
    (in an arbitrary order, and possibly in parallel if so configured),
    then for the dates calculated from the second list, and so on.  For
    example, given the `reingestion_day_list_list`
        [
            [1, 2, 3],
            [8, 13, 18],
            [28, 38, 48]
        ],
    and assuming the current execution date is 2020-01-01, the
    instantiated dag will run the `main_function` with the parameters
        [
            ['2020-01-01'],
            ['2019-12-31', 2019-12-30', '2019-12-29'],
            ['2019-12-24', 2019-12-19', '2019-12-14'],
            ['2019-12-04', 2019-11-24', '2019-11-14']
        ].
    The order of the inner lists gives the order in which sets of dates
    may be run.  The order within the inner lists is not relevant.  The
    size of the inner lists does *not* set the number of simultaneous
    executions of the `main_function` allowed; that is set by the
    `concurrency` parameter.
    """
    args = deepcopy(default_args)
    args.update(start_date=start_date)
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=concurrency,
        max_active_runs=concurrency,
        dagrun_timeout=dagrun_timeout,
        schedule_interval="@daily",
        start_date=start_date,
        catchup=False,
    )
    with dag:
        ingest_operator_list_list = _build_ingest_operator_list_list(
            reingestion_day_list_list, main_function, ingestion_task_timeout
        )
        for i in range(len(ingest_operator_list_list) - 1):
            wait_operator = DummyOperator(
                task_id=f"wait_L{i}", trigger_rule=TriggerRule.ALL_DONE
            )
            cross_downstream(ingest_operator_list_list[i], [wait_operator])
            wait_operator >> ingest_operator_list_list[i + 1]
        ingest_operator_list_list[-1]

    return dag


def _build_ingest_operator_list_list(
    reingestion_day_list_list, main_function, ingestion_task_timeout
):
    if reingestion_day_list_list[0] != [0]:
        reingestion_day_list_list = [[0]] + reingestion_day_list_list
    return [
        [
            get_dated_main_runner_operator(
                main_function,
                ingestion_task_timeout,
                day_shift=d,
                task_id=f"ingest_{d}",
            )
            for d in L
        ]
        for L in reingestion_day_list_list
    ]
