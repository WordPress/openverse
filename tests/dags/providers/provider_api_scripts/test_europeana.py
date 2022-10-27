import json
import os

import pytest
from common.licenses import LicenseInfo, get_license_info
from providers.provider_api_scripts.europeana import (
    EuropeanaDataIngester,
    EuropeanaRecordBuilder,
)


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/europeana"
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)

    return resource_json


FROZEN_DATE = "2018-01-15"


@pytest.fixture
def ingester() -> EuropeanaDataIngester:
    return EuropeanaDataIngester(date=FROZEN_DATE)


@pytest.fixture
def record_builder() -> EuropeanaRecordBuilder:
    return EuropeanaRecordBuilder()


def test_derive_timestamp_pair(ingester):
    # Note that the timestamps are derived as if input was in UTC.
    # The timestamps below depend on the ``FROZEN_DATE`` constant
    # defined above.
    assert ingester.base_request_body["query"] == (
        "timestamp_created:[2018-01-15T00:00:00Z TO 2018-01-16T00:00:00Z]"
    )


def test_get_next_query_params_uses_default_first_pass(ingester):
    assert ingester.get_next_query_params({}) == ingester.base_request_body


def test_get_next_query_params_updates_cursor(ingester):
    prev_query_params = ingester.base_request_body.copy()
    # Set cursor to something, by default it will be empty
    cursor = 243392
    ingester.cursor = cursor

    # test that it will add the cursor when none was previously set
    next_query_params = ingester.get_next_query_params(prev_query_params)
    assert next_query_params == prev_query_params | {"cursor": cursor}

    # next test that it actually also updates any existing cursor
    next_cursor = cursor + 1
    ingester.cursor = next_cursor

    next_query_params_with_updated_cursor = ingester.get_next_query_params(
        next_query_params
    )

    assert next_query_params_with_updated_cursor == next_query_params | {
        "cursor": next_cursor
    }


def test_get_should_continue_updates_cursor(ingester):
    assert ingester.cursor is None

    response_json = {
        "nextCursor": 123533,
        "success": "True",
    }

    assert ingester.get_should_continue(response_json) is True

    assert ingester.cursor == response_json["nextCursor"]


@pytest.mark.parametrize(
    ("response_json"),
    (
        {},
        {"nextCursor": None},
    ),
)
def test_get_should_continue_returns_false(ingester, response_json):
    assert ingester.get_should_continue(response_json) is False


def test_get_batch_data_returns_None_if_success_not_True(ingester):
    response_json = {"success": "False", "items": [1]}
    assert ingester.get_batch_data(response_json) is None


def test_get_batch_data_gets_items_property(ingester):
    response_json = {"success": "True", "items": object()}

    assert ingester.get_batch_data(response_json) is response_json["items"]


def test_get_image_list_with_realistic_response(ingester):
    response_json = _get_resource_json("europeana_example.json")
    record_count = ingester.process_batch(response_json["items"])
    assert record_count == len(response_json["items"])


def test_record_builder_get_record_data(ingester, record_builder):
    image_data = _get_resource_json("image_data_example.json")
    record_data = record_builder.get_record_data(image_data)

    expect_meta_data = {
        "country": ["Spain"],
        "dataProvider": ["Biblioteca Digital de Castilla y León"],
        "description": "Sello en seco: España artística y monumental.",
    }

    assert record_data == {
        "foreign_landing_url": (
            "http://bibliotecadigital.jcyl.es/i18n/consulta/registro.cmd?" "id=26229"
        ),
        "image_url": (
            "http://bibliotecadigital.jcyl.es/i18n/catalogo_imagenes"
            "/imagen_id.cmd?idImagen=102620362"
        ),
        "license_info": (
            LicenseInfo(
                "cc0",
                "1.0",
                "https://creativecommons.org/publicdomain/zero/1.0/",
                "http://creativecommons.org/publicdomain/zero/1.0/",
            )
        ),
        "foreign_identifier": "/2022704/lod_oai_bibliotecadigital_jcyl_es_26229_ent1",
        "title": (
            "Claustro del Monasterio de S. Salvador en Oña [Material gráfico]"
            "= Cloître du Monastère de S. Salvador à Oña"
        ),
        "meta_data": expect_meta_data,
        "source": ingester.providers["image"],
    }


