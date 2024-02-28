from unittest.mock import patch

import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.europeana import (
    EmptyRequiredFieldException,
    EuropeanaDataIngester,
    EuropeanaRecordBuilder,
)


_get_resource_json = make_resource_json_func("europeana")


FROZEN_DATE = "2018-01-15"

CC0_1_0 = get_license_info("http://creativecommons.org/publicdomain/zero/1.0/")


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
        "timestamp_update:[2018-01-15T00:00:00Z TO 2018-01-16T00:00:00Z]"
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
    response_json = {"success": False, "items": [1]}
    assert ingester.get_batch_data(response_json) is None


def test_get_batch_data_gets_items_property(ingester):
    response_json = {"success": "True", "items": object()}

    assert ingester.get_batch_data(response_json) is response_json["items"]


def test_get_image_list_with_realistic_response(ingester):
    image_store = ImageStore(provider=prov.EUROPEANA_DEFAULT_PROVIDER)
    ingester.media_stores = {"image": image_store}
    batch_json = _get_resource_json("europeana_example.json")
    object_json = {}
    with patch.object(
        ingester, "_get_additional_item_data", return_value=object_json
    ) as item_call:
        with patch.object(image_store, "add_item"):
            record_count = ingester.process_batch(batch_json["items"])
            assert item_call.call_count == len(batch_json["items"])
            assert record_count == len(batch_json["items"])


ITEM_HAPPY_RESPONSE = _get_resource_json("item_full.json")
ITEM_NOT_1ST_RESPONSE = _get_resource_json("item_not_first_webresource.json")
ITEM_HAPPY_WEBRESOURCE = (
    ITEM_HAPPY_RESPONSE.get("object").get("aggregations")[0].get("webResources")[0]
)
ITEM_NOT_1ST_WEBRESOURCE = (
    ITEM_NOT_1ST_RESPONSE.get("object").get("aggregations")[0].get("webResources")[1]
)


@pytest.mark.parametrize(
    "response_json, url, expected",
    [
        pytest.param(
            ITEM_HAPPY_RESPONSE, "happy_url", ITEM_HAPPY_WEBRESOURCE, id="happy_path"
        ),
        pytest.param(
            ITEM_NOT_1ST_RESPONSE, "happy_url", ITEM_NOT_1ST_WEBRESOURCE, id="not_first"
        ),
        pytest.param(
            {"success": False, "object": {}}, "happy_url", {}, id="success_is_false"
        ),
        pytest.param(
            {"success": True, "no": "object"}, "happy_url", {}, id="no_object"
        ),
        pytest.param(
            {"success": True, "object": {}}, "happy_url", {}, id="no_aggregation"
        ),
        pytest.param(None, "happy_url", {}, id="no_response"),
        pytest.param(ITEM_HAPPY_RESPONSE, "sad_url", {}, id="wrong_url"),
    ],
)
def test_get_additional_item_data(response_json, url, expected, ingester):
    with patch.object(
        ingester, "get_response_json", return_value=response_json
    ) as patch_api_call:
        with patch.object(ingester, "_get_id_and_url", return_value=("/FAKE_ID", url)):
            actual = ingester._get_additional_item_data({})
            assert actual == expected
    patch_api_call.assert_called_once_with(
        endpoint="https://api.europeana.eu/record/v2/FAKE_ID.json",
        query_params=ingester.item_params,
    )


def test_get_additional_item_data_no_foreign_id(ingester):
    with patch.object(ingester, "get_response_json", return_value={}) as patch_call:
        actual = ingester._get_additional_item_data({"info": "but not an ID"})
        expected = {}
        assert actual == expected
    patch_call.assert_not_called


def test_record_builder_get_record_data(ingester, record_builder):
    image_data = _get_resource_json("image_data_example.json") | {
        "item_webresource": _get_resource_json("item_full.json")
        .get("object")
        .get("aggregations")[0]
        .get("webResources")[0]
    }
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
        "url": (
            "http://bibliotecadigital.jcyl.es/i18n/catalogo_imagenes"
            "/imagen_id.cmd?idImagen=102620362"
        ),
        "license_info": CC0_1_0,
        "foreign_identifier": "/2022704/lod_oai_bibliotecadigital_jcyl_es_26229_ent1",
        "title": (
            "Claustro del Monasterio de S. Salvador en Oña [Material gráfico]"
            "= Cloître du Monastère de S. Salvador à Oña"
        ),
        "meta_data": expect_meta_data,
        "source": ingester.providers["image"],
        "height": 480,
        "width": 381,
        "filesize": 36272,
        "filetype": "jpeg",
    }


def test_record_builder_get_license_info_with_real_example(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data["rights"] = ["http://creativecommons.org/publicdomain/zero/1.0/"]

    assert record_builder.get_record_data(image_data)["license_info"] == CC0_1_0


def test_get_license_url_with_non_cc_license(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data["rights"] = ["http://noncc.org/"]

    assert record_builder.get_record_data(image_data) is None


def test_get_license_info_with_multiple_license(record_builder):
    image_data = _get_resource_json("image_data_example.json")
    image_data["rights"] = [
        "http://noncc.org/",
        "http://creativecommons.org/publicdomain/zero/1.0/",
    ]
    expect_license = CC0_1_0
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


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"edmIsShownBy": None},
        {"edmIsShownBy": ["dropbox.com/value"]},
    ],
)
def test_get_image_url_empty(data, record_builder):
    with pytest.raises(EmptyRequiredFieldException):
        assert record_builder._get_image_url(data)


@pytest.mark.parametrize(
    "item_data, expected",
    [
        pytest.param(
            ITEM_HAPPY_WEBRESOURCE, {"width": 381, "height": 480}, id="happy_path"
        ),
        pytest.param({"no": "dimensions"}, {}, id="no_dimensions"),
        pytest.param({"ebucoreWidth": 381}, {}, id="no_height"),
        pytest.param({"ebucoreHeight": 480}, {}, id="no_width"),
    ],
)
def test_get_image_dimensions(item_data, expected, record_builder):
    assert record_builder._get_image_dimensions(item_data) == expected


@pytest.mark.parametrize(
    "item_data, expected",
    [
        pytest.param(ITEM_HAPPY_WEBRESOURCE, "jpeg", id="happy_path"),
        pytest.param({"ebucoreHasMimeType": "image-jpeg"}, "image-jpeg", id="no_slash"),
        pytest.param({"ebucoreHasMimeType": "gibberish"}, "gibberish", id="gibberish"),
        pytest.param({"ebucoreHasMimeType": None}, None, id="no_filetype"),
    ],
)
def test_get_filetype(item_data, expected, record_builder):
    assert record_builder._get_filetype(item_data) == expected


@pytest.mark.parametrize(
    "item_data, expected",
    [
        pytest.param(ITEM_HAPPY_WEBRESOURCE, 36272, id="happy_path"),
        pytest.param({"ebucoreFileByteSize": "gibberish"}, "gibberish", id="gibberish"),
        pytest.param({"no": "filesize"}, None, id="no_filesize"),
    ],
)
def test_get_filesize(item_data, expected, record_builder):
    assert record_builder._get_filesize(item_data) == expected


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
        "url": (
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
