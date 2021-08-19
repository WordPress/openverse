import json
import logging
import os
import requests
from unittest.mock import patch, MagicMock

from common.licenses.licenses import LicenseInfo
import europeana

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/europeana'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG,
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)

    return resource_json


def test_derive_timestamp_pair():
    # Note that the timestamps are derived as if input was in UTC.
    start_ts, end_ts = europeana._derive_timestamp_pair('2018-01-15')
    assert start_ts == '2018-01-15T00:00:00Z'
    assert end_ts == '2018-01-16T00:00:00Z'


def test_get_image_list_retries_with_none_response():
    with patch.object(
            europeana.delayed_requester,
            'get',
            return_value=None
    ) as mock_get:
        europeana._get_image_list('1234', '5678', 'test_cursor', max_tries=3)

    assert mock_get.call_count == 3


def test_get_image_list_for_last_page():
    response_json = _get_resource_json('europeana_example.json')
    response_json['items'] = []
    response_json.pop('nextCursor', None)

    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)

    with patch.object(
            europeana.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        europeana._get_image_list('1234', '5678', 'test_cursor')

    mock_get.assert_called_once()


def test_get_image_list_retries_with_non_ok_response():
    response_json = _get_resource_json('europeana_example.json')
    r = requests.Response()
    r.status_code = 504
    r.json = MagicMock(return_value=response_json)
    with patch.object(
            europeana.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        europeana._get_image_list('1234', '5678', 'test_cursor', max_tries=3)

    assert mock_get.call_count == 3


def test_get_image_list_with_realistic_response():
    response_json = _get_resource_json('europeana_example.json')
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(
            europeana.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        image_list, next_cursor, total_number_of_images = (
            europeana._get_image_list(
                '1234', '5678', 'test_cursor', max_tries=3)
        )
    expect_image_list = _get_resource_json(
        'europeana_image_list.json')

    assert mock_get.call_count == 1
    assert image_list == expect_image_list


# This test will fail if default constants change.
def test_build_query_param_dict_default():
    start_timestamp = '1234'
    end_timestamp = '5678'
    europeana_api_key = 'test_key'
    resource_type = 'IMAGE'
    reuse_terms = ['open', 'restricted']
    resources_per_request = '100'

    actual_query_param_dict = europeana._build_query_param_dict(
        start_timestamp,
        end_timestamp,
        'test_cursor',
        api_key=europeana_api_key
    )
    expect_query_param_dict = {
        'wskey': europeana_api_key,
        'profile': 'rich',
        'reusability': reuse_terms,
        'sort': ['europeana_id+desc', 'timestamp_created+desc'],
        'rows': resources_per_request,
        'media': 'true',
        'start': 1,
        'qf': [
            f'TYPE:{resource_type}',
            'provider_aggregation_edm_isShownBy:*'],
        'query': f'timestamp_created:[{start_timestamp} TO {end_timestamp}]',
        'cursor': 'test_cursor',

    }
    assert actual_query_param_dict == expect_query_param_dict


def test_extract_image_list_from_json_handles_realistic_input():
    test_dict = _get_resource_json('europeana_example.json')
    expect_image_list = _get_resource_json('europeana_image_list.json')
    expect_next_cursor = "test_next_cursor"
    expect_total_number_of_images = 27
    actual_image_list, actual_next_cursor, actual_total_number_of_images = (
        europeana._extract_image_list_from_json(test_dict)
    )
    assert actual_image_list == expect_image_list
    assert actual_next_cursor == expect_next_cursor
    assert actual_total_number_of_images == expect_total_number_of_images


def test_extract_image_list_from_json_returns_nones_given_non_true_success():
    test_dict = {'success': 'false', 'nextCursor': 'test_next_cursor'}
    assert europeana._extract_image_list_from_json(
        test_dict) == (None, None, None)


def test_extract_image_list_from_json_returns_nones_given_none_json():
    assert europeana._extract_image_list_from_json(None) == (None, None, None)


def test_process_image_data_with_real_example():
    image_data = _get_resource_json('image_data_example.json')
    with patch.object(
            europeana.image_store,
            'add_item',
            return_value=100
    ) as mock_add_item:
        total_images = europeana._process_image_data(image_data)

    expect_meta_data = {
        'country': ["Spain"],
        'dataProvider': ["Biblioteca Digital de Castilla y León"],
        'description': "Sello en seco: España artística y monumental."
    }

    mock_add_item.assert_called_once_with(
        foreign_landing_url=(
            "http://bibliotecadigital.jcyl.es/i18n/consulta/registro.cmd?"
            "id=26229"),
        image_url=(
            "http://bibliotecadigital.jcyl.es/i18n/catalogo_imagenes"
            "/imagen_id.cmd?idImagen=102620362"),
        license_info=(LicenseInfo('cc0', '1.0', 'https://creativecommons.org/publicdomain/zero/1.0/', 'http://creativecommons.org/publicdomain/zero/1.0/')),
        thumbnail_url=(
            "https://api.europeana.eu/api/v2/thumbnail-by-url.json?uri=http"
            "%3A%2F%2Fbibliotecadigital.jcyl.es%2Fi18n%2Fcatalogo_imagenes%2"
            "Fimagen_id.cmd%3FidImagen%3D102620362&type=IMAGE"),
        foreign_identifier=(
            "/2022704/lod_oai_bibliotecadigital_jcyl_es_26229_ent1"),
        title=(
            "Claustro del Monasterio de S. Salvador en Oña [Material gráfico]"
            "= Cloître du Monastère de S. Salvador à Oña"),
        meta_data=expect_meta_data,
        source=europeana.PROVIDER
    )
    assert total_images == 100


def test_get_license_url_with_real_example():
    rights_field = ["http://creativecommons.org/publicdomain/zero/1.0/"]

    assert europeana._get_license_url(
        rights_field) == "http://creativecommons.org/publicdomain/zero/1.0/"


def test_get_license_url_with_non_cc_license():
    rights_field = ["http://noncc.org/"]

    assert europeana._get_license_url(rights_field) is None


def test_get_license_url_with_multiple_license():
    rights_field = ["http://noncc.org/",
                    "http://creativecommons.org/publicdomain/zero/1.0/"]
    expect_license = "http://creativecommons.org/publicdomain/zero/1.0/"
    assert europeana._get_license_url(rights_field) == expect_license


def test_get_foreign_landing_url_with_edmIsShownAt():
    image_data = _get_resource_json('image_data_example.json')
    expect_url = (
        "http://bibliotecadigital.jcyl.es/i18n/consulta/registro.cmd?id=26229")

    assert europeana._get_foreign_landing_url(image_data) == expect_url


def test_get_foreign_landing_url_without_edmIsShownAt():
    image_data = _get_resource_json('image_data_example.json')
    image_data.pop('edmIsShownAt', None)
    expect_url = (
        "https://www.europeana.eu/item/2022704/lod_oai_bibliotecadigital_jcyl"
        "_es_26229_ent1?utm_source=api&utm_medium=api&utm_campaign=test_key")

    assert europeana._get_foreign_landing_url(image_data) == expect_url


def test_create_meta_data_dict():
    image_data = _get_resource_json('image_data_example.json')

    expect_meta_data = {
        'country': ["Spain"],
        'dataProvider': ["Biblioteca Digital de Castilla y León"],
        'description': "Sello en seco: España artística y monumental."
    }

    assert europeana._create_meta_data_dict(image_data) == expect_meta_data


def test_create_meta_data_dict_without_country():
    image_data = _get_resource_json('image_data_example.json')
    image_data.pop('country', None)

    expect_meta_data = {
        'dataProvider': ["Biblioteca Digital de Castilla y León"],
        'description': "Sello en seco: España artística y monumental."
    }

    assert europeana._create_meta_data_dict(image_data) == expect_meta_data


def test_get_description_with_langaware_en():
    image_data = _get_resource_json('image_data_example.json')
    image_data['dcDescriptionLangAware']['en'] = [
        'First English Description', 'Second English Description']
    expect_description = "First English Description"

    assert europeana._get_description(image_data) == expect_description


def test_get_description_with_langaware_def():
    image_data = _get_resource_json('image_data_example.json')

    expect_description = "Sello en seco: España artística y monumental."

    assert europeana._get_description(image_data) == expect_description


def test_get_description_without_langaware():
    image_data = _get_resource_json('image_data_example.json')
    image_data.pop('dcDescriptionLangAware', None)
    expect_description = "Sello en seco: España artística y monumental."

    assert europeana._get_description(image_data) == expect_description


def test_get_description_without_description():
    image_data = _get_resource_json('image_data_example.json')
    image_data.pop('dcDescriptionLangAware', None)
    image_data.pop('dcDescription', None)
    expect_description = ""

    assert europeana._get_description(image_data) == expect_description


def test_process_image_data_with_sub_provider():
    image_data = _get_resource_json('image_data_sub_provider_example.json')
    with patch.object(
            europeana.image_store,
            'add_item',
            return_value=100
    ) as mock_add_item:
        total_images = europeana._process_image_data(image_data)

    expect_meta_data = {
        'country': ["United Kingdom"],
        'dataProvider': ["Wellcome Collection"],
        'description': "Lettering: Greenwich Hospital."
    }

    mock_add_item.assert_called_once_with(
        foreign_landing_url="https://wellcomecollection.org/works/zzwnbyhb",
        image_url=(
            "https://iiif.wellcomecollection.org/image/V0013398.jpg/full/512,"
            "/0/default.jpg"),
        license_info=LicenseInfo(
            'by',
            '4.0',
            "https://creativecommons.org/licenses/by/4.0/",
            "http://creativecommons.org/licenses/by/4.0/"
        ),
        thumbnail_url=(
            "https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%"
            "2Fiiif.wellcomecollection.org%2Fimage%2FV0013398.jpg%2Ffull%2F"
            "500%2C%2F0%2Fdefault.jpg&type=IMAGE"),
        foreign_identifier="/9200579/zzwnbyhb",
        title=(
            "Royal Naval Hospital, Greenwich, with ships and rowing boats "
            "in the foreground. Engraving."),
        meta_data=expect_meta_data,
        source='wellcome_collection'
    )
    assert total_images == 100
