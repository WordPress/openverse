from rest_framework.throttling import SimpleRateThrottle
import logging
from cccatalog.settings import TRUSTED_NETWORK
from cccatalog.api.utils.oauth2_helper import get_token_info

log = logging.getLogger(__name__)


def _from_internal_network(ip):
    return ip.startswith(TRUSTED_NETWORK)


class AnonRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a anonymous users.

    The IP address of the request will be used as the unique cache key.
    """
    scope = 'anon'

    def get_cache_key(self, request, view):
        if _from_internal_network:
            return None
        # Do not throttle requests with a valid access token.
        if request.auth:
            client_id, _ = get_token_info(str(request.auth))
            if client_id:
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


class ThreePerDay(AnonRateThrottle):
    rate = '3/day'


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
        if _from_internal_network:
            return None
        # Find the client ID associated with the access token.
        client_id, rate_limit_model = get_token_info(str(request.auth))
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
