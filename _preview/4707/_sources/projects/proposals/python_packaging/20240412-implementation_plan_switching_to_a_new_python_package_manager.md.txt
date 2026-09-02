# 2024-04-12 Implementation Plan: Switching to a new Python package manager

**Author**: @dhruvkb

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @sarayourfriend
- [x] @AetherUnbound

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan compares the current best tools for managing Python
dependencies and packages and proposes a plan to switch to a new package manager
determined by the comparison.

## Expected Outcomes

At the end of the implementation of this plan, we should have the Openverse API
project using a new Python package manager. The new package manager will be
integrated with our existing integrations and will be behind the Docker builds
for the API being run in staging and production.

Other parts of the Openverse project can also be migrated to the new package
manager based on the success of this implementation, but they should not be
considered as success criteria for this project.

## Goals

These are criteria for choosing a package manager that would make an option
ineligible if not met. The package manager must

- **support apps and libraries**

  We want to build Python libraries as publish to PyPI, as well as applications
  like the API and ingestion server. Our package manager has to suitable for
  both purposes.

- **support internal dependencies**

  Following up on the last point, our tools package manager must allow our apps
  to depend on libraries, either as part of their monorepo support or as path
  dependencies. This should also work reliably inside Docker.

- **support targeted updates**

  This is one of the main reasons we are switching away from Pipenv so the
  alternative has to support this requirement. Updating one package should not
  update any unrelated packages.

- **integrate with auto-updaters**

  Following up on the last point, we use Renovate for automatically updating
  packages periodically, and also Dependabot for immediate security updates.
  These tools support popular package managers and those that adhere to PEP 621
  (see [Renovate](https://docs.renovatebot.com/modules/manager/pep621/) and
  [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates#pip-and-pip-compile)).

### Additional good-to-haves

These are not deal-breaking criteria but would be nice to have. The package
manager should

- **be fast**

  The package manager should quickly resolve dependencies and should also make
  downloading and installing packages faster using caching similar to pnpm.

- **have ease of use**

  This is somewhat subjective, but the package manager should be fairly easy to
  use, should not have too much magic, and should make Python workflows like
  building Docker images and publishing packages to PyPI easier.

- **comply with standards**

  The package manager should not reinvent the wheel and should follow the
  standards like PEP 621, PEP 517 and PEP 508. This is important for future
  integrations and compatibility with other tools.

- **be around for the long term**

  The package manager should be actively developed and maintained, and should
  have a good community around it. This is important for long-term support and
  active maintenance in the future.

## Decision making

To decide the new package manager, many options were considered. Here are the
options, what benefits they provided and why they were ultimately not chosen as
the path forward.

![](./star_history.png)

### [Rye](https://rye-up.com/)

#### Why?

- all-in-one tool (at least trying to be)
- provisions
  [@indygreg's python-build-standalone](https://github.com/indygreg/python-build-standalone)
- PEP 621 compliant
- fastest among all options considered (written in Rust, uses
  [`uv`](https://github.com/astral-sh/uv/) under the hood)
- lockfile follows `requirements.txt` standard
- supports monorepo workspaces
- developed by [Armin Ronacher](https://github.com/mitsuhiko)
- fastest growing in terms of GitHub stars
- supports multiple build backends via
  [PyPA/build](https://build.pypa.io/en/stable/)

#### Why not?

- looks like
  [1 core maintainer](https://github.com/astral-sh/rye/graphs/contributors)
- [no stable v1 yet](https://github.com/astral-sh/rye/releases)
- [considered "experimental"](https://github.com/search?q=repo:astral-sh/rye%20experimental&type=code)
- [VC-backed](https://astral.sh/about)
- [not supported by Renovate](https://github.com/renovatebot/renovate/issues/25273)
  [⚠️ deal-breaker]
- does not generate platform-independent lockfiles

### [PDM](https://pdm-project.org/)

#### Why?

- PEP 621 compliant
- supports libraries (build and publish to PyPI) as well as apps
- generates cross-platform lockfiles
- good CLI experience for developers
- supported by [Renovate](https://docs.renovatebot.com/modules/manager/pep621/)
  and
  [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates#pip-and-pip-compile)
- supports multiple build backends
- supports monorepo workspaces
- provisions
  [@indygreg's python-build-standalone](https://github.com/indygreg/python-build-standalone)
- [endorsed](https://github.com/astral-sh/rye/discussions/6#discussioncomment-5700997)
  by creator of Rye!

#### Why not?

- looks like
  [1 core maintainer](https://github.com/pdm-project/pdm/graphs/contributors)
- fewest GitHub stars and forks indicative of low popularity
- [flagship feature rejected](https://pdm-project.org/en/latest/usage/pep582/)

### [Poetry](https://python-poetry.org/)

#### Why?

- stable (post v1) and mature (6+ years old)
- ease of use due to being ideologically close to Pipenv
- supports libraries (build and publish to PyPI) as well as apps
- generates cross-platform lockfiles
- good CLI experience for developers
- highest GitHub stars and forks indicative of high popularity
- looks like
  [2 core maintainers](https://github.com/python-poetry/poetry/graphs/contributors)
  (> 1)
- supported by
  [Renovate](https://docs.renovatebot.com/modules/manager/poetry/)[^poetry_reno]
  and
  [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#package-ecosystem)
- [challenged non-endorsement](https://github.com/astral-sh/rye/discussions/6#discussioncomment-5702537)
  by creator of Rye

[^poetry_reno]:
    Renovate is not 100% compatible with Poetry and recommends pinning
    dependencies in `pyproject.toml` instead of using ranges, although their
    justification for this is very weak.

#### Why not?

- [PEP 621 non-compliant](https://github.com/python-poetry/roadmap/issues/3)
- only supports
  [one build backend](https://github.com/python-poetry/poetry-core)
- does not support monorepo workspaces
- despite cache, not as fast as other alternatives

### Conclusions

We have opted to use PDM because of its compliance with various PEP standards,
as well as its support for caches. It will support us to build Python libraries
as well as applications.

I have good hopes for Rye to be a strong contender in the future once it is
mature and popular enough to be taken seriously. If Poetry manages to become PEP
compliant and faster, it may be considered in the future too.

## Step-by-step plan

1. Replace Pipenv with PDM.
2. Update Renovate configuration.
3. Update `Dockerfile`s.
4. Update `just` recipes.

These are fairly small steps and we can cover all of them in one PR
[like this](https://github.com/WordPress/openverse/pull/4107).
