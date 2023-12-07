import abc
import logging

from rest_framework.throttling import SimpleRateThrottle

from api.utils.oauth2_helper import get_token_info


parent_logger = logging.getLogger(__name__)


class SimpleRateThrottleHeader(SimpleRateThrottle, metaclass=abc.ABCMeta):
    """
    Extends the ``SimpleRateThrottle`` class to provide additional functionality such as
    rate-limit headers in the response.
    """

    def allow_request(self, request, view):
        is_allowed = super().allow_request(request, view)
        view.headers |= self.headers()
        return is_allowed

    def headers(self):
        """
        Get `X-RateLimit-` headers for this particular throttle. Each pair of headers
        contains the limit and the number of requests left in the limit. Since multiple
        rate limits can apply concurrently, the suffix identifies each pair uniquely.
        """
        prefix = "X-RateLimit"
        suffix = self.scope or self.__class__.__name__.lower()
        if hasattr(self, "history"):
            return {
                f"{prefix}-Limit-{suffix}": self.rate,
                f"{prefix}-Available-{suffix}": self.num_requests - len(self.history),
            }
        else:
            return {}


class AbstractAnonRateThrottle(SimpleRateThrottleHeader, metaclass=abc.ABCMeta):
    """
    Limits the rate of API calls that may be made by a anonymous users.

    The IP address of the request will be used as the unique cache key.
    """

    logger = parent_logger.getChild("AnonRateThrottle")

    def get_cache_key(self, request, view):
        self.logger.getChild("get_cache_key")
        # Do not apply anonymous throttle to request with valid tokens.
        if request.auth:
            token_info = get_token_info(str(request.auth))
            if token_info and token_info.valid:
                return None

        ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class BurstRateThrottle(AbstractAnonRateThrottle):
    scope = "anon_burst"


class SustainedRateThrottle(AbstractAnonRateThrottle):
    scope = "anon_sustained"


class HealthcheckAnonRateThrottle(AbstractAnonRateThrottle):
    scope = "anon_healthcheck"


class AnonThumbnailRateThrottle(AbstractAnonRateThrottle):
    scope = "anon_thumbnail"


class TenPerDay(AbstractAnonRateThrottle):
    rate = "10/day"


class OnePerSecond(AbstractAnonRateThrottle):
    rate = "1/second"


class AbstractOAuth2IdRateThrottle(SimpleRateThrottleHeader, metaclass=abc.ABCMeta):
    """
    Ties a particular throttling scope from ``settings.py`` to a rate limit model.

    See ``ThrottledApplication.rate_limit_model`` for an explanation of that concept.
    """

    scope: str
    # The name of the scope. Used to retrieve the rate limit from settings.
    applies_to_rate_limit_model: str
    # The ``ThrottledApplication.rate_limit_model`` to which the scope applies.

    def get_cache_key(self, request, view):
        # Find the client ID associated with the access token.
        auth = str(request.auth)
        token_info = get_token_info(auth)
        if not (token_info and token_info.valid):
            return None

        if token_info.rate_limit_model != self.applies_to_rate_limit_model:
            return None

        return self.cache_format % {"scope": self.scope, "ident": token_info.client_id}


class OAuth2IdThumbnailRateThrottle(AbstractOAuth2IdRateThrottle):
    applies_to_rate_limit_model = "standard"
    scope = "oauth2_client_credentials_thumbnail"


class OAuth2IdSustainedRateThrottle(AbstractOAuth2IdRateThrottle):
    applies_to_rate_limit_model = "standard"
    scope = "oauth2_client_credentials_sustained"


class OAuth2IdBurstRateThrottle(AbstractOAuth2IdRateThrottle):
    applies_to_rate_limit_model = "standard"
    scope = "oauth2_client_credentials_burst"


class EnhancedOAuth2IdSustainedRateThrottle(AbstractOAuth2IdRateThrottle):
    applies_to_rate_limit_model = "enhanced"
    scope = "enhanced_oauth2_client_credentials_sustained"


class EnhancedOAuth2IdBurstRateThrottle(AbstractOAuth2IdRateThrottle):
    applies_to_rate_limit_model = "enhanced"
    scope = "enhanced_oauth2_client_credentials_burst"


class ExemptOAuth2IdRateThrottle(AbstractOAuth2IdRateThrottle):
    applies_to_rate_limit_model = "exempt"
    scope = "exempt_oauth2_client_credentials"
