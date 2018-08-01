from rest_framework.throttling import UserRateThrottle


class PostRequestThrottler(UserRateThrottle):
    rate = '30/day'