import logging
import requests

import pytest
import tldextract

from common.storage import image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

# This avoids needing the internet for testing.
image.licenses.urls.tldextract.extract = tldextract.TLDExtract(
    suffix_list_urls=None
)
image.columns.urls.tldextract.extract = tldextract.TLDExtract(
    suffix_list_urls=None
)


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv('OUTPUT_DIR', '/tmp')


@pytest.fixture
def mock_rewriter(monkeypatch):
    def mock_rewrite_redirected_url(url_string):
        return url_string
    monkeypatch.setattr(
        image.licenses.urls,
        'rewrite_redirected_url',
        mock_rewrite_redirected_url,
    )


@pytest.fixture
def get_good(monkeypatch):
    def mock_get(url, timeout=60):
        return requests.Response()
    monkeypatch.setattr(image.licenses.urls.requests, 'get', mock_get)


def test_ImageStore_uses_OUTPUT_DIR_variable(
        monkeypatch,
):
    testing_output_dir = '/my_output_dir'
    monkeypatch.setenv('OUTPUT_DIR', testing_output_dir)
    image_store = image.ImageStore()
    assert testing_output_dir in image_store._OUTPUT_PATH


def test_ImageStore_falls_back_to_tmp_output_dir_variable(
        monkeypatch,
        setup_env,
):
    monkeypatch.delenv('OUTPUT_DIR')
    image_store = image.ImageStore()
    assert '/tmp' in image_store._OUTPUT_PATH


def test_ImageStore_includes_provider_in_output_file_string(
        setup_env,
):
    image_store = image.ImageStore('test_provider')
    assert type(image_store._OUTPUT_PATH) == str
    assert 'test_provider' in image_store._OUTPUT_PATH


def test_ImageStore_add_item_adds_realistic_image_to_buffer(
        setup_env, mock_rewriter
):
    license_url = 'https://creativecommons.org/publicdomain/zero/1.0/'
    image_store = image.ImageStore(provider='testing_provider')
    image_store.add_item(
        foreign_landing_url='https://images.org/image01',
        image_url='https://images.org/image01.jpg',
        license_url=license_url,
    )
    assert len(image_store._image_buffer) == 1


