from dataclasses import dataclass

from providers.provider_api_scripts.flickr import FlickrDataIngester
from providers.provider_workflows import ProviderWorkflow


@dataclass
class ProviderTargetedIngestionWorkflow(ProviderWorkflow):
    """
    Provider targeted ingestion workflow configurations.

    Extends the ProviderWorkflow with configuration options used to set up
    a targeted ingestion workflow DAG.
    """

    max_foreign_identifiers: int = 0
    """
    The maximum foreign identifiers to allow for a single run of the DAG.

    This should limit the DAG run to less than the setting for ``pull_timeout``.
    """

    schedule_string: None = None
    """
    Targeted reingestion cannot happen on a schedule and must be triggered
    by another process.
    """

    def __post_init__(self):
        if not self.dag_id:
            _, provider_name = self._get_module_info()
            self.dag_id = f"{provider_name}_targeted_ingestion_workflow"

        super().__post_init__()


PROVIDER_TARGETED_INGESTION_WORKFLOWS = [
    ProviderTargetedIngestionWorkflow(
        ingester_class=FlickrDataIngester,
        max_foreign_identifiers=2000,
    ),
]
