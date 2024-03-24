from django.conf import settings

from api.constants.parameters import TAG


CREATOR_COLLECTIONS_DISABLED = """
Search by creator only. Cannot be used with `q`. The search
is fuzzy, so `creator=john` will match any value that includes the
word `john`. If the value contains space, items that contain any of
the words in the value will match. To search for several values,
join them with a comma."""

CREATOR = """
_When `q` parameter is present, `creator` parameter is ignored._

**Creator collection**
When used with `collection=creator&source=sourceName`, returns the collection of media
by the specified creator. Notice that a single creator's media items
can be found on several sources, but this collection only returns the
items from the specified source.
This is why for this collection, both the creator and the source
parameters are required, and matched exactly. For a fuzzy creator search,
use the default search without the `collection` parameter.

**Creator search**
When used without the `collection` parameter, will search in the creator field only.
The search is fuzzy, so `creator=john` will match any value that includes the
word `john`. If the value contains space, items that contain any of
the words in the value will match. To search for several values,
join them with a comma.
"""

CREATOR_HELP_TEXT = (
    CREATOR if settings.SHOW_COLLECTION_DOCS else CREATOR_COLLECTIONS_DISABLED
)
COLLECTION_HELP_TEXT = f"""
The kind of media collection to return.

Should be used with `{TAG}`, `source` or `creator`+`source`"""

EXCLUDED_SOURCE_HELP_TEXT = """
A comma separated list of data sources to exclude from the search.
Valid values are `source_name`s from the stats endpoint: %(origin)s/v1/%(media_path)s/stats/.
"""
SOURCE_HELP_TEXT_COLLECTIONS_DISABLED = """
A comma separated list of data sources; valid values are
`source_name`s from the stats endpoint: %(origin)s/v1/%(media_path)s/stats/."""

SOURCE = """
For default search, a comma separated list of data sources.
When the `collection` parameter is used, this parameter only accepts a single source.

Valid values are `source_name`s from the stats endpoint: %(origin)s/v1/%(media_path)s/stats/.
"""

SOURCE_HELP_TEXT = (
    SOURCE if settings.SHOW_COLLECTION_DOCS else SOURCE_HELP_TEXT_COLLECTIONS_DISABLED
)

TAG_HELP_TEXT = """
_Must be used with `collection=tag`_

Get the collection of media with a specific tag. Returns the collection of media
that has the specified tag, matching exactly and entirely.

Differences that will cause tags to not match are:
- upper and lower case letters
- diacritical marks
- hyphenation
- spacing
- multi-word tags where the query is only one of the words in the tag
- multi-word tags where the words are in a different order.

Examples of tags that **do not** match:
- "Low-Quality" and "low-quality"
- "jalapeño" and "jalapeno"
- "Saint Pierre des Champs" and "Saint-Pierre-des-Champs"
- "dog walking" and "dog  walking" (where the latter has two spaces between the
last two words, as in a typographical error)
- "runner" and "marathon runner"
- "exclaiming loudly" and "loudly exclaiming"

For non-exact or multi-tag matching, using the `tags` query parameter.
"""
