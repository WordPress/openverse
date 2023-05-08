from dataclasses import asdict, dataclass
from typing import Self

from django.db.models import CharField
from django.db.models.functions import Cast

from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.response import Hit

from api import models
from api.constants.media_types import OriginIndex


@dataclass
class SearchContext:
    all_result_identifiers: set[str]
    """All the result identifiers gathered for the search."""

    user_reported_sensitive_result_identifiers: set[str]
    """Subset of result identifiers for results with confirmed sensitive reports."""

    sensitive_text_result_identifiers: set[str]
    """Subset of result identifiers for results with sensitive textual content."""

    @classmethod
    def get_mature_media_class_for_index(
        cls, origin_index: OriginIndex
    ) -> models.MatureImage | models.MatureAudio:
        match origin_index:
            case "image":
                return models.MatureImage
            case "audio":
                return models.MatureAudio
            case _:
                raise ValueError(f"Unknown `origin_index` value '{origin_index}'")

    @classmethod
    def build(cls, results: list[Hit], origin_index: OriginIndex) -> Self:
        if not results:
            return cls(set(), set(), set())

        all_result_identifiers = {r.identifier for r in results}

        filtered_index_search = Search(index=f"{origin_index}-filtered")
        filtered_index_search = filtered_index_search.query(
            Q("terms", id=[result.id for result in results])
        )

        results_in_filtered_index = filtered_index_search.execute()
        filtered_index_identifiers = {
            result.identifier for result in results_in_filtered_index
        }
        sensitive_text_result_identifiers = {
            identifier
            for identifier in all_result_identifiers
            if identifier not in filtered_index_identifiers
        }

        mature_media_class = cls.get_mature_media_class_for_index(origin_index)

        user_reported_sensitive_result_identifiers = set(
            mature_media_class.objects
            # ``identifier`` comes back as a UUID by default, so it needs to be
            # cast to string to match the interface of the sets expected
            # by ``SearchContext``
            .annotate(identifier_string=Cast("media_obj_id", output_field=CharField()))
            .filter(media_obj_id__in=list(all_result_identifiers))
            .values_list("identifier_string", flat=True)
        )

        return cls(
            all_result_identifiers=all_result_identifiers,
            sensitive_text_result_identifiers=sensitive_text_result_identifiers,
            user_reported_sensitive_result_identifiers=user_reported_sensitive_result_identifiers,
        )

    def asdict(self):
        return asdict(self)
