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


@pytest.mark.parametrize("field", ["name", "description"])
def test_registration_fields_reject_blank(schema, field):
    properties = schema["components"]["schemas"]["OAuth2Registration"]["properties"]
    assert properties[field]["minLength"] == 1


def test_optional_query_params_allow_blank(schema):
    # DRF treats a blank optional query value as omitted, so it must not be documented as invalid
    params = schema["paths"]["/v1/images/"]["get"]["parameters"]
    blank_rejecting = [
        param["name"]
        for param in params
        if param["in"] == "query"
        and not param.get("required")
        and "minLength" in param["schema"]
    ]
    assert blank_rejecting == []
    assert all(
        param["allowEmptyValue"]
        for param in params
        if param["in"] == "query" and not param.get("required")
    )


@pytest.mark.parametrize(
    "path",
    [
        "/v1/images/{identifier}/thumb/",
        "/v1/audio/{identifier}/thumb/",
        "/v1/audio/{identifier}/waveform/",
        "/v1/rate_limit/",
    ],
)
def test_upstream_failures_are_documented(schema, path):
    # Raised when a provider or the cache cannot be reached
    assert "424" in schema["paths"][path]["get"]["responses"]


@pytest.mark.parametrize("media_type", ["images", "audio"])
def test_thumbnail_validation_errors_are_documented(schema, media_type):
    path = f"/v1/{media_type}/{{identifier}}/thumb/"
    assert "400" in schema["paths"][path]["get"]["responses"]
