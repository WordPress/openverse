import argparse
import datetime
import logging
import sys
from collections import namedtuple

from github import Github, Issue, GithubException
from github.PullRequest import PullRequest

from shared.data import get_data
from shared.github import get_client
from shared.log import configure_logger
from shared.project import get_org_project, get_project_column

log = logging.getLogger(__name__)

EntityInfo = namedtuple("EntityInfo", ["display_name", "content_type"])
ENTITY_INFO = {
    "pr": EntityInfo("PR", "PullRequest"),
    "issue": EntityInfo("issue", "Issue"),
}

# region argparse
parser = argparse.ArgumentParser(
    description="Move issues to the correct columns in projects",
)
parser.add_argument(
    "--entity-type",
    dest="entity_type",
    metavar="entity-type",
    type=str,
    required=True,
    choices=["issue", "pr"],
    help="the type of entity to add to the project",
)
parser.add_argument(
    "--project-number",
    dest="proj_number",
    metavar="project-number",
    type=int,
    required=True,
    help="the project in which to add new cards with the entity",
)
parser.add_argument(
    "--target-column",
    dest="target_col_name",
    metavar="target-column",
    type=str,
    default="Backlog",
    help="column in which to add new cards with the entity",
)
parser.add_argument(
    "--period",
    type=int,  # minutes
    default=60,
    help="time period in minutes within which to check for new issues",
)


# endregion


def get_new_issues(
    gh: Github,
    org_handle: str,
    repo_names: list[str],
    ent_type: str,
    since: datetime.datetime,
) -> list[Issue]:
    """
    From given repos in the given organization, retrieve a list of open issues
    that were created after the specified time. This includes PRs.

    :param gh: the GitHub client
    :param org_handle: the name of the org in which to look for issues
    :param repo_names: the name of the repos in which to look for issues
    :param ent_type: whether to retrieve issues or PRs (as issues)
    :param since: the timestamp after which to retrieve
    :return: the list of all retrieved entities
    """

    display_name = ENTITY_INFO[ent_type].display_name
    all_entities = []
    for repo_name in repo_names:
        log.info(f"Looking for new {display_name}s in {org_handle}/{repo_name}")
        entities = gh.search_issues(
            query="",
            sort="updated",
            order="desc",
            **{
                "repo": f"{org_handle}/{repo_name}",
                "is": ent_type,
                "state": "open",
                "created": f">={since.isoformat()}",
            },
        )
        all_entities += list(entities)

    log.info(f"Found {len(all_entities)} new {entity_info.display_name}s created")
    return all_entities


if __name__ == "__main__":
    configure_logger()

    args = parser.parse_args()

    log.debug(f"Entity type: {args.entity_type}")
    log.debug(f"Project number: {args.proj_number}")
    log.debug(f"Target column name: {args.target_col_name}")
    log.debug(f"Time period: {args.period}m")

    since = datetime.datetime.utcnow() - datetime.timedelta(minutes=args.period)

    github_info = get_data("github.yml")
    org_handle = github_info["org"]
    log.info(f"Organization handle: {org_handle}")
    repo_names = github_info["repos"].values()
    log.info(f"Repository names: {', '.join(repo_names)}")

    gh = get_client()
    org = gh.get_organization(org_handle)

    entity_type = args.entity_type
    entity_info = ENTITY_INFO[entity_type]
    new_entities: list[Issue] = get_new_issues(
        gh=gh,
        org_handle=org_handle,
        repo_names=repo_names,
        ent_type=entity_type,
        since=since,
    )
    if len(new_entities) == 0:
        log.warning(f"Found no new {entity_info.display_name}s, stopping")
        sys.exit()
    if entity_type == "pr":
        new_entities: list[PullRequest] = [
            entity.as_pull_request() for entity in new_entities
        ]

    proj = get_org_project(org=org, proj_number=args.proj_number)
    log.info(f"Found project: {proj.name}")
    target_column = get_project_column(proj=proj, col_name=args.target_col_name)
    log.debug("Found target column")

    for entity in new_entities:
        log.info(f"Creating card for {entity_info.display_name} {entity.number}")
        try:
            target_column.create_card(
                content_id=entity.id,
                content_type=entity_info.content_type,
            )
        except GithubException as ex:
            if "Project already has the associated" in str(ex):
                log.warning(f"Card already exists")
            else:
                log.error(
                    f"Failed to create card for {entity_info.display_name} {entity.number}"
                )
