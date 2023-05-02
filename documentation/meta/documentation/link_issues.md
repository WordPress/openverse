# Sphinx GitHub issue resolver plugin (`link_issues`)

The `link_issues` Sphinx plugin is copied directly into the repository to
accommodate updates necessary to support modern Sphinx versions.

Please see the
[documentation string at the top of the module for credits and license text for the code](/_ext/link_issues.py).
Modifications have been made to the original code to enable the use of GitHub
authentication tokens to prevent rate limiting from breaking issue resolution.
If you want to test issue resolution locally, add a `LINK_ISSUES_GITHUB_TOKEN`
environment variable when running the documentation stack. The token must have
read permissions for public repositories.
