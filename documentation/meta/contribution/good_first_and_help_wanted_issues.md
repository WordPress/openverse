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

---

## Reply Templates

- Scenario: A "first time contributor" asks if they can work on an issue.

  ```md
  Hi @{user}, thank you for your interest in contributing to Openverse! I've
  assigned this issue to you. If you have any questions, please leave them here.
  Please check out our
  [welcome](https://docs.openverse.org/general/contributing.html) and
  [quickstart](https://docs.openverse.org/general/quickstart.html) documentation
  pages for getting started with setting up your local environment.
  ```
