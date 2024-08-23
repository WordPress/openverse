import json
import logging

import smart_open
from airflow.decorators import task
from airflow.models import Variable
from psycopg2.extras import Json

from common.sql import PostgresHook
from data_augmentation.rekognition import constants, types
from data_augmentation.rekognition.label_mapping import LABEL_MAPPING


logger = logging.getLogger(__name__)


@task.branch
def resume_insertion():
    """
    Determine whether to skip table creation and indexing. This is based on the
    presence of the CURRENT_POS_VAR_NAME Variable when starting the DAG. If the
    Variable is present, assume that the DAG is resuming from an existing run,
    otherwise assume a fresh run.
    """
    if Variable.get(constants.CURRENT_POS_VAR_NAME, default_var=None):
        # Skip table creation and indexing
        return constants.INSERT_LABELS_TASK_ID
    return constants.CREATE_TEMP_TABLE_TASK_ID


def _process_labels(labels: list[types.Label]) -> list[types.MachineGeneratedTag]:
    tags = []
    for label in labels:
        name = label["Name"]
        # Map name if a correction exists for it
        name = LABEL_MAPPING.get(name, name)
        tags.append(
            {
                "name": name,
                # Confidence values need to be between 0 and 1
                "accuracy": label["Confidence"] / 100,
                "provider": constants.PROVIDER,
            }
        )
    return tags


def _insert_tags(tags_buffer: types.TagsBuffer, postgres_conn_id: str):
    logger.info(f"Inserting {len(tags_buffer)} records into the temporary table")
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=constants.INSERT_TIMEOUT,
    )
    postgres.insert_rows(constants.TEMP_TABLE_NAME, tags_buffer, executemany=True)


@task(multiple_outputs=True)
def parse_and_insert_labels(
    s3_bucket: str,
    s3_prefix: str,
    in_memory_buffer_size: int,
    file_buffer_size: int,
    postgres_conn_id: str,
):
    tags_buffer: types.TagsBuffer = []
    failed_records = []
    total_processed = 0
    known_offset = Variable.get(
        constants.CURRENT_POS_VAR_NAME,
        default_var=None,
        deserialize_json=True,
    )

    with smart_open.open(
        f"{s3_bucket}/{s3_prefix}",
        transport_params={"buffer_size": file_buffer_size},
    ) as file:
        # Navigate to known offset if available
        if known_offset:
            file.seek(known_offset)

        # Begin parsing the file
        for blob in file:
            total_processed += 1
            try:
                labeled_image: types.LabeledImage = json.loads(blob)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON: {blob}")
                # Only track the first 100 failed records, if something
                # is systematically wrong we don't want this getting massive
                if len(failed_records) < 100:
                    failed_records.append(blob)
                continue
            image_id = labeled_image["image_uuid"]
            raw_labels = labeled_image["response"]["Labels"]
            if not raw_labels:
                continue
            tags = _process_labels(raw_labels)
            tags_buffer.append((image_id, Json(tags)))

            if len(tags_buffer) >= in_memory_buffer_size:
                _insert_tags(tags_buffer, postgres_conn_id)
                Variable.set(
                    constants.CURRENT_POS_VAR_NAME,
                    value=file.tell(),
                    serialize_json=True,
                )
                tags_buffer.clear()

        # If there's anything left in the buffer, insert it
        if tags_buffer:
            _insert_tags(tags_buffer, postgres_conn_id)

        # Clear the offset if we've finished processing the file
        Variable.delete(constants.CURRENT_POS_VAR_NAME)

    return {"total_processed": total_processed, "failed_record": failed_records}
