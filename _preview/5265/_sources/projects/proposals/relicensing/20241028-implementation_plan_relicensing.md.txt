# 2024-10-28 Implementation Plan: Relicensing

**Author**: @dhruvkb

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @krysal
- [x] @obulat

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- <s>Project Thread</s>
- [Project Proposal](/projects/proposals/relicensing/20241028-project_proposal.md)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan

- describes the different code blocks in the repository.
- lists the different goals we have for each of these blocks in terms of the
  license.
- lists the ideal license for each code block.
- documents the process we will use to change the license.

There are a few approaches that we can take here but the simplest would be to
relicense the software directly. See alternatives [below](#alternatives).

> In the case of a permissive software license, a new license (including
> proprietary licenses) can be applied to the project and it can be
> redistributed under those terms.
>
> - [Drew deVault's blog](https://drewdevault.com/2023/07/04/Dont-sign-a-CLA-2.html)

Since Openverse is licensed under the permissive MIT license, it is possible for
us to unilaterally and directly change the license. This would be logically
equivalent to a new project that builds upon all of Openverse's code but under a
GNU license.

The code prior to the license change commit would continue to be available in
the repository's history and will remain MIT licensed. It would allow people who
disagree, or cannot comply, with the GNU licenses to be able to use code from
before the license change under the terms of the MIT license.

By doing so, we are not betraying the trust of the contributors who have
contributed to the project as their contributions will continue to be
open-source. We did not have a contributor license agreement (CLA) and will not
add one. It is generally regarded negatively and indicates that the project can
migrate to becoming closed-source in the future.

> Thus, the absence of a CLA combined with the use of a copyleft license serves
> as a strong promise about the future of the project.
>
> - [Drew deVault's blog](https://drewdevault.com/2023/07/04/Dont-sign-a-CLA-2.html)

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

The outcomes of the implementation plan will be the names of the final license
for each code block and the process we will use to migrate the license.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

1. Determine code blocks.
2. Determine the goals for these blocks from the license.
3. Determine new licenses.
4. Institute code freeze.
5. Apply new licenses.

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

### Determine code blocks

The Openverse monorepo consists of the following code blocks.

- Libraries
  - Attribution
  - API client
- Applications
  - API
  - Frontend
- DAGs
- Glue
  - Workflows
  - Automations
  - `ov` (development environment)

### Determine the goals for these blocks from the license

- Libraries

  We want our libraries to be used as broadly as possible, in both free as well
  as non-free software. The libraries encourage good practices in terms of API
  usage and attribution and so we do not want to limit them to just free
  software.

- Applications

  We want our applications to be open-source, and forks of these applications to
  be open-source as well. We do not want to discourage free software derivatives
  of Openverse. We want GPL protections to apply even when these applications
  are accessed over the Internet.

### Determine new licenses

- Libraries

  The GNU LGPL license allows our libs to be used universally in both free as
  well as non-free environments. Our goal is the proliferation of good
  attribution practices and making the Openverse API easily accessible.

  > using the Lesser GPL permits use of the library in proprietary programs
  >
  > - [FSF](https://www.gnu.org/licenses/why-not-lgpl.html#:~:text=using%20the%20Lesser%20GPL%20permits%20use%20of%20the%20library%20in%20proprietary%20programs)

- Applications

  The GNU AGPL license requires derivatives of the API and frontend, which are
  accessed over a network to also share source code, which is want we want.

  > if you run a modified program on a server and let other users communicate
  > with it there, your server must also allow them to download the source code
  > corresponding to the modified version running there
  >
  > - [FSF](https://www.gnu.org/licenses/why-affero-gpl.html#:~:text=if%20you%20run%20a%20modified%20program%20on%20a%20server%20and%20let%20other%20users%20communicate%20with%20it%20there%2C%20your%20server%20must%20also%20allow%20them%20to%20download%20the%20source%20code%20corresponding%20to%20the%20modified%20version%20running%20there)

- Everything else

  The GNU GPL license is a good fit for the rest of the codebase, since there
  are no special requirements for this code (unlike apps and libs).

I have audited the licenses of our dependencies (specifically those of the API
and frontend) and they are compatible with us switching to the AGPL license.
Additionally Airflow is licensed under the Apache license which is also
compatible with us relicensing to GPL.

### Institute code freeze

We need to institute a code freeze because we need to add the commit hash of the
last commit that will be under the MIT license to the `LICENSING.md` file.

Any PRs opened before the code freeze can take one of three routes.

- Be merged before the license transition and be covered by the MIT license
- Reaffirm that they are compatible with the GNU license family and be merged.
- Be closed without being merged.

### Apply new licenses

To apply different licenses to different parts of the repository, we will take
the following steps.

#### Add a `LICENSING.md` file

The purpose of this file is to explain what licenses apply to which code block
and how they are cascaded. It should look like this template (3 fields need to
be filled out):

```md
The default license for this project is
[GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html).

The following libraries are licensed under
[LGPL-3.0-or-later](https://spdx.org/licenses/LGPL-3.0-or-later.html) and not
under the default license.

- <libraries' names go here>

The following applications are licensed under
[AGPL-3.0-or-later](https://spdx.org/licenses/AGPL-3.0-or-later.html) and not
under the default license.

- <applications' names go here>

## History

All code before <commit> is available under
[MIT](https://spdx.org/licenses/MIT.html).
```

#### Add/update `LICENSE` files

We will update the existing root license and add the appropriate licenses for
the code blocks that were exempted from the default and applied specific
licenses.

- `api/LICENSE` (new, AGPL-3.0-or-later)
- `frontend/LICENSE` (new, AGPL-3.0-or-later)
- `packages/js/api-client/LICENSE` (new, LGPL-3.0-or-later)
- `packages/python/openverse-attribution/LICENSE` (new, LGPL-3.0-or-later)
- `LICENSE` (MIT → GPL-3.0-or-later)

#### Update license in manifests

The following files contain references to the project license. These will need
to be updated.

- Python packages
  - `.vale/pyproject.toml`
  - `api/pyproject.toml`
  - `documentation/pyproject.toml`
  - `indexer_worker/pyproject.toml`
  - `packages/python/openverse-attribution/pyproject.toml`
- JS packages
  - `packages/js/api-client/package.json`
  - `packages/js/k6/package.json`
- Other references
  - `documentation/packages/js/api_client/index.md`
  - `api/conf/settings/spectacular.py`
  - `catalog/tests/factories/github/pull.json`

## Communications

<!-- Note any projects this plan depends on. -->

Both at the start of the migration, and once the migration is completed, we will
need to communicate the status to the
[stakeholders listed in the project proposal](/projects/proposals/relicensing/20241028-project_proposal.md#participants-and-stakeholders).

The following communication will be needed

- intent to relicense

  This should be communicated once this project proposal and implementation plan
  are approved and merged.

  This notification should clearly state

  - the new GNU licenses that we are planning to switch to for the various code
    blocks
  - that the change only applies to future commits after the license change
  - that code before the license change can continue to be used under the same
    terms

  This also gives us time to see the community's reception to the changes.

  I do not anticipate any negative reactions because, unlike the license changes
  at Elasticseach, Redis and others, we are not making the project closed-source
  but rather making it more open-source
  ([in a sense](https://drewdevault.com/2024/04/19/2024-04-19-copyleft-is-not-restrictive.html))
  by adding stronger copyleft protections.

  If concerns or objections are raised by this communication, we will convene a
  discussion to address and potentially adjust the relicensing strategy.

- new licenses

  This should be communicated out once the license change commit is merged.

  This notification should clearly state

  - the new GNU licenses that we are now using the for the various code blocks
  - that users should ensure their compliance with the terms of the new licenses
  - that they should not use post-relicensing versions if they do not comply

## Alternatives

Prior to the clarification about the relicensing approach, I had considered
dual-licensing as a viable option. All code contributed up to a specific commit
would be licensed under the current MIT license, and all code contributed after
that point would be licensed under the various GNU licenses we have applied to
the various code blocks.

In such cases each `LICENSE` file in the repository would have two licenses, the
original MIT and the new GNU, with a section at the top explaining which license
is applicable to which part of the code, based on whether it was added/modified
before/after the cut-off date.

## Design

<!-- Note any design requirements for this plan. -->

The communications mentioned above can use some visuals. Such visuals would be
completely optional and subject to the availability and bandwidth of our
designer, Francisco.

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

This project has no blockers but it also doesn't have any urgency to it. We
should ideally be careful and not rush into any decisions.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

There is precedent for a number of web-based products switching to the GNU AGPL
license:

- [Joplin](https://joplinapp.org/news/20221221-agpl/)
- [Plausible](https://plausible.io/blog/open-source-licenses)
- [Grafana](https://grafana.com/blog/2021/04/20/grafana-loki-tempo-relicensing-to-agplv3/)
- [MinIO](https://blog.min.io/from-open-source-to-free-and-open-source-minio-is-now-fully-licensed-under-gnu-agplv3/)

Three of these four are respectable open-source products that we ourselves use
at Openverse. We can refer to their approaches as the framework for handling our
own migration.
