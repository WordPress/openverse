# Maintainer guidelines for "Good first" and "Help wanted" issues

GitHub issues tagged "good first issue" and "help wanted" are often a
contributors entry-point into a project. As such, it is important that these
issues not only are true to their tag names, but that they are also giving new
contributors an ideal first experience. Finally, _providing_ this experience
needs to be straightforward and repeatable for maintainers.

Here you will find guidelines, predefined responses, and tools for creating
these issues and guiding the contributors who seek to resolve them.

# Good first issues

## What makes an issue a good first issue?

Generally speaking, a good first issue is one that provides a contributor an
isolated, discrete task that teaches the contributor something new about
Openverse. This learning enables the contributor to take on subsequent issues
with increased confidence.

Here are some example signs that an issue is sufficiently isolated. These
issues:

- Do not require a holistic understanding of Openverse's ingestion pipeline
- Are limited to single programming language or programming paradigm (i.e,
  frontend JS, CSS, and markup)
- Occupy a single slice of the Openverse stack
- Touch a single file or as few files as necessary; ideally these files are
  colocated in the repository
- Are based on the `main` branch and not sub-features of a larger, multi-PR
  changeset

Other qualities of appropriate "good first" issues are that they:

- Are not 'high priority', 'critical priority', or otherwise time sensitive
- Are appropriate for those new to open source or Git workflows in-general
- Can be, approximately, completed within two hours, one of which may be
  necessary for local development environment setup

## Writing good first issue descriptions

Good first issue descriptions should provide as much context as possible. These
issues should generally be self-contained; all the documentation necessary to
complete the issue should be included with or linked to in the issue
description. The aim is to make the issue as approachable as possible while
setting clear expectations. This up-front effort is to the benefit of
contributors and maintainers. Ideally, it decreases the amount of time
maintainers spend reviewing PRs that have not met the minimum requirements
(e.g., no unit tests, linting failures, and so on). For contributors, it helps
prevent them from feeling discouraged after completing the "core functionality"
of a PR to then have to revisit the PR and add significant changes.

Descriptions should:

- Clearly articulate the expected outcome of resolving the issue. Include any of
  the following, when relevant:
  - Changes (modifications or additions) to tests
  - Link to instructions for updating Playwright snapshots if the change might
    require it
  - Changes (modifications or additions) to documentation
- Link to the relevant files and/or lines of code which need changing
- Reference any past PRs which will help the contributor, for example:
  - A PR with a similar change
  - A PR which originally implemented the feature being modified
- Relevant Openverse domain knowledge, either links to succinct documentation or
  links and a summary of the important aspects when documentation is detailed
  - Ideally "good first issue"s require essentially no Openverse-specific domain
    knowledge, but if they at all do (for example, to explain why a non-obvious
    solution is requested) then it must be included

### Additional boilerplate for "good first issues"

In addition to our standard issue template, good first issues should _also_
contain the following block of requirements:

```md
## Good first issue checks

- Have I filled out the PR template correctly?
  - Did I include testing instructions?
- Does my PR pass linting? (Test either via precommit or by running `just lint`
  manually)
- Do all the tests still pass?
  - If JavaScript changes, run `pnpm -r run test`
  - If API changes, run ` just api/test`
  - If catalog changes, run `just catalog/test`
```

---

## Reply templates and behaviors

These predefined responses ("predefs") provide consistient solutions to common
situations.

If you find yourself dealing with a recurring scenario that _isn't_ included in
this list, please submit a pull request to add it here.

### Scenario 1: Issue Request

A "first time contributor" asks if they can work on an issue.

#### Initial Response

```md
Hi `@user`, thank you for your interest in contributing to Openverse! I've
assigned this issue to you. If you have any questions, you may leave them here.

Please check out our
[welcome](https://docs.openverse.org/general/contributing.html) and
[quickstart](https://docs.openverse.org/general/quickstart.html) documentation
pages for getting started with setting up your local environment.
```

#### Follow up

Assign the issue to the user.

### Scenario 2: Improper PR Template

A community pull request author did not use the pull request template or failed
to fill out all sections correctly.

#### Initial Response

```md
Hi `@user`, could you update your pr description to use the
[pull request template](https://github.com/WordPress/openverse/blob/main/.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)?
If you have any questions please let us know in the comments.
```

#### Follow through

If the contributor doesn't reply or update the PR, move on to
[scenario #3](#scenario-3-absent-contributor).

### Scenario 3: Absent Contributor

A contributor opened a pull request but hasn't updated it or responded to
changes in the required timeframe.

#### Initial Response

```md
Hi {@user}, are you still able to work on this PR? We appreciate all the work
you have completed so far. If you are not able to finish this pull request we
can unassign you, so a maintainer can take over the remaining work.
```

#### Follow through

Wait 5 business days for the user to respond. If they do not respond, unassign
the PR, draft the PR, and reply with the following:

```md
@{user} thank you again for your efforts here. I have unassigned this PR and
drafted it to be picked up by a maintainer when avaliable. If you would ever
like to resume work, do not hesitate to let us know here.
```
