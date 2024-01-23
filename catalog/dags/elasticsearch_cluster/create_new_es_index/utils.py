def merge_configurations(base_configuration, update_configuration):
    """
    Return a new dictionary which is the result of merging the given
    update_configuration dictionary into the base_configuration dictionary,
    according to the following merge policy:

    A leaf key in the `update_configuration` overwrites the entire value
    present in the `base_configuration` at that key. This is a naive
    overwrite, such that a list value for example is completely
    overwritten rather than appended to. For example:

    merge_configurations(
        base_configuration={
            "parent_key": {
                "leaf_key": ["value1", "value2"]
            },
            "other_key": True,
        },
        update_configuration={
            "parent_key": {
                "leaf_key": ["value3",]
            },
        }
    )

    will return:

    {
        "parent_key": {
            "leaf_key": ["value3",]
        },
        "other_key": True
    }
    """
    merge_configuration = base_configuration.copy()
    for key, val in update_configuration.items():
        if (
            # The key is not present in the base configuration, so
            # we are adding a new value rather than updating an existing
            # one and can simply add it.
            key not in base_configuration
            or
            # This is a leaf node.
            not isinstance(val, dict)
        ):
            merge_configuration[key] = val
        else:
            # Recurse down to the leaf nodes.
            merge_configuration[key] = merge_configurations(
                base_configuration[key], update_configuration[key]
            )

    return merge_configuration
