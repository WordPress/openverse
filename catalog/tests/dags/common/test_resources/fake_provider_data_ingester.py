"""
This is a fake provider module used in test_dag_factory.
It is used to check that the output path acquisition logic is correct.
"""

from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


class FakeDataIngester(ProviderDataIngester):
    @property
    def providers(self) -> dict[str, str]:
        return {"image": "fake_image", "audio": "fake_audio"}

    @property
    def endpoint(self):
        return ""

    def get_next_query_params(self, old_query_params: dict | None) -> dict:
        return old_query_params

    def get_batch_data(self, response_json):
        return None

    def get_media_type(self, record: dict) -> str:
        return ""

    def get_record_data(self, data: dict) -> dict | list[dict]:
        return {}
