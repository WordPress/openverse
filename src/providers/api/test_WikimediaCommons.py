import WikimediaCommons


def test_extract_creator_info_handles_plaintext():
    artist_string = 'Artist Name'
    image_info = {"extmetadata": {"Artist": {"value": artist_string, "source": "commons-desc-page" }}}
    actual_creator, actual_creator_url = WikimediaCommons.extract_creator_info(image_info)
    expect_creator = artist_string
    expect_creator_url = None
    assert expect_creator == actual_creator and expect_creator_url == actual_creator_url

def test_extract_creator_info_handles_well_formed_link():
    artist_string = '<a href="https://test.com/linkspot" title="linktitle">link text</a>'
    image_info = {"extmetadata": {"Artist": {"value": artist_string, "source": "commons-desc-page" }}}
    actual_creator, actual_creator_url = WikimediaCommons.extract_creator_info(image_info)
    expect_creator = 'link text'
    expect_creator_url = 'https://test.com/linkspot'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url

def test_extract_creator_info_handles_div_with_no_link():
    artist_string = '<div class="fn value">\nJona Lendering</div>'
    image_info = {"extmetadata": {"Artist": {"value": artist_string, "source": "commons-desc-page" }}}
    actual_creator, actual_creator_url = WikimediaCommons.extract_creator_info(image_info)
    expect_creator = 'Jona Lendering'
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url

def test_extract_creator_info_handles_internal_wc_link():
    artist_string = '<a href="//commons.wikimedia.org/w/index.php?title=User:NotaRealUser&amp;action=edit&amp;redlink=1" class="new" title="User:NotaRealUser (page does not exist)">NotaRealUser</a>'
    image_info = {"extmetadata": {"Artist": {"value": artist_string, "source": "commons-desc-page" }}}
    actual_creator, actual_creator_url = WikimediaCommons.extract_creator_info(image_info)
    expect_creator = 'NotaRealUser'
    expect_creator_url = 'https://commons.wikimedia.org/w/index.php?title=User:NotaRealUser&action=edit&redlink=1'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url

def test_extract_creator_info_handles_link_as_partial_text():
    artist_string = "<a rel=\"nofollow\" class=\"external text\" href=\"https://www.flickr.com/people/16707908@N07\">Jeff &amp; Brian</a> from Eastbourne"
    image_info = {"extmetadata": {"Artist": {"value": artist_string, "source": "commons-desc-page" }}}
    actual_creator, actual_creator_url = WikimediaCommons.extract_creator_info(image_info)
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
    actual_row = WikimediaCommons.process_image_data(image_data)
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
    actual_row = WikimediaCommons.process_image_data(min_data)
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
    actual_row = WikimediaCommons.process_image_data(no_foreign_url_data)
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
    actual_row = WikimediaCommons.process_image_data(no_image_url_data)
    expect_row = None
    assert actual_row == expect_row


def test_process_image_data_returns_none_when_missing_image_info():
    no_image_info_data = {
        "pageid": 81754323,
        "title": "File:20120925 PlozevetBretagne LoneTree DSC07971 PtrQs.jpg",
      }
    actual_row = WikimediaCommons.process_image_data(no_image_info_data)
    expect_row = None
    assert actual_row == expect_row
