from rest_framework.throttling import SimpleRateThrottle
from oauth2_provider.models import AccessToken, Application
import datetime as dt
import logging

log = logging.getLogger(__name__)


def _validate_access_token(token: str):
    """
    Recover an OAuth2 application client ID from an access token.

    :param token: An OAuth2 access token.
    :return: If the token is valid, return the client ID associated with the
    token; else return None
    """
    try:
        token = AccessToken.objects.get(token=token)
    except AccessToken.DoesNotExist:
        log.warning('Rejected nonexistent access token.')
        return None
    if token.expires >= dt.datetime.now(token.expires.tzinfo):
        try:
            client_id = str(
                Application.objects.get(accesstoken=token).client_id
            )
        except Application.DoesNotExist:
            log.warning('Failed to find application associated with token.')
            client_id = None
        return client_id
    else:
        log.warning('Rejected expired access token.')
        return None


class AnonRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a anonymous users.

    The IP address of the request will be used as the unique cache key.
    """
    scope = 'anon'

    def get_cache_key(self, request, view):
        # Do not throttle requests with a valid access token.
        if request.auth:
            if _validate_access_token(str(request.auth)):
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


class OAuth2IdRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a given user's access
    token.

    The OAuth2 application ID will be used as a unique cache key if the token
    is valid.  For anonymous requests, the IP address of the request will
    be used.
    """
    scope = 'oauth2_client_credentials'

    def get_cache_key(self, request, view):
        # Find the
        client_id = _validate_access_token(str(request.auth))
        if client_id:
            ident = client_id
        else:
            # Don't throttle invalid tokens; leave that to the anonymous
            # throttlers.
            return None

        #from remote_pdb import RemotePdb
        #RemotePdb('0.0.0.0', 4444).set_trace()
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class OAuth2IdRateThrottleSustained(OAuth2IdRateThrottle):
    scope = 'oauth2_client_credentials_sustained'


class OAuth2IdRateThrottleBurst(OAuth2IdRateThrottle):
    scope = 'oauth2_client_credentials_burst'
