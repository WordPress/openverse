import os

import WikimediaCommons as wmc


def test_extract_creator_info_handles_plaintext():
    artist_string = 'Artist Name'
    image_info = {
        "extmetadata": {
            "Artist": {
                "value": artist_string,
                "source": "commons-desc-page"
            }
        }
    }
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = artist_string
    expect_creator_url = None
    assert expect_creator == actual_creator and expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_well_formed_link():
    artist_string = '<a href="https://test.com/linkspot" title="linktitle">link text</a>'
    image_info = {
        "extmetadata": {
            "Artist": {
                "value": artist_string,
                "source": "commons-desc-page"
            }
        }
    }
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'link text'
    expect_creator_url = 'https://test.com/linkspot'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_div_with_no_link():
    artist_string = '<div class="fn value">\nJona Lendering</div>'
    image_info = {
        "extmetadata": {
            "Artist": {
                "value": artist_string,
                "source": "commons-desc-page"
            }
        }
    }
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'Jona Lendering'
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_internal_wc_link():
    artist_string = '<a href="//commons.wikimedia.org/w/index.php?title=User:NotaRealUser&amp;action=edit&amp;redlink=1" class="new" title="User:NotaRealUser (page does not exist)">NotaRealUser</a>'
    image_info = {
        "extmetadata": {
            "Artist": {
                "value": artist_string,
                "source": "commons-desc-page"
            }
        }
    }
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'NotaRealUser'
    expect_creator_url = 'https://commons.wikimedia.org/w/index.php?title=User:NotaRealUser&action=edit&redlink=1'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_link_as_partial_text():
    artist_string = "<a rel=\"nofollow\" class=\"external text\" href=\"https://www.flickr.com/people/16707908@N07\">Jeff &amp; Brian</a> from Eastbourne"
    image_info = {"extmetadata": {"Artist": {"value": artist_string, "source": "commons-desc-page"}}}
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = 'Jeff & Brian from Eastbourne'
    expect_creator_url = 'https://www.flickr.com/people/16707908@N07'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_process_image_data_handles_example_dict():
    """
    This test is just a basic snapshot, here to make refactoring slightly safer
    """
    image_data = {
        "pageid": 81754323,
        "ns": 6,
        "title": "File:20120925 PlozevetBretagne LoneTree DSC07971 PtrQs.jpg",
        "imagerepository": "local",
        "imageinfo": [
          {
            "user": "PtrQs",
            "size": 11863148,
            "width": 5514,
            "height": 3102,
            "thumburl": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg/300px-20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg",
            "thumbwidth": 300,
            "thumbheight": 169,
            "url": "https://upload.wikimedia.org/wikipedia/commons/2/25/20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg",
            "descriptionurl": "https://commons.wikimedia.org/wiki/File:20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg",
            "descriptionshorturl": "https://commons.wikimedia.org/w/index.php?curid=81754323",
            "extmetadata": {
              "DateTime": {
                "value": "2019-09-01 00:38:47",
                "source": "mediawiki-metadata",
                "hidden": ""
              },
              "ObjectName": {
                "value": "20120925 PlozevetBretagne LoneTree DSC07971 PtrQs",
                "source": "mediawiki-metadata",
                "hidden": ""
              },
              "CommonsMetadataExtension": {
                "value": 1.2,
                "source": "extension",
                "hidden": ""
              },
              "Categories": {
                "value": "Coasts of Finistère|Photographs taken with Minolta AF Zoom 28-70mm F2.8 G|Plozévet|Self-published work|Taken with Sony DSLR-A900|Trees in Finistère",
                "source": "commons-categories",
                "hidden": ""
              },
              "Assessments": {
                "value": "",
                "source": "commons-categories",
                "hidden": ""
              },
              "ImageDescription": {
                "value": "SONY DSC",
                "source": "commons-desc-page"
              },
              "DateTimeOriginal": {
                "value": "2012-09-25 16:23:02",
                "source": "commons-desc-page"
              },
              "Credit": {
                "value": "<span class=\"int-own-work\" lang=\"en\">Own work</span>",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Artist": {
                "value": "<a href=\"//commons.wikimedia.org/wiki/User:PtrQs\" title=\"User:PtrQs\">PtrQs</a>",
                "source": "commons-desc-page"
              },
              "LicenseShortName": {
                "value": "CC BY-SA 4.0",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "UsageTerms": {
                "value": "Creative Commons Attribution-Share Alike 4.0",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "AttributionRequired": {
                "value": "true",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Attribution": {
                "value": "Photo by <a href=\"//commons.wikimedia.org/wiki/User:PtrQs\" title=\"User:PtrQs\">PtrQs</a>",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "LicenseUrl": {
                "value": "https://creativecommons.org/licenses/by-sa/4.0",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Copyrighted": {
                "value": "True",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Restrictions": {
                "value": "",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "License": {
                "value": "cc-by-sa-4.0",
                "source": "commons-templates",
                "hidden": ""
              }
            }
          }
        ]
      }
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
    min_data = {
        "imageinfo": [
          {
            "url": "https://upload.wikimedia.org/image.jpg",
            "descriptionshorturl": "https://commons.wikimedia.org/descriptionurl",
            "extmetadata": {
              "LicenseUrl": {
                "value": "https://creativecommons.org/licenses/by-sa/4.0",
                "source": "commons-desc-page",
                "hidden": ""
              }
            }
          }
        ]
      }
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
    no_foreign_url_data = {
        "imageinfo": [
          {
            "url": "https://upload.wikimedia.org/image.jpg",
            "extmetadata": {
              "LicenseUrl": {
                "value": "https://creativecommons.org/licenses/by-sa/4.0",
                "source": "commons-desc-page",
                "hidden": ""
              }
            }
          }
        ]
      }
    actual_row = wmc.process_image_data(no_foreign_url_data)
    expect_row = None
    assert actual_row == expect_row


def test_process_image_data_returns_none_when_missing_image_url():
    no_image_url_data = {
        "imageinfo": [
          {
            "descriptionshorturl": "https://commons.wikimedia.org/descriptionurl",
            "extmetadata": {
              "LicenseUrl": {
                "value": "https://creativecommons.org/licenses/by-sa/4.0",
                "source": "commons-desc-page",
                "hidden": ""
              }
            }
          }
        ]
      }
    actual_row = wmc.process_image_data(no_image_url_data)
    expect_row = None
    assert actual_row == expect_row


def test_process_image_data_returns_none_when_missing_image_info():
    no_image_info_data = {
        "pageid": 81754323,
        "title": "File:20120925 PlozevetBretagne LoneTree DSC07971 PtrQs.jpg",
      }
    actual_row = wmc.process_image_data(no_image_info_data)
    expect_row = None
    assert actual_row == expect_row


def test_get_image_batch_returns_correctly_without_continue(monkeypatch):
    resp_dict = {
        "batchcomplete": "",
        "continue": {"continue": "gaicontinue||"},
        "query": {
            "pages": {
                "84798633": {
                    "pageid": 84798633,
                    "title": "File:Ambassade1.jpg"
                }
            }
        }
    }

    def mock_response(endpoint):
        expect_endpoint = "https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json"
        if endpoint == expect_endpoint:
            return resp_dict
        else:
            return None

    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    continue_token, result = wmc.get_image_batch('2019-01-01', '2019-01-02')
    assert continue_token is None
    assert result == resp_dict['query']['pages']


def test_get_image_batch_returns_correctly_with_continue(monkeypatch):
    resp_dict = {
        "batchcomplete": "",
        "continue": {
            "gaicontinue": "next.jpg",
            "continue": "gaicontinue||"
        },
        "query": {
            "pages": {
                "84798633": {
                    "pageid": 84798633,
                    "title": "File:Ambassade1.jpg"
                }
            }
        }
    }

    def mock_response(endpoint):
        expect_endpoint = "https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json"
        if endpoint == expect_endpoint:
            return resp_dict
        else:
            return None

    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    continue_token, result = wmc.get_image_batch('2019-01-01', '2019-01-02')
    assert result == resp_dict['query']['pages']
    assert continue_token == resp_dict['continue']['gaicontinue']


def test_get_image_batch_returns_correctly_when_given_continue(monkeypatch):
    resp_dict = {
        "batchcomplete": "",
        "continue": {
            "gaicontinue": "next2jpg",
            "continue": "gaicontinue||"
        },
        "query": {
            "pages": {
                "84798633": {
                    "pageid": 84798633,
                    "title": "File:Ambassade1.jpg"
                }
            }
        }
    }

    def mock_response(endpoint):
        expect_endpoint = "https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json&gaicontinue=next.jpg"
        if endpoint == expect_endpoint:
            return resp_dict
        else:
            return None

    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')
    monkeypatch.setattr(wmc.etl_mods, 'requestContent', mock_response)
    continue_token, result = wmc.get_image_batch(
        '2019-01-01', '2019-01-02', continue_='next.jpg')
    assert result == resp_dict['query']['pages']
    assert continue_token == resp_dict['continue']['gaicontinue']


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
    resp_dict_0 = {
        "batchcomplete": "",
        "continue": {
            "gaicontinue": "next.jpg",
            "continue": "gaicontinue||"
        },
        "query": {
            "pages": {
                "123": {
                    "pageid": 123,
                    "ns": 6,
                    "title": "File:prettypic0.jpg",
                    "imagerepository": "local",
                    "imageinfo": [
                        {
                            "user": "User0",
                            "size": 10000,
                            "width": 5000,
                            "height": 3000,
                            "thumburl": "https://upl.wiki.org/thumburl0",
                            "thumbwidth": 300,
                            "thumbheight": 180,
                            "url": "https://upl.wiki.org/url0",
                            "descriptionurl": "https://comm.wiki.org/desc0",
                            "descriptionshorturl": "https://comm.wiki.org/sml1",
                            "extmetadata": {
                                "ObjectName": {
                                    "value": "prettypic0.jpg",
                                    "source": "mediawiki-metadata",
                                    "hidden": ""
                                },
                                "ImageDescription": {
                                    "value": "description 0",
                                    "source": "commons-desc-page"
                                },
                                "Artist": {
                                    "value": "<a href=\"//commons.wikimedia.org/wiki/User:User0\" title=\"User:User0\">User0</a>",
                                    "source": "commons-desc-page"
                                },
                                "LicenseUrl": {
                                    "value": "https://creativecommons.org/licenses/by-sa/4.0",
                                    "source": "commons-desc-page",
                                    "hidden": ""
                                },
                            }
                        }
                    ]
                }
            }
        }
    }

    resp_dict_1 = {
        "batchcomplete": "",
        "continue": {},
        "query": {
            "pages": {
                "456": {
                    "pageid": 456,
                    "title": "File:prettypic1.jpg",
                    "imageinfo": [
                        {
                            "user": "User1",
                            "size": 20000,
                            "width": 10000,
                            "height": 6000,
                            "thumburl": "https://upl.wiki.org/thumburl1",
                            "thumbwidth": 300,
                            "thumbheight": 180,
                            "url": "https://upl.wiki.org/url1",
                            "descriptionurl": "https://comm.wiki.org/desc1",
                            "descriptionshorturl": "https://comm.wiki.org/sml1",
                            "extmetadata": {
                                "ImageDescription": {
                                    "value": "decription 1",
                                    "source": "commons-desc-page"
                                },
                                "Artist": {
                                    "value": "<a rel=\"nofollow\" class=\"external text\" href=\"http://www.geograph.org.uk/profile/1234\">Alice Bobby</a>",
                                    "source": "commons-desc-page"
                                },
                                "LicenseUrl": {
                                    "value": "https://creativecommons.org/licenses/by-sa/4.0",
                                    "source": "commons-desc-page",
                                    "hidden": ""
                                },
                            }
                        }
                    ]
                },
                "789": {
                    "pageid": 789,
                    "title": "File:prettypic2.jpg",
                    "imageinfo": [
                        {
                            "user": "User2",
                            "size": 2000,
                            "width": 1000,
                            "height": 500,
                            "thumburl": "https://upl.wiki.org/thumburl2",
                            "thumbwidth": 300,
                            "thumbheight": 150,
                            "url": "https://upl.wiki.org/url2",
                            "descriptionurl": "https://comm.wiki.org/desc2",
                            "descriptionshorturl": "https://comm.wiki.org/sml2",
                            "extmetadata": {
                                "ImageDescription": {
                                    "value": "decription 2",
                                    "source": "commons-desc-page"
                                },
                                "Artist": {
                                    "value": "<a rel=\"nofollow\" class=\"external text\" href=\"http://www.geograph.org.uk/profile/5678\">Charlie Doe</a>",
                                    "source": "commons-desc-page"
                                },
                                "LicenseUrl": {
                                    "value": "https://creativecommons.org/licenses/by-sa/2.0",
                                    "source": "commons-desc-page",
                                    "hidden": ""
                                }
                            }
                        }
                    ]
                }
            }
        }
    }

    def mock_delay(proc_time, delay):
        pass

    def mock_response(endpoint):
        expect_endpoint_0 = "https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json"
        expect_endpoint_1 = "https://testhost.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=12345&gaisort=timestamp&gaistart=2019-01-01T00:00:00Z&gaiend=2019-01-02T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json&gaicontinue=next.jpg"
        if endpoint == expect_endpoint_0:
            return resp_dict_0
        elif endpoint == expect_endpoint_1:
            return resp_dict_1
        else:
            return None

    tmp_directory = '/tmp/'
    output_filename = 'wikimedia_test.tsv'
    monkeypatch.setattr(wmc.etl_mods, "requestContent", mock_response)
    monkeypatch.setattr(wmc.etl_mods, "delayProcessing", mock_delay)
    monkeypatch.setattr(
        wmc.etl_mods.writeToFile, '__defaults__', (tmp_directory,))
    output_fullpath = os.path.join(tmp_directory, output_filename)
    try:
        os.remove(output_fullpath)
    except:
        print("Could not delete old output.  Perhaps it does not exist yet.")
    expected_records = 3

    monkeypatch.setattr(wmc.etl_mods, "requestContent", mock_response)
    monkeypatch.setattr(wmc.etl_mods, "delayProcessing", mock_delay)

    monkeypatch.setattr(
        wmc.etl_mods.writeToFile, '__defaults__', (tmp_directory,))
    monkeypatch.setattr(wmc, "FILE", output_filename)
    monkeypatch.setattr(wmc, 'LIMIT', 12345)
    monkeypatch.setattr(wmc, 'WM_HOST', 'testhost.org')

    wmc.exec_job({'start': '2019-01-01', 'end': '2019-01-02'})

    with open(output_fullpath) as f:
        actual_filestring = f.read()
    expect_filestring = """123\thttps://comm.wiki.org/sml1\thttps://upl.wiki.org/url0\thttps://upl.wiki.org/thumburl0\t5000\t3000\t\\N\tby-sa\t4.0\tUser0\thttp://commons.wikimedia.org/wiki/User:User0\tFile:prettypic0.jpg\t{"description": "description 0"}\t\\N\tf\twikimedia\twikimedia
456\thttps://comm.wiki.org/sml1\thttps://upl.wiki.org/url1\thttps://upl.wiki.org/thumburl1\t10000\t6000\t\\N\tby-sa\t4.0\tAlice Bobby\thttp://www.geograph.org.uk/profile/1234\tFile:prettypic1.jpg\t{"description": "decription 1"}\t\\N\tf\twikimedia\twikimedia
789\thttps://comm.wiki.org/sml2\thttps://upl.wiki.org/url2\thttps://upl.wiki.org/thumburl2\t1000\t500\t\\N\tby-sa\t2.0\tCharlie Doe\thttp://www.geograph.org.uk/profile/5678\tFile:prettypic2.jpg\t{"description": "decription 2"}\t\\N\tf\twikimedia\twikimedia\n"""
    assert expect_filestring == actual_filestring
