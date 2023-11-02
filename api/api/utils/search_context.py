from dataclasses import asdict, dataclass
from typing import Self

from django.conf import settings

from elasticsearch_dsl import Q, Search

from api.constants.media_types import OriginIndex
from api.controllers.elasticsearch.helpers import get_es_response


@dataclass
class SearchContext:
    # Note: These sets use "identifiers" very explicitly
    # to convey that it is the Openverse result identifier and
    # not the document _id

    all_result_identifiers: list[str]
    """All the result identifiers gathered for the search."""

    sensitive_text_result_identifiers: set[str]
    """Subset of result identifiers for results with sensitive textual content."""

    @classmethod
    def build(
        cls, all_result_identifiers: list[str], origin_index: OriginIndex
    ) -> Self:
        if not all_result_identifiers:
            return cls(list(), set())

        if not settings.ENABLE_FILTERED_INDEX_QUERIES:
            return cls(all_result_identifiers, set())

        filtered_index_search = Search(index=f"{origin_index}-filtered")
        filtered_index_search = filtered_index_search.query(
            # Use `identifier` rather than the document `id` due to
            # `id` instability between refreshes:
            # https://github.com/WordPress/openverse/issues/2306
            Q("terms", identifier=all_result_identifiers)
        )

        # The default query size is 10, so we need to slice the query
        # to change the size to be big enough to encompass all the
        # results.
        filtered_index_slice = filtered_index_search[: len(all_result_identifiers)]
        results_in_filtered_index = get_es_response(
            filtered_index_slice, "filtered_index_context"
        )
        filtered_index_identifiers = {
            result.identifier for result in results_in_filtered_index
        }
        sensitive_text_result_identifiers = {
            identifier
            for identifier in all_result_identifiers
            if identifier not in filtered_index_identifiers
        }

        return cls(
            all_result_identifiers=all_result_identifiers,
            sensitive_text_result_identifiers=sensitive_text_result_identifiers,
        )

    def asdict(self):
        """
        Cast the object to a dict.

        This is a convenience method to avoid leaking dataclass
        implementation details elsewhere in the code.
        """
        return asdict(self)