def test_ImageStore_add_item_adds_multiple_images_to_buffer(
        mock_rewriter, setup_env,
):
    image_store = image.ImageStore(provider='testing_provider')
    image_store.add_item(
        foreign_landing_url='https://images.org/image01',
        image_url='https://images.org/image01.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image02',
        image_url='https://images.org/image02.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image03',
        image_url='https://images.org/image03.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image04',
        image_url='https://images.org/image04.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    assert len(image_store._image_buffer) == 4


def test_ImageStore_add_item_flushes_buffer(
        mock_rewriter, setup_env, tmpdir,
):
    output_file = 'testing.tsv'
    tmp_directory = tmpdir
    output_dir = str(tmp_directory)
    tmp_file = tmp_directory.join(output_file)
    tmp_path_full = str(tmp_file)

    image_store = image.ImageStore(
        provider='testing_provider',
        output_file=output_file,
        output_dir=output_dir,
        buffer_length=3
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image01',
        image_url='https://images.org/image01.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image02',
        image_url='https://images.org/image02.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image03',
        image_url='https://images.org/image03.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image04',
        image_url='https://images.org/image04.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    assert len(image_store._image_buffer) == 1
    with open(tmp_path_full) as f:
        lines = f.read().split('\n')
    assert len(lines) == 4  # recall the last '\n' will create an empty line.


def test_ImageStore_commit_writes_nothing_if_no_lines_in_buffer():
    image_store = image.ImageStore(output_dir='/path/does/not/exist')
    image_store.commit()


def test_ImageStore_produces_correct_total_images(mock_rewriter, setup_env):
    image_store = image.ImageStore(provider='testing_provider')
    image_store.add_item(
        foreign_landing_url='https://images.org/image01',
        image_url='https://images.org/image01.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image02',
        image_url='https://images.org/image02.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    image_store.add_item(
        foreign_landing_url='https://images.org/image03',
        image_url='https://images.org/image03.jpg',
        license_url='https://creativecommons.org/publicdomain/zero/1.0/'
    )
    assert image_store.total_images == 3


def test_ImageStore_get_image_places_given_args(
        monkeypatch,
        setup_env
):
    image_store = image.ImageStore(provider='testing_provider')
    args_dict = {
        'foreign_landing_url': 'https://landing_page.com',
        'image_url': 'http://imageurl.com',
        'license_': 'testlicense',
        'license_version': '1.0',
        'license_url': None,
        'foreign_identifier': 'foreign_id',
        'thumbnail_url': 'http://thumbnail.com',
        'width': 200,
        'height': 500,
        'creator': 'tyler',
        'creator_url': 'https://creatorurl.com',
        'title': 'agreatpicture',
        'meta_data': {'description': 'cat picture'},
        'raw_tags': [{'name': 'tag1', 'provider': 'testing'}],
        'watermarked': 'f',
        'source': 'testing_source'
    }

    def mock_license_chooser(license_url, license_, license_version):
        return image.licenses.LicenseInfo(
            license_, license_version, license_url
        )
    monkeypatch.setattr(
        image.licenses,
        'get_license_info',
        mock_license_chooser
    )

    def mock_get_source(source, provider):
        return source
    monkeypatch.setattr(
        image.util,
        'get_source',
        mock_get_source
    )

    def mock_enrich_tags(tags):
        return tags
    monkeypatch.setattr(
        image_store,
        '_enrich_tags',
        mock_enrich_tags
    )

    actual_image = image_store._get_image(**args_dict)
    args_dict['tags'] = args_dict.pop('raw_tags')
    args_dict.pop('license_url')
    args_dict['provider'] = 'testing_provider'
    args_dict['filesize'] = None
    assert actual_image == image._Image(**args_dict)


def test_ImageStore_get_image_calls_license_chooser(
        monkeypatch,
        setup_env,
):
    image_store = image.ImageStore()

    def mock_license_chooser(license_url, license_, license_version):
        return image.licenses.LicenseInfo(
            'diff_license', None, license_url
        )
    monkeypatch.setattr(
        image.licenses,
        'get_license_info',
        mock_license_chooser
    )

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.license_ == 'diff_license'


def test_ImageStore_get_image_gets_source(
        monkeypatch,
        setup_env,
):
    image_store = image.ImageStore()

    def mock_get_source(source, provider):
        return 'diff_source'
    monkeypatch.setattr(image.util, 'get_source', mock_get_source)

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.source == 'diff_source'


def test_ImageStore_get_image_replaces_non_dict_meta_data_with_no_license_url(
        setup_env,
):
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_url=None,
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data='notadict',
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.meta_data == {
        'license_url': None, 'raw_license_url': None
    }


def test_ImageStore_get_image_creates_meta_data_with_valid_license_url(
        monkeypatch, setup_env
):
    def mock_license_chooser(license_url, license_, license_version):
        return image.licenses.LicenseInfo(
            license_, license_version, license_url
        )
    monkeypatch.setattr(
        image.licenses,
        'get_license_info',
        mock_license_chooser
    )
    license_url = 'https://my.license.url'
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_url=license_url,
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.meta_data == {
        'license_url': license_url, 'raw_license_url': license_url
    }


def test_ImageStore_get_image_adds_valid_license_url_to_dict_meta_data(
        monkeypatch, setup_env
):
    def mock_license_chooser(license_url, license_, license_version):
        return image.licenses.LicenseInfo(
            license_, license_version, license_url
        )
    monkeypatch.setattr(
        image.licenses,
        'get_license_info',
        mock_license_chooser
    )
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data={'key1': 'val1'},
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.meta_data == {
        'key1': 'val1',
        'license_url': 'https://license/url',
        'raw_license_url': 'https://license/url'
    }


def test_ImageStore_get_image_fixes_invalid_license_url(
        monkeypatch, setup_env
):
    original_url = 'https://license/url',
    updated_url = 'https://updatedurl.com'

    def mock_license_chooser(license_url, license_, license_version):
        return image.licenses.LicenseInfo(
            license_, license_version, updated_url
        )
    monkeypatch.setattr(
        image.licenses,
        'get_license_info',
        mock_license_chooser
    )
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_url=original_url,
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data={},
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.meta_data == {
        'license_url': updated_url, 'raw_license_url': original_url
    }


def test_ImageStore_get_image_enriches_singleton_tags(
        setup_env,
):
    image_store = image.ImageStore('test_provider')

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=['lone'],
        watermarked=None,
        source=None,
    )

    assert actual_image.tags == [{'name': 'lone', 'provider': 'test_provider'}]


def test_ImageStore_get_image_tag_blacklist(
        setup_env,
):
    raw_tags = [
        'cc0',
        'valid',
        'garbage:=metacrap',
        'uploaded:by=flickrmobile',
        {
            'name': 'uploaded:by=instagram',
            'provider': 'test_provider'
        }
    ]

    image_store = image.ImageStore('test_provider')

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=raw_tags,
        watermarked=None,
        source=None,
    )

    assert actual_image.tags == [
        {'name': 'valid', 'provider': 'test_provider'}
    ]


