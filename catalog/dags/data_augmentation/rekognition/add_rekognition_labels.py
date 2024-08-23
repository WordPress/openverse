import json
import logging

import smart_open
from airflow.decorators import task
from airflow.models import Variable
from data_augmentation.rekognition import constants, types
from psycopg2.extras import Json


logger = logging.getLogger(__name__)


@task.branch
def resume_insertion():
    """
    Determine whether to skip table creation and indexing. This is based on the
    presence of the CURRENT_POS_VAR_NAME Variable when starting the DAG. If the
    Variable is present, assume that the DAG is resuming from an existing run,
    otherwise assume a fresh run.
    """
    resume_insertion = Variable.get(constants.CURRENT_POS_VAR_NAME, default_var=None)
    if resume_insertion:
        # Skip table creation and indexing
        return constants.INSERT_LABELS_TASK_ID
    return constants.CREATE_TEMP_TABLE_TASK_ID


def _process_labels(labels: list[types.Label]) -> list[types.MachineGeneratedTag]: ...


def _insert_tags(tags_buffer: types.TagsBuffer): ...


@task(multiple_outputs=True)
def parse_and_insert_labels(
    s3_bucket: str,
    s3_prefix: str,
    in_memory_buffer_size: int,
    file_buffer_size: int,
):
    tags_buffer: types.TagsBuffer = []
    failed_records = []
    total_processed = 0
    known_offset = Variable.get(
        constants.CURRENT_POS_VAR_NAME, default_var=None, deserialize_json=True
    )

    with smart_open.open(f"{s3_bucket}/{s3_prefix}") as file:
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
                _insert_tags(tags_buffer)
                Variable.set(
                    constants.CURRENT_POS_VAR_NAME,
                    value=file.tell(),
                    serialize_json=True,
                )
                tags_buffer.clear()

    return {"total_processed": total_processed, "failed_record": failed_records}
