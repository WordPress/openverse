from rest_framework.throttling import AnonRateThrottle


class PostRequestThrottler(AnonRateThrottle):
    rate = '30/day'


class BurstRateThrottle(AnonRateThrottle):
    scope = 'burst'


class SustainedRateThrottle(AnonRateThrottle):
    scope = 'sustained'


class ThreePerDay(AnonRateThrottle):
    rate = '3/day'
