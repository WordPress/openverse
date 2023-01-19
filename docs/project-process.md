# Projects in Openverse

Openverse contributors use project threads to track our work. Project threads
GitHub meta issue in the `WordPress/openverse` repository with some special
requirements:

- The issue follows the "project thread" issue template
- The `project` label is applied to the issue
- A `status` label is applied to the issue (enforced via GitHub action)

These threads are for the benefit of our contributors, but also external
stakeholders to the project. Each project thread is a place to see the current
status, timeline, and motivation of a given work stream.

All requirements for working with project threads can be found in this document.
If you have any questions please feel free to reach out to an Openverse
maintainer in the #openverse channel of the
[Making WordPress Chat](https://make.wordpress.org/chat) or
[file an issue](https://github.com/WordPress/openverse/issues/new/choose).

## Where documents are kept, how they are named, and how they are reviewed

For each project, planning documents should be kept in the `rfcs/` directory of
this repository. Each project should have its own subdirectory, with projects
predating this document being moved into subdirectories. Individual documents
should be date-stamped in the `YYYYMMDD` format. An example of this entire
structure follows:

```
| rfcs/
   | service_metrics/
      - YYYYMMDD-project_proposal.md
      - YYYYMMDD-implementation_planning.md
   | 3d_model_support/
      - YYYYMMDD-project_proposal.md
      - YYYYMMDD-implementation_planning_(catalogue).md
      - YYYYMMDD-implementation_planning_(api).md
      - YYYYMMDD-implementation_planning_(frontend).md
```

Using subdirectories makes it slightly easier to navigate an ever-growing list
of planning documents. This is especially the case in projects similar to the 3D
Models project in the example above that may require multiple implementation
planning documents for each part of the application. In the process of planning
or implementing some projects, we may develop additional supporting documents or
appendixes that go beyond the required scope of the project planning process
described in this document. Those documents should accompany the required ones
in the same subdirectory for the project.

All project documentation can be authored with any tool, but must be written in
[GitHub Flavored Markdown](https://github.github.com/gfm/) including the
available
[GitHub-specific advanced formatting features](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting).

Additionally, all documents should be formatted to pass the Prettier linting
step required by the repository for Markdown documents.

When submitting a new document for a project, the author should open a pull
request with the document. The review process of the document will happen as a
PR review. Once the document is accepted and approved, it is merged and the
relevant step of the process is complete.

## Project Lifecycle

There a few stages in the project process. None is inherently more important
than the next. At each stage of the project lifecycle, an appropriate status tag
should be used to label the project thread. The correct tag can be found in the
title of each project lifecycle section.

### Creation (`status: not started`)

When contributors have decided to work on a project, we immediately create a
project thread to capture this intent. You can use "Project Thread" issue
template [To be created in this PR] to create a new project thread. At this
point, it is okay if we don't have any of the metadata for the project, which
includes:

```
ETA: {YYYY-MM-DD [Q?]}
Start Date: {YYYY-MM-DD}
Project Lead: {@username}
Actual Shipping Date: —
```

The post should include a small description explaining the goal and outcomes of
the project. For example:

> This is a project thread for using a cookie to store user session information,
> especially information related to preventing layout shift caused by server
> rendering and media queries.

This stage is the smallest and is meant to expressing our intent to work on the
project. At this time it is important to link to any background on the project
that could help the eventual project lead. Some ideas for this content include:

- Links to existing issues or draft PRs related to the project
- References to similar functionality in other projects, or 3rd party
  documentation for a relevant integration
- Links to past chat threads related to the project

In conclusion, the deliverable for this stage is a new project thread which
expresses our intent to work on a feature and why.

Finally, a GitHub
[issue can be created](https://github.com/WordPress/openverse/issues/new/choose)
in the `wordpress/openverse` repository to request a project proposal. This is
how we can track the creation of and lead assignment of a project.

> **Note**: At some point between creation and kickoff we need to make a
> determination about whom the lead of a project is. Often this has happened
> organically in the past, based on who may be most interested in a project or
> on whose work might be most relevant to the project.
>
> Do we need additional processes for assigning leads in cases where no one
> volunteers to work on a project?

### Kickoff (`status: in kickoff`)

In the kickoff stage, a **project proposal** is written and shared with the team
by the project lead. The primary goals of this document are that of discovery;
uncovering assumptions we've made about the project's goals and implementation.
Depending on the project, this discovery process may weigh more heavily towards
infrastructural and other technical considerations or towards team processes and
execution strategy.

#### Required content

Every plan should contain the following information:

1. Which of our year goals does this project advance?
2. How will we measure the success of this project? Share any new analytics
   tracking or metrics we will need to evaluate the success of the project.
3. Who will work on the project? Consider any sponsored developers needed, along
   with any external contributors or collaborators who need to be involved.
4. Are there any infrastructural changes or costs associated with this project?
5. Is there any marketing outreach that should be coordinated with this project?
   How is the project presented and made visible to our users?
6. Will any outside stakeholders or communities need to approve parts of the
   project, or confirm their interest?

Leads are not expected to know the answers to all of these questions. Rather,
leads should **ask questions** directly in the document, tagging relevant
contributors who can bring needed expertise and guidance. The goal is to lead
the process of requirement and assumption discovery.

> **A note on analytics**: Leads must endeavour to describe metrics and analysis
> that should be completed before the changes for the project's ultimate goal
> are implemented. Whenever possible or relevant, projects should have success
> criteria that compare the state of relevant metrics after the project's
> completion to the same metrics beforehand.

#### Tone and audience

This document should be readable by anyone unfamiliar with the specific
implementation details of Openverse. The discussion should largely mirror this
and be about the intentions, assumptions, and expectations of a project rather
than the technical details of it (which are covered in the next step). As
projects often focus on providing value to our users, consider if this document
were to be read by Openverse users, not just contributors. Would it effectively
convey the value of the work?

#### Formatting and process for Project Proposals

The PR description should use the
["Project Proposal" PR template.](./templates/project-proposal-pr-template.md)

#### The review process

Project proposals will be open for a two-week review period. In cases where
relevant contributors are AFK or otherwise unavailable, or a project proposal
experiences low engagement for a number of reasons, projects proposal deadlines
will be extended by one week.

Projects, their deadlines, and reviewers, will be added to our
[Action Items project board](https://github.com/orgs/WordPress/projects/59/views/1?query=is%3Aopen+sort%3Aupdated-desc)
for tracking with our other action items.

#### Wrapping up

Finally, the plan and technical proposals are merged, then the project thread is
given a substantial update. At this point we should be able to fill in all
metadata, including some additional fields:

- Links to the kick-off and technical implementation documents
- Links to any other external documents or supporting materials
- List stakeholders:
  - Implementers
  - Planners
  - Designers
  - Anyone else who is expecting the feature or has authoritative input over the
    project
  - Anyone who the implementers will depend on to be able to complete any of the
    steps of the project (no matter how obvious this might seem)
- Links to all milestones and relevant issues

### Implementation RFCs (`status: in rfc`)

[TBD]

<!-- notes for section

This section is a bunch of "identifying" technical details, leading up to a list of steps for implementing the projects requirements. The steps should be discrete and ordered. They should also, as much as possible, be organised into parallelisable work streams that can be distributed across multiple team members (if desired).

- technical planning
- giving step by step process for planning
- identify technical tools that will be used
   - when available, alternative options should be listed with their relevant pros and cons
- identify new Pypi, NPM, or binary dependencies required for the project
- identify work-streams that can run parallel
- identify work dependencies, especially cross-project dependencies that will need to be coordinated
- list feature flags that will be used
- explore API version conflicts and ensure that versioning is respected
   - gosh I'd really like to get a technical plan for adding new API version endpoints in the future :cold_sweat:
- identify hard blockers that will prevent further work on the project
- identify areas of technical ambiguity that were not able to be predetermined during planning (i.e., after we've implemented _x_, we'll be able to make an informed decision about _y_)
- identify significant/unprecedented cost increases or decreases associated with related infrastructure changes
- identify atomic blocks of work so that work can be split into individual, small, easily reviewable PRs
   - ideally PRs can be reviewed by anyone capable of reviewing in the relevant parts of the code base, not only people intimately familiar with the project
   - this isn't always possible, but it is good to strive for it as much as we can

-->

### Implementation (`status: in progress`)

In the implementation phase, contributors begin work on the project. At this
point the work has been divided into discrete tasks and ordered according to
priority. Folks who have _not read_ the motivating documents or who even lack a
full understanding of the project should be able to jump in and work on
individual pieces of the project by _exclusively_ reading the information
present in the GitHub issue or task they are being assigned.

> **Warning** If this isn't possible, planning was insufficient, and we may want
> to place the project in `status: on hold` to re-adjust. It's a very important
> aspect of the work.

> **Note for implementers**: With sufficient planning, it may make certain
> issues able to be easily implemented at the same time, in a single PR.
> However, this should be avoided. The implementation plan will have split the
> work into small, atomic, and digestible chunks of work that progress the
> project at an appropriate pace. Keep in mind that small PRs are reviewed
> _much_ faster than bigger PRs. While implementing two or three issues in one
> go may _feel_ faster, it is often no faster, but much riskier (due to
> increased review overhead) than going step-by-step.

> **Note for code reviewers**: Code reviewers should focus primarily on the
> technical aspects of the implementation required by the issue. At times,
> during the course of a project, significant issues will only be discovered
> during implementation and sometimes an alarm bell must be rung. However, these
> should be reserved for issues that will cause long-term harm to the project.
> Merely disagreeing with a particular detail of the project's implementation
> details is not sufficient for holding up a PR that is part of a larger,
> carefully planned project, for which a technical implementation plan has
> already been reviewed and approved. Therefore, avoid raising objections to the
> broad technical decisions of a PR unless they do cause long term harm to the
> project. This allows projects to move along at an expedient pace and trusts
> that the project planners did their due diligence in considering alternatives.
>
> Of course, exceptions to this do exist and reviewers are expected to point out
> when there is a significant issue with the implementation details of a PR that
> will cause long-term harm.

#### Providing project updates

Project updates should be left as weekly comments in the project threads. Even
if the update is "the project has stalled." or "No developments this week", the
updates should still be posted. This removes ambiguity for folks visiting the
project, avoiding questions like "I don't see an update this week; is it being
worked on or not?"

These updates are useful for folks checking in on a project but also for the
project lead. It's an opportunity to _reflect on_ the status of the project and
any blockers, or successes to be shared.

Here is an [update template](./templates/project-update.md) to be followed for
every project update.

### Delivery (`status: shipped`)

The completion of technical implementation is a time for celebration and
reflection.

### After Completion (`status: success`, `status: reverted`)

[TBD]

<!-- notes for section
- measuring analytics/frequency of analytics updates
- reporting progress towards a success or revert decision
- brainstorming fast-follow tweaks that may help project performance
-->

### Reference: Project Statuses

- `not started`: Has not started yet.
- `in kickoff`: Project proposal is in progress.
- `in RFC`: Technical implementation plan is in progress.
- `in progress`: Under active development.
- `on hold`: Stalled or blocked after work started.
- `shipped`: Launched. Success criteria are under evaluation.
- `success`: Completed. Success criteria are met.
- `rollback`: Completed. Success criteria are not met. Work is reverted.
