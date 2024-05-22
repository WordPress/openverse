from django.db import models

from oauth2_provider.models import AbstractApplication


class OAuth2Registration(models.Model):
    """Information about API key applicants."""

    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="A unique human-readable name for your application or "
        "project requiring access to the Openverse API.",
    )
    description = models.CharField(
        max_length=10000,
        help_text="A description of what you are trying to achieve with your "
        "project using the API. Please provide as much detail as "
        "possible!",
    )
    email = models.EmailField(
        help_text="A valid email that we can reach you at if we have any "
        "questions about your use case or data consumption."
    )


class ThrottledApplication(AbstractApplication):
    """An OAuth2 application with adjustable rate limits."""

    RATE_LIMIT_MODELS = [
        ("standard", "standard"),  # Default rate limit for all API keys.
        ("enhanced", "enhanced"),  # Rate limits for "super" keys, granted on a
        # case-by-case basis.
        ("exempt", "exempt"),  # Rate limits used for internal infrastructure to
        # by-pass rate limiting entirely.
    ]
    rate_limit_model = models.CharField(
        max_length=20, choices=RATE_LIMIT_MODELS, default="standard"
    )
    verified = models.BooleanField(default=False)
    revoked = models.BooleanField(default=False)


class OAuth2Verification(models.Model):
    """
    An email verification code sent by noreply-catalog.

    After verification occurs, the entry should be deleted.
    """

    associated_application = models.ForeignKey(
        ThrottledApplication, on_delete=models.CASCADE
    )
    email = models.EmailField()
    code = models.CharField(max_length=256, db_index=True)
