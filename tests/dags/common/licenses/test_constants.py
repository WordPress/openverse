from common.licenses import constants


def test_get_license_path_map_comprehenseion(monkeypatch):
    example_paths = [
        "licenses/by/1.0",
        "licenses/by/2.0",
        "licenses/by-nd/3.0",
        "licenses/by-sa/2.0",
    ]
    monkeypatch.setattr(constants, "_SIMPLE_LICENSE_PATHS", example_paths[:2])
    monkeypatch.setattr(
        constants, "_SIMPLE_IRREVERSIBLE_LICENSE_PATHS", example_paths[2:]
    )
    monkeypatch.setattr(constants, "_SPECIAL_CASE_LICENSE_PATHS", {})
    monkeypatch.setattr(constants, "_SPECIAL_CASE_IRREVERSIBLE_LICENSE_PATHS", {})
    actual_license_path_map = constants.get_license_path_map()
    expect_license_path_map = {
        "licenses/by/1.0": ("by", "1.0"),
        "licenses/by/2.0": ("by", "2.0"),
        "licenses/by-nd/3.0": ("by-nd", "3.0"),
        "licenses/by-sa/2.0": ("by-sa", "2.0"),
    }
    assert expect_license_path_map == actual_license_path_map


def test_get_license_path_map_update(monkeypatch):
    simple_paths = [
        "licenses/by/1.0",
        "licenses/by/2.0",
        "licenses/by-nd/3.0",
        "licenses/by-sa/2.0",
    ]
    special_paths = {
        "licenses/by-nc-nd/1.0": ("by-nd-nc", "1.0"),
        "publicdomain/zero/1.0": ("cc0", "1.0"),
        "publicdomain/mark/1.0": ("pdm", "1.0"),
    }
    special_irr_paths = {
        "licenses/mark/1.0": ("pdm", "1.0"),
    }
    monkeypatch.setattr(constants, "_SIMPLE_LICENSE_PATHS", simple_paths[:2])
    monkeypatch.setattr(
        constants, "_SIMPLE_IRREVERSIBLE_LICENSE_PATHS", simple_paths[2:]
    )
    monkeypatch.setattr(constants, "_SPECIAL_CASE_LICENSE_PATHS", special_paths)
    monkeypatch.setattr(
        constants, "_SPECIAL_CASE_IRREVERSIBLE_LICENSE_PATHS", special_irr_paths
    )
    actual_license_path_map = constants.get_license_path_map()
    expect_license_path_map = {
        "licenses/by/1.0": ("by", "1.0"),
        "licenses/by/2.0": ("by", "2.0"),
        "licenses/by-nd/3.0": ("by-nd", "3.0"),
        "licenses/by-sa/2.0": ("by-sa", "2.0"),
        "licenses/by-nc-nd/1.0": ("by-nd-nc", "1.0"),
        "licenses/mark/1.0": ("pdm", "1.0"),
        "publicdomain/mark/1.0": ("pdm", "1.0"),
        "publicdomain/zero/1.0": ("cc0", "1.0"),
    }
    assert expect_license_path_map == actual_license_path_map


def test_get_reverse_license_path_map_comprehension(monkeypatch):
    example_paths = [
        "licenses/by/1.0",
        "licenses/by/2.0",
        "licenses/by-nd/3.0",
        "licenses/by-sa/2.0",
    ]
    monkeypatch.setattr(constants, "_SIMPLE_LICENSE_PATHS", example_paths[:2])
    monkeypatch.setattr(
        constants, "_SIMPLE_IRREVERSIBLE_LICENSE_PATHS", example_paths[2:]
    )
    monkeypatch.setattr(constants, "_SPECIAL_CASE_LICENSE_PATHS", {})
    monkeypatch.setattr(constants, "_SPECIAL_CASE_IRREVERSIBLE_LICENSE_PATHS", {})
    monkeypatch.setattr(constants, "_SPECIAL_REVERSE_ONLY_PATHS", {})
    actual_license_path_map = constants.get_reverse_license_path_map()
    expect_license_path_map = {
        ("by", "1.0"): "licenses/by/1.0",
        ("by", "2.0"): "licenses/by/2.0",
    }
    assert expect_license_path_map == actual_license_path_map


def test_get_reverse_license_path_map_update(monkeypatch):
    simple_paths = [
        "licenses/by/1.0",
        "licenses/by/2.0",
        "licenses/by-nd/3.0",
        "licenses/by-sa/2.0",
    ]
    special_paths = {
        "licenses/by-nc-nd/1.0": ("by-nd-nc", "1.0"),
        "publicdomain/zero/1.0": ("cc0", "1.0"),
        "publicdomain/mark/1.0": ("pdm", "1.0"),
    }
    special_irr_paths = {
        "licenses/mark/1.0": ("pdm", "1.0"),
    }
    special_rev_paths = {("by", "2.1"): "licenses/by/2.0"}
    monkeypatch.setattr(constants, "_SIMPLE_LICENSE_PATHS", simple_paths[:2])
    monkeypatch.setattr(
        constants, "_SIMPLE_IRREVERSIBLE_LICENSE_PATHS", simple_paths[2:]
    )
    monkeypatch.setattr(constants, "_SPECIAL_CASE_LICENSE_PATHS", special_paths)
    monkeypatch.setattr(
        constants, "_SPECIAL_CASE_IRREVERSIBLE_LICENSE_PATHS", special_irr_paths
    )
    monkeypatch.setattr(constants, "_SPECIAL_REVERSE_ONLY_PATHS", special_rev_paths)
    actual_license_path_map = constants.get_reverse_license_path_map()
    expect_license_path_map = {
        ("by", "1.0"): "licenses/by/1.0",
        ("by", "2.0"): "licenses/by/2.0",
        ("by-nd-nc", "1.0"): "licenses/by-nc-nd/1.0",
        ("pdm", "1.0"): "publicdomain/mark/1.0",
        ("cc0", "1.0"): "publicdomain/zero/1.0",
        ("by", "2.1"): "licenses/by/2.0",
    }
    assert expect_license_path_map == actual_license_path_map
