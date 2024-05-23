import typing
from dataclasses import dataclass

from rest_framework.request import Request


ANONYMOUS: typing.Literal["anonymous"] = "anonymous"
AUTHENTICATED: typing.Literal["authenticated"] = "authenticated"
PRIVILEGED: typing.Literal["privileged"] = "privileged"

Level = typing.Literal[ANONYMOUS, AUTHENTICATED, PRIVILEGED]
LEVELS = typing.get_args(Level)


_PRIVILEGES = {}


@dataclass
class Privilege:
    """
    Privileges granted to applications upon approved request to Openverse maintainers.

    Maintainers review requests for increased privileges on a per-case basis.

    Distinct from ``rate_limit_model`` which only affects access rates rather than privileges.
    """

    slug: str
    anonymous: typing.Any
    authenticated: typing.Any
    privileged: typing.Any

    def __post_init__(self):
        _PRIVILEGES[self.slug] = self

    def request_level(self, request: None | Request) -> tuple[Level, typing.Any]:
        """Retrieve the level of any request in relation to the privilege."""
        if request is None or request.auth is None:
            return ANONYMOUS, self.anonymous

        if self.slug in request.auth.application.privileges:
            return PRIVILEGED, self.privileged

        return AUTHENTICATED, self.authenticated

    @classmethod
    @property
    def choices(cls):
        return ((slug,) * 2 for slug in _PRIVILEGES)


PAGE_SIZE = Privilege(
    "page_size",
    anonymous=20,
    authenticated=50,
    # Max out privileged page size at the maximum authenticated
    # pagination depth, otherwise privileged page size limit can
    # contradict pagination depth limit.
    privileged=240,
)

PAGINATION_DEPTH = Privilege(
    "pagination_depth",
    # 12 pages of 20 results
    # Both anon and authed are limited to the same depth
    # authed users can request bigger pages, but still only the same
    # overall number of results available
    anonymous=12 * PAGE_SIZE.anonymous,
    authenticated=12 * PAGE_SIZE.anonymous,
    # 20 pages of maxed out page sizes for privileged apps
    privileged=20 * PAGE_SIZE.privileged,
)
