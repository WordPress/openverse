import datetime as dt
import logging
from dataclasses import dataclass

from oauth2_provider.models import AccessToken

from api import models


parent_logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Extracted ``models.ThrottledApplication`` metadata."""

    client_id: str
    rate_limit_model: str
    verified: bool
    application_name: str

    @property
    def valid(self):
        return self.client_id and self.verified


def get_token_info(token: str) -> None | TokenInfo:
    """
    Recover an OAuth2 application client ID and rate limit model from an access token.

    :param token: An OAuth2 access token.
    :return: If the token is valid, return the client ID associated with the
    token, rate limit model, and email verification status as a tuple; else
    return ``(None, None, None)``.
    """
    logger = parent_logger.getChild("get_token_info")
    try:
        token = AccessToken.objects.get(token=token)
    except AccessToken.DoesNotExist:
        return None

    try:
        application = models.ThrottledApplication.objects.get(accesstoken=token)
    except models.ThrottledApplication.DoesNotExist:
        # Critical because it indicates a data integrity problem.
        # In practice should never occur so long as the preceding
        # operation to retrieve the access token was successful.
        logger.critical("Failed to find application associated with access token.")
        return None

    expired = token.expires < dt.datetime.now(token.expires.tzinfo)
    if expired:
        logger.info(
            "rejected expired access token "
            f"application.name={application.name} "
            f"application.client_id={application.client_id} "
        )
        return None

    return TokenInfo(
        client_id=str(application.client_id),
        rate_limit_model=application.rate_limit_model,
        verified=application.verified,
        application_name=application.name,
    )
