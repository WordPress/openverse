from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


class TargetedRecordsProviderDataIngesterMixin:
    """
    A mixin used with ProviderDataIngesters to create subclasses for ingesting targeted records.

    Records are identified to the `ingest_records` entrypoint by their foreign identifiers.

    This class leverages existing functionality in ProviderDataIngester implementations
    like the batched processing methods. It mimics batched processing by wrapping the
    responses for each retrieved record in a list. In other words, each individual record
    is treated as its own "batch", which would have otherwise corresponded to a single
    page of the regular ingestion workflow for the provider. As such, if the provider returns
    the same data format for individual records as for those records in search, it is not necessary
    to override the data processing methods for individual records that will already be present
    in ProviderDataIngester implementations.

    At request time, URLs and query parameters unique to each foreign identifier should
    be created by implementing overrides to `get_endpoint` and `get_query_params`, each
    of which take the foreign identifier as an argument. For more complex scenarios,
    you may override `get_record` instead for.
    """

    def __init__(self: ProviderDataIngester, conf: dict, *args, **kwargs):
        self.foreign_identifiers = conf["foreign_identifiers"]
        super().__init__(conf, *args, **kwargs)

    def ingest_records(self: ProviderDataIngester) -> None:
        logger.info(f"Begin ingestion of single records for {self.__class__.__name__}")

        for foreign_identifier in self.foreign_identifiers:
            single_record = self.get_record(foreign_identifier)
            self.record_count += self.process_batch([single_record])
            logger.info(f"{self.record_count} records ingested so far.")

            if self.limit and self.record_count >= self.limit:
                logger.info(f"Ingestion limit of {self.limit} has been reached.")
                break

        self._commit_records()

    def get_query_params(self: ProviderDataIngester, foreign_identifier: str) -> dict:
        """Build the query params to request the data for the given foreign identifier"""
        return self.additional_query_params

    def get_endpoint(self: ProviderDataIngester, foreign_identifier: str) -> str:
        """Build the endpoint to request the data for the given foreign identifier"""
        return self.endpoint

    def get_record(self: ProviderDataIngester, foreign_identifier: str) -> dict | None:
        """
        Retrieve an individual record's data from the provider.

        Analogous to `ProviderDataIngester::get_batch`.
        """
        logger.info("Getting single record %s", foreign_identifier)
        endpoint = self.get_endpoint(foreign_identifier)
        query_params = self.get_query_params(foreign_identifier)
        return self.get_response_json(query_params, endpoint)