def test_ImageStore_get_image_enriches_multiple_tags(
        setup_env,
):
    image_store = image.ImageStore('test_provider')
    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=['tagone', 'tag2', 'tag3'],
        watermarked=None,
        source=None,
    )

    assert actual_image.tags == [
        {'name': 'tagone', 'provider': 'test_provider'},
        {'name': 'tag2', 'provider': 'test_provider'},
        {'name': 'tag3', 'provider': 'test_provider'},
    ]


def test_ImageStore_get_image_leaves_preenriched_tags(
        setup_env
):
    image_store = image.ImageStore('test_provider')
    tags = [
        {'name': 'tagone', 'provider': 'test_provider'},
        {'name': 'tag2', 'provider': 'test_provider'},
        {'name': 'tag3', 'provider': 'test_provider'},
    ]

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=tags,
        watermarked=None,
        source=None,
    )

    assert actual_image.tags == tags


def test_ImageStore_get_image_nones_nonlist_tags(
        setup_env,
):
    image_store = image.ImageStore('test_provider')
    tags = 'notalist'

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=tags,
        watermarked=None,
        source=None,
    )

    assert actual_image.tags is None


@pytest.fixture
def default_image_args(
        setup_env,
):
    return dict(
        foreign_identifier=None,
        foreign_landing_url='https://image.org',
        image_url='https://image.org',
        thumbnail_url=None,
        width=None,
        height=None,
        filesize=None,
        license_='cc0',
        license_version='1.0',
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        tags=None,
        watermarked=None,
        provider=None,
        source=None,
    )


def test_create_tsv_row_non_none_if_req_fields(
        default_image_args,
        get_good,
        setup_env,
):
    image_store = image.ImageStore()
    test_image = image._Image(**default_image_args)
    actual_row = image_store._create_tsv_row(test_image)
    assert actual_row is not None


def test_create_tsv_row_none_if_no_foreign_landing_url(
        default_image_args,
        setup_env,
):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['foreign_landing_url'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_none_if_no_license(
        default_image_args,
        setup_env,
):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['license_'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_none_if_no_license_version(
        default_image_args,
        setup_env,
):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['license_version'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_returns_none_if_missing_image_url(
        default_image_args,
        setup_env,
):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['image_url'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_handles_empty_dict_and_tags(
        default_image_args,
        setup_env,
):
    image_store = image.ImageStore()
    meta_data = {}
    tags = []
    image_args = default_image_args
    image_args['meta_data'] = meta_data
    image_args['tags'] = tags
    test_image = image._Image(**image_args)

    actual_row = image_store._create_tsv_row(test_image).split('\t')
    actual_meta_data, actual_tags = actual_row[12], actual_row[13]
    expect_meta_data, expect_tags = '\\N', '\\N'
    assert expect_meta_data == actual_meta_data
    assert expect_tags == actual_tags


def test_create_tsv_row_turns_empty_into_nullchar(
        default_image_args,
        setup_env,
):
    image_store = image.ImageStore()
    image_args = default_image_args
    test_image = image._Image(**image_args)

    actual_row = image_store._create_tsv_row(test_image).split('\t')
    assert all(
        [
            actual_row[i] == '\\N'
            for i in [0, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15]
        ]
    ) is True
    assert actual_row[-1] == '\\N\n'


def test_create_tsv_row_properly_places_entries(
        setup_env, monkeypatch
):

    def mock_validate_url(url_string):
        return url_string

    monkeypatch.setattr(
        image.columns.urls, 'validate_url_string', mock_validate_url
    )
    image_store = image.ImageStore()
    req_args_dict = {
        'foreign_landing_url': 'https://landing_page.com',
        'image_url': 'http://imageurl.com',
        'license_': 'testlicense',
        'license_version': '1.0',
    }
    args_dict = {
        'foreign_identifier': 'foreign_id',
        'thumbnail_url': 'http://thumbnail.com',
        'width': 200,
        'height': 500,
        'filesize': None,
        'creator': 'tyler',
        'creator_url': 'https://creatorurl.com',
        'title': 'agreatpicture',
        'meta_data': {'description': 'cat picture'},
        'tags': [{'name': 'tag1', 'provider': 'testing'}],
        'watermarked': 'f',
        'provider': 'testing_provider',
        'source': 'testing_source'
    }
    args_dict.update(req_args_dict)

    test_image = image._Image(**args_dict)
    actual_row = image_store._create_tsv_row(
        test_image
    )
    expect_row = '\t'.join([
        'foreign_id',
        'https://landing_page.com',
        'http://imageurl.com',
        'http://thumbnail.com',
        '200',
        '500',
        '\\N',
        'testlicense',
        '1.0',
        'tyler',
        'https://creatorurl.com',
        'agreatpicture',
        '{"description": "cat picture"}',
        '[{"name": "tag1", "provider": "testing"}]',
        'f',
        'testing_provider',
        'testing_source'
    ]) + '\n'
    assert expect_row == actual_row
