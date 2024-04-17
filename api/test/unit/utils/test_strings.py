import pytest

from api.utils.strings import clean_tags, convert_grp, decode_data


p = pytest.param


@pytest.mark.parametrize(
    "grp, output",
    [
        p(r"03b1", "α", id="u-escaped without backslash"),
        p(r"e9", "é", id="x-escaped with double backslashes"),
        p(r"0000", "\x00", id="min-value"),
        p(r"ffff", "\uffff", id="max-value"),
        p(r"dadd", None, id="non-encodable value"),
    ],
)
def test_convert_grp(grp, output):
    assert convert_grp(grp) == output


@pytest.mark.parametrize(
    "data, expected",
    [
        p("", "", id="empty string"),
        p(None, "", id="None"),
        p("muséo", "muséo", id="single non-ASCII character"),
        p("mus\xe9o", "muséo", id="x-escaped with single backslash"),
        p("mus\u00e9o", "muséo", id="u-escaped with single backslash"),
        p("musu00e9o", "muséo", id="u-escaped without backslash"),
        p("mus\\u00e9o", "muséo", id="u-escaped with double backslash"),
        p(
            "mus\\u00E9o",
            "muséo",
            id="u-escaped with double backslash and uppercase hex",
        ),
        p("u03b9u03c4u03b1u03bbu03afu03b1", "ιταλία", id="1"),
        p("u0438u0442u0430u043bu0438u044f", "италия", id="5"),
        p("u0645u062au062du0641", "متحف", id="7"),
        p("ιταλία", "ιταλία", id="8"),
        p("太陽", "太陽", id="9"),
        p("u592Au967D", "太陽", id="10"),
        p(
            "ciudaddelasartesylasciencias",
            "ciudaddelasartesylasciencias",
            id="does not convert to non-encodeable characters",
        ),
    ],
)
def test_decode_data(data, expected):
    assert decode_data(data) == expected


@pytest.mark.parametrize(
    "raw_tags,cleaned",
    [
        p(
            [("musée", "provider", None), ("mus\\u00e9e", "provider", None)],
            [("musée", "provider", None)],
            id="correctly-encoded duplicate tag is retained",
        ),
        p(
            [("cat", "provider1", None), ("cat", "provider2", None)],
            [("cat", "provider1", None), ("cat", "provider2", None)],
            id="does not deduplicate tags with different providers",
        ),
        p(
            [("cat", "provider", None), ("cat", "clarifai", 0.9)],
            [("cat", "provider", None), ("cat", "clarifai", 0.9)],
            id="does not deduplicate tags with different accuracies and providers",
        ),
        p(
            [("ciudaddelasartesylasciencias", "provider", None)],
            [("ciudaddelasartesylasciencias", "provider", None)],
            id="does not decode non-encodable characters",
        ),
    ],
)
def test_clean_tags(raw_tags, cleaned):
    def tuple_to_tags(x):
        return [{"name": tag[0], "provider": tag[1], "accuracy": tag[2]} for tag in x]

    tags = tuple_to_tags(raw_tags)

    cleaned_tags = clean_tags(tags)
    assert cleaned_tags == tuple_to_tags(cleaned)
