# Regular maintainer tasks

This document summarises and collects links to information about tasks other
than opening new code contributions that maintainers should consider, especially
if they already have several PRs with reviews requested.

- Review
  [older open PRs, even ones not assigned to you](https://github.com/WordPress/openverse/pulls?q=is%3Apr+is%3Aopen+sort%3Acreated-asc+draft%3Afalse+-reviewed-by%3A%40me+review%3Arequired+-author%3A%40me+)
- Review the
  [issue backlog and perform some of the regular backlog maintenance tasks](/general/contributing.md#issue-backlog-maintenance)
- Pick up the
  [oldest, unassigned implementation plan](https://github.com/wordpress/openverse/issues?q=is%3Aopen+is%3Aissue+label%3A%22%F0%9F%A7%AD+project%3A+implementation+plan%22%2C%22%F0%9F%A7%AD+project%3A+proposal%22+sort%3Acreated-asc+no%3Aassignee)
  - This will eventually result in a new PR but usually takes a while to
    complete and are easy to overlook in favour of direct code contributions
  - If an older implementation plan is assigned and hasn't been started and you
    could pick it up, consider pinging the current assignee to offer to take if
    off their plate
- Search through Sentry for older issues that might be getting worse; see
  [section below for details](#sentry-review)
- Read and respond to
  [active discussions](https://github.com/WordPress/openverse/discussions)
- Research unknown/under-documented parts of the project; see
  [section below for advice](#unknownunder-documented-parts-of-the-project)
- Pick up active incident investigation
  - Check with MSR if you need help identifying what incidents need help
    investigating
- Proofread documentation; see
  [the documentation review page for advice](/meta/documentation/review.md)

## Sentry review

While the Openverse Mini-Support Rotation[^msr] covers recording and triaging
_new_ Sentry issues, it does not include regularly checking the frequency of
existing issues. You can review Sentry issues by frequency by visiting the
following links:

[^msr]:
    The Openverse Mini-Support Rotation is managed by the core maintainers. Each
    week, one of the maintainers takes on several responsibilities for regular
    maintenance tasks, one of which is to check Sentry for new events that need
    to be converted into GitHub issues.

- [Django API](https://openverse.sentry.io/issues/?project=6107216&query=is%3Aunresolved&referrer=issue-list&sort=freq&statsPeriod=30d)
- [Frontend](https://openverse.sentry.io/issues/?project=5799642&query=is%3Aunresolved&referrer=issue-list&sort=freq&statsPeriod=30d)
- [Ingestion Server](https://openverse.sentry.io/issues/?project=4504934126059520&query=is%3Aunresolved&referrer=issue-list&sort=freq&statsPeriod=30d)

If you see an issue with heaps of events and see that the GitHub issue is not
being worked on or has been prioritised such that it will not be picked up soon,
use your best judgement to determine whether it needs to be worked on
immediately (it could be the next code contribution you work on) or if it's safe
enough to just add to the weekly dev chat agenda.

## Unknown/under-documented parts of the project

There are a handful of issues in our backlog that request documentation for
parts of the project. You can find those by scanning the list of
[text-aspect issues](https://github.com/wordpress/openverse/issues?q=is%3Aopen+is%3Aissue+sort%3Acreated-asc+no%3Aassignee+label%3A%22%F0%9F%93%84+aspect%3A+text%22).
To identify other parts of the project that might need additional documentation,
think of the following:

- Is there anything that you know particularly well that you feel other
  maintainers might not?
- On the other hand, is there anything that you do not know well and feel could
  be better documented? This could be a good time to learn more about it with
  hands on experience researching and documenting it. **This is especially
  important if it is something that none of the maintainers know well.**
- Is there ambient context or domain-specific knowledge that is not explicitly
  documented that should be?

If you start writing documentation, you're likely to open a PR. This is okay,
text/documentation PRs are excluded from the list of requested reviews as they
have a significantly lower review burden than code changes, in particular
because the consequences of incorrect or poor documentation are usually far less
severe than incorrect code.
