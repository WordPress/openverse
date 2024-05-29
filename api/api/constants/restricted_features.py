import typing
from dataclasses import dataclass

from rest_framework.request import Request


ANONYMOUS: typing.Literal["anonymous"] = "anonymous"
AUTHENTICATED: typing.Literal["authenticated"] = "authenticated"
PRIVILEGED: typing.Literal["privileged"] = "privileged"

AccessLevel = typing.Literal[ANONYMOUS, AUTHENTICATED, PRIVILEGED]
ACCESS_LEVELS = typing.get_args(AccessLevel)


_RESTRICTED_FEATURES = {}

T = typing.TypeVar("T")


@dataclass
class RestrictedFeature(typing.Generic[T]):
    """
    Feature with gradient levels of access granted to applications upon approved request to Openverse maintainers.

    Maintainers review requests for increased access to restricted features on a per-case basis.

    Distinct from ``rate_limit_model`` which only affects access rates rather than level of access to certain features.
    """

    slug: str
    anonymous: T
    authenticated: T
    privileged: T

    def __post_init__(self):
        _RESTRICTED_FEATURES[self.slug] = self

    def request_level(self, request: None | Request) -> tuple[AccessLevel, T]:
        """Retrieve the level of any request in relation to the privilege."""
        if request is None or request.auth is None:
            return ANONYMOUS, self.anonymous

        if self.slug in request.auth.application.privileges:
            return PRIVILEGED, self.privileged

        return AUTHENTICATED, self.authenticated

    @classmethod
    @property
    def choices(cls):
        return ((slug,) * 2 for slug in _RESTRICTED_FEATURES)


MAX_PAGE_SIZE: RestrictedFeature[int] = RestrictedFeature(
    "max_page_size",
    anonymous=20,
    authenticated=50,
    # Max out privileged page size at the maximum authenticated
    # pagination depth, otherwise privileged page size limit can
    # contradict pagination depth limit.
    privileged=240,
)

MAX_RESULT_COUNT: RestrictedFeature[int] = RestrictedFeature(
    "max_result_count",
    # 12 pages of 20 results
    # Both anon and authed are limited to the same depth
    # authed users can request bigger pages, but still only the same
    # overall number of results available
    anonymous=12 * MAX_PAGE_SIZE.anonymous,
    authenticated=12 * MAX_PAGE_SIZE.anonymous,
    # 20 pages of maxed out page sizes for privileged apps
    privileged=20 * MAX_PAGE_SIZE.privileged,
)
