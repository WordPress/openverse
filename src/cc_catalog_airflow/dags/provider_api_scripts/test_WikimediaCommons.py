import os
import json

import WikimediaCommons as wmc

RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests/resources/wikimedia')


def test_extract_creator_info_handles_plaintext():
    with open(os.path.join(RESOURCES, 'image_info_artist_string.json')) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'Artist Name'
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_well_formed_link():
    with open(os.path.join(RESOURCES, 'image_info_artist_link.json')) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'link text'
    expect_creator_url = 'https://test.com/linkspot'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_div_with_no_link():
    with open(os.path.join(RESOURCES, 'image_info_artist_div.json')) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'Jona Lendering'
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_internal_wc_link():
    with open(
            os.path.join(RESOURCES, 'image_info_artist_internal_link.json')
    ) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'NotaRealUser'
    expect_creator_url = 'https://commons.wikimedia.org/w/index.php?title=User:NotaRealUser&action=edit&redlink=1'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_link_as_partial_text():
    with open(
            os.path.join(RESOURCES, 'image_info_artist_partial_link.json')
    ) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'Jeff & Brian from Eastbourne'
    expect_creator_url = 'https://www.flickr.com/people/16707908@N07'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_create_meta_data_scrapes_text_from_html_description():
    with open(
            os.path.join(RESOURCES, 'image_data_html_description.json')
    ) as f:
        image_data = json.load(f)
    actual_meta_data_dict = wmc.create_meta_data_dict(image_data)
    expected_meta_data_dict = {
        'description': 'Identificatie Titel(s):  Allegorie op kunstenaar Francesco Mazzoli, bekend als Parmigianino'
    }
    assert expected_meta_data_dict == actual_meta_data_dict


def test_process_image_data_handles_example_dict():
    """
    This test is just a basic snapshot, here to make refactoring slightly safer
    """
    with open(os.path.join(RESOURCES, 'image_data_example.json')) as f:
        image_data = json.load(f)
    actual_row = wmc.process_image_data(image_data)
    expect_row = [
        '81754323',
        'https://commons.wikimedia.org/w/index.php?curid=81754323',
        'https://upload.wikimedia.org/wikipedia/commons/2/25/20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg/300px-20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg',
        '5514',
        '3102',
        '\\N',
        'by-sa',
        '4.0',
        'PtrQs',
        'https://commons.wikimedia.org/wiki/User:PtrQs',
        'File:20120925 PlozevetBretagne LoneTree DSC07971 PtrQs.jpg',
        '{"description": "SONY DSC"}',
        '\\N',
        'f',
        'wikimedia',
        'wikimedia'
    ]
    assert expect_row == actual_row


def test_process_image_data_handles_bare_minimum():
    with open(os.path.join(RESOURCES, 'image_data_minimal.json')) as f:
        min_data = json.load(f)
    actual_row = wmc.process_image_data(min_data)
    expect_row = [
        '\\N',
        'https://commons.wikimedia.org/descriptionurl',
        'https://upload.wikimedia.org/image.jpg',
        '\\N',
        '\\N',
        '\\N',
        '\\N',
        'by-sa',
        '4.0',
        '\\N',
        '\\N',
        '\\N',
        '\\N',
        '\\N',
        'f',
        'wikimedia',
        'wikimedia'
    ]
    assert actual_row == expect_row


def test_process_image_data_returns_none_when_missing_foreign_url():
    with open(
            os.path.join(RESOURCES, 'image_data_missing_foreign_url.json')
    ) as f:
        no_foreign_url_data = json.load(f)
    actual_row = wmc.process_image_data(no_foreign_url_data)
    expect_row = None
    assert actual_row == expect_row


def test_process_image_data_returns_none_when_missing_image_url():
    with open(
            os.path.join(RESOURCES, 'image_data_missing_image_url.json')
    ) as f:
        no_image_url_data = json.load(f)
    actual_row = wmc.process_image_data(no_image_url_data)
    expect_row = None
    assert actual_row == expect_row


def test_process_image_data_returns_none_when_missing_image_info():
    with open(
            os.path.join(RESOURCES, 'image_data_missing_imageinfo.json')
    ) as f:
        no_image_info_data = json.load(f)
    actual_row = wmc.process_image_data(no_image_info_data)
    expect_row = None
    assert actual_row == expect_row


