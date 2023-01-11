import logging
import os

from github import Github


log = logging.getLogger(__name__)


def get_client(is_authenticated: bool = True) -> Github:
    """
    Get a PyGithub client to access the GitHub API.

    The client can optionally be authenticated using the GITHUB_ACCESS_TOKEN
    from the environment variables.

    :param is_authenticated: whether to authenticate the client
    :return: the PyGithub client
    """

    log.info("Setting up GitHub client")
    if is_authenticated:
        access_token: str | None = os.getenv("ACCESS_TOKEN")
        if access_token is None:
            log.error("Access token was not found in env.ACCESS_TOKEN.")
            raise ValueError("Access token not found")
    else:
        log.debug("Generating a non-authenticated client")
        access_token = None

    client: Github = Github(access_token)
    return client
