from dataclasses import asdict, dataclass
from typing import Self

from django.conf import settings

from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.response import Hit

from api.constants.media_types import OriginIndex


@dataclass
class SearchContext:
    # Note: These sets use "identifiers" very explicitly
    # to convey that it is the Openverse result identifier and
    # not the document _id

    all_result_identifiers: set[str]
    """All the result identifiers gathered for the search."""

    sensitive_text_result_identifiers: set[str]
    """Subset of result identifiers for results with sensitive textual content."""

    @classmethod
    def build(cls, results: list[Hit], origin_index: OriginIndex) -> Self:
        if not results:
            return cls(set(), set())

        all_result_identifiers = {r.identifier for r in results}

        if not settings.ENABLE_FILTERED_INDEX_QUERIES:
            return cls(all_result_identifiers, set())

        filtered_index_search = Search(index=f"{origin_index}-filtered")
        filtered_index_search = filtered_index_search.query(
            # Use `identifier` rather than the document `id` due to
            # `id` instability between refreshes:
            # https://github.com/WordPress/openverse/issues/2306
            # `identifier` is mapped as `text` which will match fuzzily.
            # Use `identifier.keyword` to match _exactly_
            # cf: https://github.com/WordPress/openverse/issues/2154
            Q(
                "terms",
                **{"identifier.keyword": [result.identifier for result in results]},
            )
        )

        # The default query size is 10, so we need to slice the query
        # to change the size to be big enough to encompass all the
        # results.
        results_in_filtered_index = filtered_index_search[: len(results)].execute()
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
