from collections.abc import Iterable


def make_comma_separated_help_text(items: Iterable[str], name: str) -> str:
    """
    Generate help text that describes a comma separated list of items with the name
    provided. Items are wrapped in backticks, and lists with more than one item will
    have an "and" added before the final item.

    :param items: iterable of available options for this field
    :param name: plural name of the list of items (e.g. "categories", "aspect ratios")
    :return: generated help text
    """
    formatted = [f"`{item}`" for item in sorted(items)]
    # Add an "and" at the end of the list
    if len(formatted) > 1:
        formatted[-1] = f"and {formatted[-1]}"
    help_text = (
        f"A comma separated list of {name}; available {name} include: "
        f"{', '.join(formatted)}."
    )
    return help_text
