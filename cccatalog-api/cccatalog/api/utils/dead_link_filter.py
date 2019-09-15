
from typing import List
from django_redis import get_redis_connection


def get_query_mask(query_hash: str) -> List[int]:
    '''
    '''
    redis = get_redis_connection("default")
    key = f'{query_hash}:dead_link_filter'
    return list(map(int, redis.lrange(key, 0, -1)))


def save_new_query_mask(query_hash: str, mask: List):
    '''
    '''
    redis = get_redis_connection("default")
    key = f'{query_hash}:dead_link_filter'
    redis.delete(key)
    redis.rpush(key, *mask)
