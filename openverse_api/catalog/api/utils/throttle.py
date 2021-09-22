from rest_framework.throttling import SimpleRateThrottle
import logging
from catalog.api.utils.oauth2_helper import get_token_info
from django_redis import get_redis_connection

log = logging.getLogger(__name__)


def _from_internal_network(ip):
    redis = get_redis_connection('default')
    return redis.sismember('ip-whitelist', ip)


class AnonRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a anonymous users.

    The IP address of the request will be used as the unique cache key.
    """
    scope = 'anon'

    def get_cache_key(self, request, view):
        if _from_internal_network(self.get_ident(request)):
            return None
        # Do not throttle requests with a valid access token.
        if request.auth:
            client_id, _, verified = get_token_info(str(request.auth))
            if client_id and verified:
                return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class PostRequestThrottler(AnonRateThrottle):
    rate = '30/day'


class BurstRateThrottle(AnonRateThrottle):
    scope = 'anon_burst'


class SustainedRateThrottle(AnonRateThrottle):
    scope = 'anon_sustained'


class TenPerDay(AnonRateThrottle):
    rate = '10/day'


class OneThousandPerMinute(AnonRateThrottle):
    rate = '1000/min'


class OnePerSecond(AnonRateThrottle):
    rate = '1/second'


class OAuth2IdThrottleRate(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a given user's Oauth2
    client ID. Can be configured to apply to either standard or enhanced
    API keys.
    """
    scope = 'oauth2_client_credentials'
    applies_to_rate_limit_model = 'standard'

    def get_cache_key(self, request, view):
        if _from_internal_network(self.get_ident(request)):
            return None
        # Find the client ID associated with the access token.
        auth = str(request.auth)
        client_id, rate_limit_model, verified = get_token_info(auth)
        if client_id and rate_limit_model == self.applies_to_rate_limit_model:
            ident = client_id
        else:
            # Don't throttle invalid tokens; leave that to the anonymous
            # throttlers. Don't throttle enhanced rate limit tokens either.
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class OAuth2IdThrottleSustainedRate(OAuth2IdThrottleRate):
    applies_to_rate_limit_model = 'standard'
    scope = 'oauth2_client_credentials_sustained'


class OAuth2IdThrottleBurstRate(OAuth2IdThrottleRate):
    applies_to_rate_limit_model = 'standard'
    scope = 'oauth2_client_credentials_burst'


class EnhancedOAuth2IdThrottleSustainedRate(OAuth2IdThrottleRate):
    applies_to_rate_limit_model = 'enhanced'
    scope = 'enhanced_oauth2_client_credentials_sustained'


class EnhancedOAuth2IdThrottleBurstRate(OAuth2IdThrottleRate):
    applies_to_rate_limit_model = 'enhanced'
    scope = 'enhanced_oauth2_client_credentials_burst'
