# GitHub contribution practices

Here are some of the practices we follow at Openverse when it comes to GitHub
contributions.

## GitHub labels

### Aspect

There are many [aspects](https://github.com/WordPress/openverse/labels?q=aspect)
in which the Openverse project can be improved. These can directly involve the
code but there are other related areas such as documentation and interfaces.

### Technology

Openverse projects span a lot of languages, frameworks, tools and
[technologies](https://github.com/WordPress/openverse/labels?q=tech) across the
stack from JavaScript and TypeScript on the frontend to Python on the backend.

### Stack

Openverse spans a tall
[stack](https://github.com/WordPress/openverse/labels?q=stack), from the catalog
at the innermost level, followed by the ingestion server, the API and the
frontend. There is scope of improvement at each level.

### Contributor friendliness

We use two labels to identify issues that have been specifically created or
selected for new contributors:
["help wanted"](https://github.com/WordPress/openverse/issues?q=is:issue+is:open+sort:updated-desc+label:%22help+wanted%22)
and
["good first issue"](https://github.com/WordPress/openverse/issues?q=is:issue+is:open+sort:updated-desc+label:%22good+first+issue%22).

#### Help wanted

These are issues that are friendly for outside contributors because they are not
urgent, have well-defined scope and don't need any special access, permissions
or knowledge that contributors might not have.

#### Good first issues

These issues are a subset of [issues wanting help](#help-wanted) that are
smaller in scope, make for a gentle introduction to the code and can be
completed in under ~4 hours (including the [setup](../guides/general_setup.md)).

```{caution}
In reality, the process can take more time if the setup process does not go
smoothly. In such cases, we encourage you to share your experience in an issue.
We will try to prevent those roadblocks for future contributors.
```

Items marked with the good first issue label are intended for first-time or new
contributors. It indicates that members will keep an eye out for these issues
and shepherd the contributors and their PRs through our processes.

All "good first issues" are "help wanted" but not vice versa.

## Choosing an issue

The right issue to work on is one whose aspect, technology and stack labels
match your interested area of work. Making contributions will be easier if these
align with your forte, but they don't necessarily have to.

You can filter issues based on these labels to find one that matches all of the
following criteria.

- Is open.
- Has the "help wanted" label.
- Does not have someone working on it in the last ~7 days.
- Has not recently been requested by someone else.

Once you've picked an issue to work on, please leave a comment saying so on the
issue and tag `@WordPress/openverse-maintainers` in the comment. That way the
team will be notified and one of us will assign the issue to you.
