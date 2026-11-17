import sentry_sdk
from decouple import config
from psycopg_pool import PoolTimeout
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

from api.utils.sentry import make_sensitive_value_scrubber
from conf.settings.base import ENVIRONMENT
from conf.settings.databases import DATABASES
from conf.settings.security import DEBUG


SENTRY_DSN = config("SENTRY_DSN", default="")

SENTRY_TRACES_SAMPLE_RATE: float = config(
    "SENTRY_TRACES_SAMPLE_RATE", default=0, cast=float
)
SENTRY_PROFILES_SAMPLE_RATE: float = config(
    "SENTRY_PROFILES_SAMPLE_RATE", default=0, cast=float
)


def profiles_sampler(sampling_context) -> float:
    """
    Control the performance profile sampling.
    See https://docs.sentry.io/platforms/python/profiling/

    Returns a float between 0.0 and 1.0.
    """
    url_path = sampling_context.get("url.path", "")

    if "healthcheck" in url_path:
        return 0.0  # Exclude the health check URL from profiling

    # All the other instances
    return SENTRY_PROFILES_SAMPLE_RATE


def _is_pool_timeout(exc: BaseException | None) -> bool:
    # Django wraps the pool's ``PoolTimeout`` in its own ``OperationalError``,
    # so the type to match is somewhere down the exception chain.
    seen = set()
    while exc is not None and id(exc) not in seen:
        if isinstance(exc, PoolTimeout):
            return True
        seen.add(id(exc))
        exc = exc.__cause__ or exc.__context__
    return False


# Redact infrastructure hostnames (e.g. the database DNS name) that can leak
# into events as free text, where key-based scrubbing never sees them.
scrub_sensitive_values = make_sensitive_value_scrubber([DATABASES["default"]["HOST"]])


def before_send(event, hint):
    """
    Drop events that only report infrastructure noise.

    - DB connection pool timeouts: the pool is saturated and the request can
      only be retried; there is nothing to fix at the call site.
    - uvloop's "Fatal error on SSL protocol" log: the remote end of an outbound
      HTTPS request closed the connection. The request itself succeeds, but
      asyncio logs this at ERROR, which ``SentryProcessor`` turns into an event.

    Events that are kept have sensitive values scrubbed from them.
    """
    exc_info = hint.get("exc_info")
    if exc_info and _is_pool_timeout(exc_info[1]):
        return None

    message = event.get("message") or ""
    if event.get("logger") == "asyncio" and message.startswith(
        "Fatal error on SSL protocol"
    ):
        return None

    return scrub_sensitive_values(event, hint)


INTEGRATIONS = [
    # See https://docs.sentry.io/platforms/python/integrations/django/
    DjangoIntegration(),
    # This prevents two errors from being sent to Sentry (one with the correct
    # information and the other with the logged JSON as the error name), since we
    # use JSON-logging as well which can conflict with the way Sentry expects alerts.
    # https://github.com/kiwicom/structlog-sentry?tab=readme-ov-file#logging-as-json
    LoggingIntegration(event_level=None, level=None),
]

if not DEBUG and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=INTEGRATIONS,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sampler=profiles_sampler,
        before_send=before_send,
        send_default_pii=False,
        environment=ENVIRONMENT,
        before_send_transaction=scrub_sensitive_values,
    )

    # ALLOW_HOSTS is correctly configured so ignore this to prevent
    # spammy bots like https://github.com/robertdavidgraham/masscan
    # from pushing un-actionable alerts to Sentry like
    # https://sentry.io/share/issue/9af3cdf8ef74420aa7bbb6697760a82c/
    ignore_logger("django.security.DisallowedHost")
    # ``django-structlog`` writes ERROR logs when a response has a 5xx response
    # code, which can be registered by Sentry and obscure the underlying reason
    # why 5xx response was returned in the first place.
    ignore_logger("django_structlog.middlewares.request")
    # These errors can occur in large volumes and so we don't want them to fill
    # up in Sentry and overwhelm us with Slack notifications.
    ignore_logger("api.utils.check_dead_links._head")
