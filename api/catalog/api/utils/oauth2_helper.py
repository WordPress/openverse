import datetime as dt
import logging

from oauth2_provider.models import AccessToken

from catalog.api import models


parent_logger = logging.getLogger(__name__)


def get_token_info(token: str):
    """
    Recover an OAuth2 application client ID and rate limit model from an access
    token.

    :param token: An OAuth2 access token.
    :return: If the token is valid, return the client ID associated with the
    token, rate limit model, and email verification status as a tuple; else
    return (None, None, None).
    """
    logger = parent_logger.getChild("get_token_info")
    try:
        token = AccessToken.objects.get(token=token)
    except AccessToken.DoesNotExist:
        return None, None, None
    if token.expires >= dt.datetime.now(token.expires.tzinfo):
        try:
            application = models.ThrottledApplication.objects.get(accesstoken=token)
            client_id = str(application.client_id)
            rate_limit_model = application.rate_limit_model
            verified = application.verified
        except models.ThrottledApplication.DoesNotExist:
            logger.warning("Failed to find application associated with access token.")
            client_id = None
            rate_limit_model = None
            verified = None
        return client_id, rate_limit_model, verified
    else:
        logger.warning("Rejected expired access token.")
        return None, None, None
