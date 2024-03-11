from dataclasses import dataclass, field
from datetime import timedelta

from airflow.models import Variable

from common.constants import PRODUCTION, STAGING
from common.sensors.constants import ES_CONCURRENCY_TAGS


@dataclass
class CreateNewIndex:
    """
    Configuration object for the create_new_es_index DAG.

    Required Constructor Arguments:

    environment:         str representation of the environment in which to
                         create the new index
    concurrency_tag:     tag used to identify dags with which to prevent
                         concurrency
                         immediately if any of these dags are running.
    reindex_timeout:     timedelta expressing maximum amount of time the
                         reindexing step may take
    requests_per_second: number of requests to send per second during ES
                         reindexing, used to throttle the reindex step
    """

    dag_id: str = field(init=False)
    es_host: str = field(init=False)
    concurrency_tag: str = field(init=False)
    environment: str
    requests_per_second: int | None = None
    reindex_timeout: timedelta = timedelta(hours=12)

    def __post_init__(self):
        self.dag_id = f"create_new_{self.environment}_es_index"
        self.concurrency_tag = ES_CONCURRENCY_TAGS[self.environment]

        if not self.requests_per_second:
            self.requests_per_second = Variable.get(
                "ES_INDEX_THROTTLING_RATE", 20_000, deserialize_json=True
            )


CREATE_NEW_INDEX_CONFIGS = {
    STAGING: CreateNewIndex(
        environment=STAGING,
    ),
    PRODUCTION: CreateNewIndex(
        environment=PRODUCTION,
    ),
}
