import pytest


@pytest.fixture
def schema(api_client):
    return api_client.get("/v1/schema/", {"format": "json"}).json()


@pytest.mark.parametrize("media_type", ["images", "audio"])
def test_report_body_omits_path_identifier(schema, media_type):
    body = schema["paths"][f"/v1/{media_type}/{{identifier}}/report/"]["post"][
        "requestBody"
    ]
    for content in body["content"].values():
        ref = content["schema"]["$ref"].rsplit("/", 1)[-1]
        assert "identifier" not in schema["components"]["schemas"][ref]["properties"]
