import requests


class GitHubAPI:
    def __init__(self, pat: str):
        """:param pat: GitHub Personal Access Token to use to authenticate requests"""
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"token {pat}"

    def _make_request(self, method: str, resource: str, **kwargs):
        response = getattr(self.session, method.lower())(
            f"https://api.github.com/{resource}", **kwargs
        )
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def get_issue(self, repo: str, issue_number: int, owner: str = "WordPress"):
        return self._make_request("GET", f"repos/{owner}/{repo}/issues/{issue_number}")

    def get_open_prs(self, repo: str, owner: str = "WordPress"):
        return self._make_request(
            "GET",
            f"repos/{owner}/{repo}/pulls",
            data={
                "state": "open",
                "base": "main",
                "sort": "updated",
                # this is the default when ``sort`` is ``updated`` but
                # it's helpful to specify for readers
                "direction": "asc",
                # we don't bother paginating because if we ever
                # have more than 100 open PRs in a single repo
                # then something is seriously wrong
                "per_page": 100,
            },
        )

    def post_issue_comment(
        self, repo: str, issue_number: int, comment_body: str, owner: str = "WordPress"
    ):
        return self._make_request(
            "POST",
            f"repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": comment_body},
        )

    def get_issue_comments(
        self, repo: str, issue_number: int, owner: str = "WordPress"
    ):
        return self._make_request(
            "GET",
            f"repos/{owner}/{repo}/issues/{issue_number}/comments",
        )

    def get_issue_events(self, repo: str, issue_number: int, owner: str = "WordPress"):
        # GitHub by default returns only 30 results, so we need to paginate over
        # all of them to get the full list of events
        # https://docs.github.com/en/rest/issues/events?apiVersion=2022-11-28#list-issue-events
        page = 1
        all_events = []
        while events := self._make_request(
            "GET",
            f"repos/{owner}/{repo}/issues/{issue_number}/events",
            params={"page": page},
        ):
            all_events.extend(events)
            page += 1
        return all_events

    def delete_issue_comment(
        self, repo: str, comment_id: int, owner: str = "WordPress"
    ):
        return self._make_request(
            "DELETE", f"repos/{owner}/{repo}/issues/comments/{comment_id}"
        )

    def get_pull_reviews(self, repo: str, pull_number: int, owner: str = "WordPress"):
        return self._make_request(
            "GET",
            f"repos/{owner}/{repo}/pulls/{pull_number}/reviews",
        )

    def get_branch_protection(self, repo: str, branch: str, owner: str = "WordPress"):
        return self._make_request(
            "GET",
            f"repos/{owner}/{repo}/branches/{branch}/protection",
        )

    def get_package_versions(self, package: str, owner: str = "WordPress"):
        return self._make_request(
            "GET",
            f"orgs/{owner}/packages/container/{package}/versions",
        )

    def dispatch_workflow(
        self,
        repo: str,
        workflow_id: str,
        inputs: dict = None,
        ref: str = "main",
        owner: str = "WordPress",
    ):
        return self._make_request(
            "POST",
            f"repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
            json={"inputs": inputs or {}, "ref": ref},
        )

    def get_team_members(self, team: str, owner: str = "WordPress"):
        return self._make_request(
            "GET",
            f"orgs/{owner}/teams/{team}/members",
        )
