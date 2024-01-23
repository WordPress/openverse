"""
# Delete Records DAG

This DAG is used to delete records from the Catalog media tables, after creating a
corresponding record in the associated `deleted_<media_type>` table for each record
to be deleted. It is important to note that records deleted by this DAG will still be
available in the API until the next data refresh runs.

Required Dagrun Configuration parameters:

* table_name:   the name of the table to delete from. Must be a valid media table
* select_query: a SQL `WHERE` clause used to select the rows that will be deleted
* reason:       a string explaining the reason for deleting the records. Ex ('deadlink')


An example dag_run configuration used to delete all records for the "foo" image provider
due to deadlinks would look like this:

```
{
    "table_name": "image",
    "select_query": "WHERE provider='foo'",
    "reason": "deadlink"
}
```

## Multiple deletions

When a record is deleted, it is added to the corresponding Deleted Media table. If the
record is reingested back into the media table, the delete_records DAG may be run
additional times to delete the same record. When this occurs, only one row will be kept
in the Deleted Media table for the record (as uniquely identified by the provider and
foreign identifier pair). This row is not updated, so the `deleted_on` time will reflect
the _first_ time the record was deleted.

When restoring records from the Deleted Media table, it is important to note that these
records have not been updated through reingestion, so fields such as popularity data may
be out of date.

## Warnings

Presently, there is no logic to prevent records that have an entry in a Deleted Media
table from simply being reingested during provider ingestion. Therefore in its current
state, the DAG should _only_ be used to delete records that we can guarantee will not
be reingested (for example, because the provider is archived).

This DAG does not have automated handling for deadlocks, so you must be certain that
records selected for deletion in this DAG are not also being written to by a provider
DAG, for instance. The simplest way to do this is to ensure that any affected provider
DAGs are not currently running.
"""


import logging

from airflow.decorators import dag
from airflow.models.param import Param

from common.constants import AUDIO, DAG_DEFAULT_ARGS, MEDIA_TYPES
from database.delete_records import constants
from database.delete_records.delete_records import (
    create_deleted_records,
    delete_records_from_media_table,
    notify_slack,
)


logger = logging.getLogger(__name__)


@dag(
    dag_id=constants.DAG_ID,
    schedule=None,
    start_date=constants.START_DATE,
    tags=["database"],
    dagrun_timeout=constants.DAGRUN_TIMEOUT,
    doc_md=__doc__,
    default_args={**DAG_DEFAULT_ARGS, "retries": 0},
    render_template_as_native_obj=True,
    params={
        "table_name": Param(
            default=AUDIO,
            enum=MEDIA_TYPES,
            description="The name of the media table from which to select records.",
        ),
        "select_query": Param(
            default="WHERE...",
            type="string",
            description=(
                "The `WHERE` clause of a query that selects all the rows to"
                " be deleted."
            ),
            pattern="^WHERE",
        ),
        "reason": Param(
            default="",
            type="string",
            description="Short descriptor of the reason for deleting the records.",
        ),
    },
)
def delete_records():
    # Create the records in the Deleted Media table
    insert_into_deleted_media_table = create_deleted_records.override(
        task_id="update_deleted_media_table", execution_timeout=constants.CREATE_TIMEOUT
    )(
        select_query="{{ params.select_query }}",
        deleted_reason="{{ params.reason }}",
        media_type="{{ params.table_name }}",
    )

    # If successful, delete the records from the media table
    delete_records = delete_records_from_media_table.override(
        execution_timeout=constants.DELETE_TIMEOUT
    )(table="{{ params.table_name }}", select_query="{{ params.select_query }}")

    notify_complete = notify_slack(
        deleted_records_count=delete_records,
        table_name="{{ params.table_name }}",
        select_query="{{ params.select_query }}",
    )

    insert_into_deleted_media_table >> delete_records >> notify_complete


delete_records()
