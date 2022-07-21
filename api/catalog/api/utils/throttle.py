import abc
import logging

from rest_framework.throttling import SimpleRateThrottle

from django_redis import get_redis_connection

from catalog.api.utils.oauth2_helper import get_token_info


parent_logger = logging.getLogger(__name__)


class AbstractAnonRateThrottle(SimpleRateThrottle, metaclass=abc.ABCMeta):
    """
    Limits the rate of API calls that may be made by a anonymous users.

    The IP address of the request will be used as the unique cache key.
    """

    logger = parent_logger.getChild("AnonRateThrottle")

    def get_cache_key(self, request, view):
        logger = self.logger.getChild("get_cache_key")
        # Do not apply anonymous throttle to request with valid tokens.
        if request.auth:
            client_id, _, verified = get_token_info(str(request.auth))
            if client_id and verified:
                return None

        ident = self.get_ident(request)
        redis = get_redis_connection("default", write=False)
        if redis.sismember("ip-whitelist", ident):
            logger.info(f"bypassing rate limiting for ident={ident}")
            """
            Exempt internal IP addresses. Exists as a legacy holdover and usages of this
            should be replaced with the exempt API key as it is easier to manage via
            Django admin and doesn't require leaky permissions in our production infra.
            """
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class BurstRateThrottle(AbstractAnonRateThrottle):
    scope = "anon_burst"


class SustainedRateThrottle(AbstractAnonRateThrottle):
    scope = "anon_sustained"


class TenPerDay(AbstractAnonRateThrottle):
    rate = "10/day"


class OneThousandPerMinute(AbstractAnonRateThrottle):
    rate = "1000/min"


class OnePerSecond(AbstractAnonRateThrottle):
    rate = "1/second"


class AbstractOAuth2IdRateThrottle(SimpleRateThrottle, metaclass=abc.ABCMeta):
    """
    Ties a particular configured throttling scope from ``settings.py`` to
    a "rate limit model". See ``ThrottledApplication.rate_limit_model``
    for an explanation of that concept.
    """

    scope: str
    # The name of the scope. Used to retrieve the rate limit from settings.
    applies_to_rate_limit_model: str
    # The ``ThrottledApplication.rate_limit_model`` to which the scope applies.

    def get_cache_key(self, request, view):
        # Find the client ID associated with the access token.
        auth = str(request.auth)
        client_id, rate_limit_model, verified = get_token_info(auth)
        if client_id and rate_limit_model == self.applies_to_rate_limit_model:
            ident = client_id
        else:
            # Return None, fallback to the anonymous rate limiting
            return None

        return self.cache_format % {"scope": self.scope, "ident": ident}


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
