from provider_api_scripts.modules import etlMods


def test_create_tsv_list_row_returns_none_if_missing_foreign_landing_url():
    expect_row = None
    actual_row = etlMods.create_tsv_list_row(
        foreign_identifier="a", image_url="a", license_="abc", license_version="123"
    )
    assert expect_row == actual_row


def test_create_tsv_list_row_returns_none_if_missing_license():
    expect_row = None
    actual_row = etlMods.create_tsv_list_row(
        foreign_identifier="a",
        image_url="a",
        license_version="123",
        foreign_landing_url="www.testurl.com",
    )
    assert expect_row == actual_row


def test_create_tsv_list_row_returns_none_if_missing_license_version():
    expect_row = None
    actual_row = etlMods.create_tsv_list_row(
        foreign_identifier="a",
        image_url="a",
        license_="abc",
        foreign_landing_url="www.testurl.com",
    )
    assert expect_row == actual_row


def test_create_tsv_list_row_returns_none_if_missing_image_url():
    expect_row = None
    actual_row = etlMods.create_tsv_list_row(
        foreign_identifier="a", foreign_landing_url="www.testurl.com", license_="abc"
    )
    assert expect_row == actual_row


def test_create_tsv_list_row_casts_to_strings():
    meta_data = {"key1": "value1", "key2": "value2"}
    tags = [
        {"name": "valuea", "provider": "valueb"},
        {"name": "aname", "provider": "aprovider"},
    ]
    height = 234
    width = 102314

    actual_row = etlMods.create_tsv_list_row(
        foreign_landing_url="www.testurl.comk",
        image_url="a",
        license_="abc",
        license_version="234",
        width=width,
        height=height,
        meta_data=meta_data,
        tags=tags,
    )
    assert all([type(element) == str for element in actual_row])


def test_create_tsv_list_row_handles_empty_dict_and_tags():
    meta_data = {}
    tags = []

    actual_row = etlMods.create_tsv_list_row(
        foreign_landing_url="www.testurl.comk",
        image_url="a",
        license_="abc",
        license_version="123",
        meta_data=meta_data,
        tags=tags,
    )
    actual_meta_data, actual_tags = actual_row[12], actual_row[13]
    expect_meta_data, expect_tags = "\\N", "\\N"
    assert expect_meta_data == actual_meta_data
    assert expect_tags == actual_tags


def test_create_tsv_list_row_turns_empty_into_nullchar():
    req_args_dict = {
        "foreign_landing_url": "landing_page.com",
        "image_url": "imageurl.com",
        "license_": "testlicense",
        "license_version": "1.0",
    }
    args_dict = {
        "foreign_identifier": None,
        "thumbnail": None,
        "width": None,
        "height": None,
        "filesize": None,
        "creator": None,
        "creator_url": None,
        "title": None,
        "meta_data": None,
        "tags": None,
        "watermarked": "f",
        "provider": None,
        "source": None,
    }
    args_dict.update(req_args_dict)

    actual_row = etlMods.create_tsv_list_row(**args_dict)
    expect_row = [
        "\\N",
        "landing_page.com",
        "imageurl.com",
        "\\N",
        "\\N",
        "\\N",
        "\\N",
        "testlicense",
        "1.0",
        "\\N",
        "\\N",
        "\\N",
        "\\N",
        "\\N",
        "f",
        "\\N",
        "\\N",
    ]
    assert actual_row == expect_row


def test_create_tsv_list_row_properly_places_entries():
    req_args_dict = {
        "foreign_landing_url": "landing_page.com",
        "image_url": "imageurl.com",
        "license_": "testlicense",
        "license_version": "1.0",
    }
    args_dict = {
        "foreign_identifier": "foreign_id",
        "thumbnail": "thumbnail.com",
        "width": 200,
        "height": 500,
        "creator": "tyler",
        "creator_url": "creatorurl.com",
        "title": "agreatpicture",
        "meta_data": {"description": "cat picture"},
        "tags": [{"name": "tag1", "provider": "testing"}],
        "watermarked": "f",
        "provider": "testing",
        "source": "testing",
    }
    args_dict.update(req_args_dict)

    actual_row = etlMods.create_tsv_list_row(**args_dict)
    expect_row = [
        "foreign_id",
        "landing_page.com",
        "imageurl.com",
        "thumbnail.com",
        "200",
        "500",
        "\\N",
        "testlicense",
        "1.0",
        "tyler",
        "creatorurl.com",
        "agreatpicture",
        '{"description": "cat picture"}',
        '[{"name": "tag1", "provider": "testing"}]',
        "f",
        "testing",
        "testing",
    ]
    assert expect_row == actual_row


