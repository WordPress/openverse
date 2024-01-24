import pytest

from elasticsearch_cluster.create_new_es_index.utils import merge_configurations


@pytest.mark.parametrize(
    "base_configuration, update_configuration, expected_merge_configuration",
    [
        # Update config includes keys not present in base config
        pytest.param(
            {"foo_key": "foo", "bar_key": "bar"},
            {"new_key": "new_val"},
            {"foo_key": "foo", "bar_key": "bar", "new_key": "new_val"},
            id="add_new_keys_to_base_config",
        ),
        # Nested leaf nodes
        pytest.param(
            {
                "grandparent_key": {
                    "parent_key": {"leaf_key": "foo", "other_leaf_key": "foobar"},
                    "other_key": "bar",
                },
                "other_top_key": "baz",
            },
            {"grandparent_key": {"parent_key": {"leaf_key": "new_leaf_val"}}},
            {
                "grandparent_key": {
                    "parent_key": {
                        "leaf_key": "new_leaf_val",
                        "other_leaf_key": "foobar",
                    },
                    "other_key": "bar",
                },
                "other_top_key": "baz",
            },
            id="update_nested_leaf_nodes",
        ),
        # Naively overwrite entire list values, rather than appending
        # to them
        pytest.param(
            {
                "parent_key": {"leaf_key": ["value1", "value2"]},
            },
            {
                "parent_key": {
                    "leaf_key": [
                        "value3",
                    ]
                },
            },
            {
                "parent_key": {
                    "leaf_key": [
                        "value3",
                    ]
                },
            },
            id="overwrite_list_values",
        ),
        pytest.param(
            {},
            {"foo": "bar", "parent": {"leaf": "baz"}},
            {"foo": "bar", "parent": {"leaf": "baz"}},
            id="empty_base_configuration",
        ),
        pytest.param(
            {"foo": "bar", "parent": {"leaf": "baz"}},
            {},
            {"foo": "bar", "parent": {"leaf": "baz"}},
            id="empty_update_configuration",
        ),
    ],
)
def test_merge_configurations(
    base_configuration, update_configuration, expected_merge_configuration
):
    actual_merge_configuration = merge_configurations(
        base_configuration, update_configuration
    )

    assert actual_merge_configuration == expected_merge_configuration
