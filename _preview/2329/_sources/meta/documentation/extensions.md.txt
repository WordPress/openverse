# Sphinx extensions

## GitHub issue resolver plugin (`link_issues`)

The `link_issues` Sphinx plugin is copied directly into the repository to
accommodate updates necessary to support modern Sphinx versions.

Please see the
[documentation string at the top of the module for credits and license text for the code](/_ext/link_issues.py).
Modifications have been made to the original code to enable the use of GitHub
authentication tokens to prevent rate limiting from breaking issue resolution.
If you want to test issue resolution locally, add a `LINK_ISSUES_GITHUB_TOKEN`
environment variable when running the documentation stack. The token must have
read permissions for public repositories.

## GitHub username link plugin (`link_usernames`)

The `link_usernames` Sphinx plugin is a simple, custom plugin which modifies the
source of documentation files to change `@username` to a link to the user's
GitHub profile. Changelog files are excluded from this process since those
username references are already linked when creating the changelog. See the
[plugin code and docstring](/_ext/link_usernames.py) for more information.
