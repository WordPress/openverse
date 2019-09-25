
from typing import List
from django_redis import get_redis_connection
from deepdiff import DeepHash
from elasticsearch_dsl import Search

# 3 hours minutes (in seconds)
DEAD_LINK_MASK_TTL = 60 * 60 * 3


def get_query_hash(s: Search) -> str:
    """
    Generates a deterministic Murmur3 or SHA256 hash from the serialized Search
    object using DeepHash so that two Search objects with the same content will
    produce the same hash.

    :param s: Search object to be serialized and hashed.
    :return: Serialized Search object hash.
    """
    serialized_search_obj = s.to_dict()
    serialized_search_obj.pop('from', None)
    serialized_search_obj.pop('size', None)
    deep_hash = DeepHash(serialized_search_obj)[serialized_search_obj]
    return deep_hash


def get_query_mask(query_hash: str) -> List[int]:
    """
    Fetches an existing query mask for a given query hash
    or returns an empty one.

    :param query_hash: Unique value for a particular query.
    :return: Boolean mask as a list of integers (0 or 1).
    """
    redis = get_redis_connection("default")
    key = f'{query_hash}:dead_link_mask'
    return list(map(int, redis.lrange(key, 0, -1)))


def save_query_mask(query_hash: str, mask: List):
    """
    Saves a query mask to redis.

    :param mask: Boolean mask as a list of integers (0 or 1).
    :param query_hash: Unique value to be used as key.
    """
    redis_pipe = get_redis_connection("default").pipeline()
    key = f'{query_hash}:dead_link_mask'

    redis_pipe.delete(key)
    redis_pipe.rpush(key, *mask)
    redis_pipe.expire(key, DEAD_LINK_MASK_TTL)
    redis_pipe.execute()