def test_create_tsv_row_sanitizes_dicts_and_lists(monkeypatch):
    def mock_sanitize_json_values(some_json):
        return "SANITIZED"

    monkeypatch.setattr(etlMods, "_sanitize_json_values", mock_sanitize_json_values)
    actual_row = etlMods.create_tsv_list_row(
        foreign_landing_url="landing_page.com",
        image_url="imageurl.com",
        license_="testlicense",
        license_version="1.0",
        meta_data={"key1": "val1"},
        tags=["item", "item2"],
    )
    expect_row = [
        "\\N",
        "landing_page.com",
        "imageurl.com",
        "\\N",
        "\\N",
        "\\N",
        "\\N",
        "testlicense",
        "1.0",
        "\\N",
        "\\N",
        "\\N",
        '"SANITIZED"',
        '"SANITIZED"',
        "f",
        "\\N",
        "\\N",
    ]
    print(actual_row)
    assert expect_row == actual_row


def test_sanitize_json_values_handles_flat_dict(monkeypatch):
    def mock_sanitizeString(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(etlMods, "sanitizeString", mock_sanitizeString)
    given_dict = {"key1": "val1", "key2": "val2"}
    actual_dict = etlMods._sanitize_json_values(given_dict)
    expect_dict = {"key1": "val1 sanitized", "key2": "val2 sanitized"}
    assert expect_dict == actual_dict


def test_sanitize_json_values_handles_nested_dict(monkeypatch):
    def mock_sanitizeString(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(etlMods, "sanitizeString", mock_sanitizeString)
    given_dict = {"key1": "val1", "key2": {"key3": "val3"}}
    actual_dict = etlMods._sanitize_json_values(given_dict)
    expect_dict = {"key1": "val1 sanitized", "key2": {"key3": "val3 sanitized"}}
    assert expect_dict == actual_dict


def test_sanitize_json_values_handles_dict_containing_list(monkeypatch):
    def mock_sanitizeString(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(etlMods, "sanitizeString", mock_sanitizeString)
    given_dict = {"key1": "val1", "key2": ["item1", "item2"]}
    actual_dict = etlMods._sanitize_json_values(given_dict)
    expect_dict = {
        "key1": "val1 sanitized",
        "key2": ["item1 sanitized", "item2 sanitized"],
    }
    assert expect_dict == actual_dict


def test_sanitize_json_values_handles_list_of_str(monkeypatch):
    def mock_sanitizeString(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(etlMods, "sanitizeString", mock_sanitizeString)
    given_list = ["item1", "item2"]
    actual_list = etlMods._sanitize_json_values(given_list)
    expect_list = ["item1 sanitized", "item2 sanitized"]
    assert expect_list == actual_list


def test_sanitize_json_values_handles_list_of_list(monkeypatch):
    def mock_sanitizeString(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(etlMods, "sanitizeString", mock_sanitizeString)
    given_list = ["item1", ["item2", ["item3"], "item4"], "item5"]
    actual_list = etlMods._sanitize_json_values(given_list)
    expect_list = [
        "item1 sanitized",
        ["item2 sanitized", ["item3 sanitized"], "item4 sanitized"],
        "item5 sanitized",
    ]
    assert expect_list == actual_list


def test_sanitize_json_values_handles_list_of_dict(monkeypatch):
    def mock_sanitizeString(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(etlMods, "sanitizeString", mock_sanitizeString)
    given_list = [
        {"name": "valuea", "provider": "valueb"},
        {"name": "aname", "provider": "aprovider"},
    ]
    actual_list = etlMods._sanitize_json_values(given_list)
    expect_list = [
        {"name": "valuea sanitized", "provider": "valueb sanitized"},
        {"name": "aname sanitized", "provider": "aprovider sanitized"},
    ]
    assert expect_list == actual_list


def test_sanitize_json_values_does_not_over_recurse():
    L = []
    L.extend([L])
    actual_list = etlMods._sanitize_json_values(L, recursion_limit=3)
    expect_list = [[["[[...]]"]]]
    assert actual_list == expect_list