def test_get_image_batch_returns_correctly_without_continue(monkeypatch):
    with open(os.path.join(RESOURCES, 'response_small_no_continue.json')) as f:
        resp_dict = json.load(f)

    def mock_response(endpoint):
        expect_endpoint = 'https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json'
        if endpoint == expect_endpoint:
            return resp_dict
        else:
            return None

    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    expected_result = {
        '84798633': {
            'pageid': 84798633,
            'title': 'File:Ambassade1.jpg'
        }
    }

    continue_token, actual_result = wmc.get_image_batch(
        '2019-01-01', '2019-01-02'
    )
    assert continue_token is None
    assert actual_result == expected_result


def test_get_image_batch_returns_correctly_with_continue(monkeypatch):
    with open(
            os.path.join(RESOURCES, 'response_small_with_continue.json')
    ) as f:
        resp_dict = json.load(f)

    def mock_response(endpoint):
        expect_endpoint = 'https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json'
        if endpoint == expect_endpoint:
            return resp_dict
        else:
            return None

    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    expect_result = {
        '84798633': {
            'pageid': 84798633,
            'title': 'File:Ambassade1.jpg'
        }
    }
    expect_continue_token = 'next.jpg'
    actual_continue_token, actual_result = wmc.get_image_batch(
        '2019-01-01',
        '2019-01-02'
    )
    assert actual_result == expect_result
    assert actual_continue_token == expect_continue_token


def test_get_image_batch_returns_correctly_when_given_continue(monkeypatch):
    with open(
            os.path.join(RESOURCES, 'response_small_with_continue_2.json')
    ) as f:
        resp_dict = json.load(f)

    def mock_response(endpoint):
        expect_endpoint = 'https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json&gaicontinue=next.jpg'
        if endpoint == expect_endpoint:
            return resp_dict
        else:
            return None

    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    expect_continue_token = 'next2jpg'
    expect_result = {
        '84798633': {
            'pageid': 84798633,
            'title': 'File:Ambassade1.jpg'
        }
    }
    actual_continue_token, actual_result = wmc.get_image_batch(
        '2019-01-01', '2019-01-02', continue_='next.jpg')
    assert actual_result == expect_result
    assert actual_continue_token == expect_continue_token


def test_get_image_batch_returns_nonenone_when_no_content(monkeypatch):

    def mock_response(endpoint):
        return None

    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    continue_token, result = wmc.get_image_batch('2019-01-01', '2019-01-02')
    assert result is None
    assert continue_token is None


def test_exec_job(monkeypatch):
    with open(os.path.join(RESOURCES, 'response_large_0.json')) as f:
        resp_dict_0 = json.load(f)

    with open(os.path.join(RESOURCES, 'response_large_1.json')) as f:
        resp_dict_1 = json.load(f)

    def mock_delay(proc_time, delay):
        pass

    def mock_response(endpoint):
        expect_endpoint_0 = 'https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json'
        expect_endpoint_1 = 'https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json&gaicontinue=next.jpg'
        if endpoint == expect_endpoint_0:
            return resp_dict_0
        elif endpoint == expect_endpoint_1:
            return resp_dict_1
        else:
            return None

    tmp_directory = '/tmp/'
    output_filename = 'wikimedia_test.tsv'
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    monkeypatch.setattr(wmc.etl_mods, 'delayProcessing', mock_delay)
    monkeypatch.setattr(
        wmc.etl_mods.writeToFile, '__defaults__', (tmp_directory,))
    output_fullpath = os.path.join(tmp_directory, output_filename)
    try:
        os.remove(output_fullpath)
    except:
        print('Could not delete old output.  Perhaps it does not exist yet.')
    expected_records = 3

    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    monkeypatch.setattr(wmc.etl_mods, 'delayProcessing', mock_delay)

    monkeypatch.setattr(
        wmc.etl_mods.writeToFile, '__defaults__', (tmp_directory,))
    monkeypatch.setattr(wmc, 'FILE', output_filename)
    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')

    wmc.exec_job({'start': '2019-01-01', 'end': '2019-01-02'})

    with open(output_fullpath) as f:
        actual_filestring = f.read()
    with open(os.path.join(RESOURCES, 'exec_job_expect_output.tsv')) as f:
        expect_filestring = f.read()

    assert actual_filestring == expect_filestring