def test_record_builder_get_license_url_with_real_example(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data["rights"] = ["http://creativecommons.org/publicdomain/zero/1.0/"]

    assert record_builder.get_record_data(image_data)[
        "license_info"
    ] == get_license_info("http://creativecommons.org/publicdomain/zero/1.0/")


def test_get_license_url_with_non_cc_license(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data["rights"] = ["http://noncc.org/"]

    assert record_builder.get_record_data(image_data) is None


def test_get_license_url_with_multiple_license(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data["rights"] = [
        "http://noncc.org/",
        "http://creativecommons.org/publicdomain/zero/1.0/",
    ]
    expect_license = get_license_info(
        "http://creativecommons.org/publicdomain/zero/1.0/"
    )
    assert record_builder.get_record_data(image_data)["license_info"] == expect_license


def test_get_foreign_landing_url_with_edmIsShownAt(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    expect_url = "http://bibliotecadigital.jcyl.es/i18n/consulta/registro.cmd?id=26229"

    assert (
        record_builder.get_record_data(image_data)["foreign_landing_url"] == expect_url
    )


def test_get_foreign_landing_url_without_edmIsShownAt(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data.pop("edmIsShownAt", None)
    expect_url = (
        "https://www.europeana.eu/item/2022704/lod_oai_bibliotecadigital_jcyl"
        "_es_26229_ent1?utm_source=api&utm_medium=api&utm_campaign=test_key"
    )

    assert (
        record_builder.get_record_data(image_data)["foreign_landing_url"] == expect_url
    )


def test_get_meta_data_dict(record_builder):
    image_data = _get_resource_json("image_data_example.json")

    expect_meta_data = {
        "country": ["Spain"],
        "dataProvider": ["Biblioteca Digital de Castilla y León"],
        "description": "Sello en seco: España artística y monumental.",
    }

    assert record_builder.get_record_data(image_data)["meta_data"] == expect_meta_data


def test_get_meta_data_dict_without_country(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data.pop("country", None)

    expect_meta_data = {
        "dataProvider": ["Biblioteca Digital de Castilla y León"],
        "description": "Sello en seco: España artística y monumental.",
    }

    assert record_builder.get_record_data(image_data)["meta_data"] == expect_meta_data


@pytest.fixture
def assert_description(record_builder):
    def fn(image_data, expected_description):
        record_data = record_builder.get_record_data(image_data)
        assert record_data["meta_data"]["description"] == expected_description

    return fn


def test_get_description_with_langaware_en(assert_description):
    image_data = _get_resource_json("image_data_example.json")
    image_data["dcDescriptionLangAware"]["en"] = [
        "First English Description",
        "Second English Description",
    ]
    expect_description = "First English Description"

    assert_description(image_data, expect_description)


def test_get_description_with_langaware_def(assert_description):
    image_data = _get_resource_json("image_data_example.json")

    expect_description = "Sello en seco: España artística y monumental."

    assert_description(image_data, expect_description)


def test_get_description_without_langaware(assert_description):
    image_data = _get_resource_json("image_data_example.json")
    image_data.pop("dcDescriptionLangAware", None)
    expect_description = "Sello en seco: España artística y monumental."

    assert_description(image_data, expect_description)


def test_get_description_without_description(assert_description):
    image_data = _get_resource_json("image_data_example.json")
    image_data.pop("dcDescriptionLangAware", None)
    image_data.pop("dcDescription", None)
    expect_description = ""

    assert_description(image_data, expect_description)


def test_get_description_dcDescriptionLangAware_without_en_or_def(assert_description):
    image_data = _get_resource_json("image_data_example.json")
    # Need to give dcDescriptionLangAware _something_ to thwart naive
    # falsy checks
    image_data["dcDescriptionLangAware"] = {"pt": "Não sou uma descrição"}

    expect_description = image_data["dcDescription"][0]
    assert_description(image_data, expect_description)


def test_process_image_data_with_sub_provider(record_builder):
    image_data = _get_resource_json("image_data_sub_provider_example.json")
    record_data = record_builder.get_record_data(image_data)

    expect_meta_data = {
        "country": ["United Kingdom"],
        "dataProvider": ["Wellcome Collection"],
        "description": "Lettering: Greenwich Hospital.",
    }

    assert record_data == {
        "foreign_landing_url": "https://wellcomecollection.org/works/zzwnbyhb",
        "image_url": (
            "https://iiif.wellcomecollection.org/image/V0013398.jpg/full/512,"
            "/0/default.jpg"
        ),
        "license_info": LicenseInfo(
            "by",
            "4.0",
            "https://creativecommons.org/licenses/by/4.0/",
            "http://creativecommons.org/licenses/by/4.0/",
        ),
        "foreign_identifier": "/9200579/zzwnbyhb",
        "title": (
            "Royal Naval Hospital, Greenwich, with ships and rowing boats "
            "in the foreground. Engraving."
        ),
        "meta_data": expect_meta_data,
        "source": "wellcome_collection",
    }


DELETE = object()


@pytest.mark.parametrize(
    ("field_name", "value", "extra_empty_fields"),
    (
        ("id", "", ()),
        ("id", None, ()),
        ("id", DELETE, ()),
        ("edmIsShownAt", "", ("guid",)),
        ("edmIsShownAt", [], ("guid",)),
        ("edmIsShownAt", [""], ("guid",)),
        ("edmIsShownAt", None, ("guid",)),
        ("edmIsShownAt", DELETE, ("guid",)),
        ("rights", [], ()),
        ("rights", [""], ()),
        ("rights", ["not-cc"], ()),
        ("rights", DELETE, ()),
        ("title", "", ()),
        ("title", None, ()),
        ("title", DELETE, ()),
        ("edmIsShownBy", "", ()),
        ("edmIsShownBy", None, ()),
        ("edmIsShownBy", [], ()),
        ("edmIsShownBy", [""], ()),
        ("edmIsShownBy", DELETE, ()),
    ),
)
def test_record_builder_returns_None_if_missing_required_field(
    record_builder, field_name, value, extra_empty_fields
):
    image_data = _get_resource_json("image_data_example.json")
    for empty_field in extra_empty_fields:
        del image_data[empty_field]

    if value is DELETE:
        del image_data[field_name]
    else:
        image_data[field_name] = value

    assert record_builder.get_record_data(image_data) is None
