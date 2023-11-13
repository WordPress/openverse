from __future__ import annotations

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Q, Term
from elasticsearch_dsl.response import Hit

from api.controllers.elasticsearch.helpers import get_es_response, get_query_slice
from api.controllers.search_controller import (
    _post_process_results,
    get_excluded_providers_query,
)


def related_media(uuid: str, index: str, filter_dead: bool) -> list[Hit]:
    """
    Given a UUID, finds 10 related search results based on title and tags.

    Uses Match query for title or SimpleQueryString for tags.
    If the item has no title and no tags, returns items by the same creator.
    If the item has no title, no tags or no creator, returns empty list.

    :param uuid: The UUID of the item to find related results for.
    :param index: The Elasticsearch index to search (e.g. 'image')
    :param filter_dead: Whether dead links should be removed.
    :return: List of related results.
    """

    # Search the default index for the item itself as it might be sensitive.
    item_search = Search(index=index)
    item_hit = item_search.query(Term(identifier=uuid)).execute().hits[0]

    # Match related using title.
    title = getattr(item_hit, "title", None)
    tags = getattr(item_hit, "tags", None)
    creator = getattr(item_hit, "creator", None)

    related_query = {"must_not": [], "must": [], "should": []}

    if not title and not tags:
        if not creator:
            return []
        else:
            # Only use `creator` query if there are no `title` and `tags`
            related_query["should"].append(Term(creator=creator))
    else:
        if title:
            related_query["should"].append(Match(title=title))

        # Match related using tags, if the item has any.
        # Only use the first 10 tags
        if tags:
            tags = [tag["name"] for tag in tags[:10]]
            related_query["should"].append(Q("terms", tags__name__keyword=tags))

    # Exclude the dynamically disabled sources.
    if excluded_providers_query := get_excluded_providers_query():
        related_query["must_not"].append(excluded_providers_query)
    # Exclude the current item and mature content.
    related_query["must_not"].extend(
        [Q("term", mature=True), Q("term", identifier=uuid)]
    )

    # Search the filtered index for related items.
    s = Search(index=f"{index}-filtered")
    s = s.query("bool", **related_query)

    page, page_size = 1, 10
    start, end = get_query_slice(s, page_size, page, filter_dead)
    s = s[start:end]

    response = get_es_response(s, es_query="related_media")
    results = _post_process_results(s, start, end, page_size, response, filter_dead)
    return results or []
