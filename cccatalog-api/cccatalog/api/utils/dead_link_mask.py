
from typing import List
from django_redis import get_redis_connection

# 3 hours minutes (in seconds)
DEAD_LINK_MASK_TTL = 60 * 60 * 3


def get_query_mask(query_hash: str) -> List[int]:
    '''
    Fetches an existing query mask for a given query hash
    or returns an empty one.

    :param query_hash: Unique value for a particular query.
    :return: Boolean mask as a list of integers (0,1).
    '''
    redis = get_redis_connection("default")
    key = f'{query_hash}:dead_link_mask'
    return list(map(int, redis.lrange(key, 0, -1)))


def save_query_mask(query_hash: str, mask: List):
    '''
    Saves a query mask to redis.

    :param query_hash: Unique value to be used as key.
    '''
    redis_pipe = get_redis_connection("default").pipeline()
    key = f'{query_hash}:dead_link_mask'

    redis_pipe.delete(key)
    redis_pipe.rpush(key, *mask)
    redis_pipe.expire(key, DEAD_LINK_MASK_TTL)
    redis_pipe.execute()
