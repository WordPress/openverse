RELEVANCE = "relevance"
INDEXED_ON = "indexed_on"
SORT_FIELDS = [
    (RELEVANCE, "Relevance"),  # default
    (INDEXED_ON, "Indexing date"),  # date on which media was indexed into Openverse
]
DEFAULT_SORT_FIELD = RELEVANCE

DESCENDING = "desc"
ASCENDING = "asc"
SORT_DIRECTIONS = [
    (DESCENDING, "Descending"),  # default
    (ASCENDING, "Ascending"),
]
DEFAULT_SORT_DIRECTION = DESCENDING
