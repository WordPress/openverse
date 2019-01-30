from rest_framework.throttling import AnonRateThrottle


class PostRequestThrottler(AnonRateThrottle):
    rate = '30/day'
