# Project Planning

Openverse contributors use project threads to track our work. Project threads
are issues in the `WordPress/openverse` repository with some special
requirements:

- The issue follows the
  [project thread issue template](https://github.com/WordPress/openverse/blob/main/.github/ISSUE_TEMPLATE/project_thread.md)
- The `project` label is applied to the issue
- A `status` is applied to the issue via our GitHub Project Board

These threads are for the benefit of our contributors, but also external
stakeholders to the project. They provide visibility into our current
initiatives and up to date information on each initiative. Each project thread
is a place to see the current status, timeline, and motivation of a given work
stream.

All requirements for working with project threads can be found in this document.
If you have any questions please feel free to reach out to an Openverse
maintainer in the #openverse channel of the
[Making WordPress Chat](https://make.wordpress.org/chat) or
[file an issue](https://github.com/WordPress/openverse/issues/new/choose).

## Where documents are kept, how they are named, and how they are reviewed

For each project, planning documents should be kept in the
`/documentation/projects/proposals/` directory of this repository. Each project
should have its own subdirectory. Projects predating this document have been
updated to follow this structure. Individual documents should be date-stamped in
the `YYYYMMDD` format. An example of this entire structure follows:

```
| documentation/projects/proposals/
   | service_metrics/
      - YYYYMMDD-project_proposal.md
      - YYYYMMDD-implementation_plan.md
   | 3d_model_support/
      - YYYYMMDD-project_proposal.md
      - YYYYMMDD-implementation_plan_(catalogue).md
      - YYYYMMDD-implementation_plan_(api).md
      - YYYYMMDD-implementation_plan_(frontend).md
```

Using subdirectories makes it slightly easier to navigate an ever-growing list
of planning documents. This is especially the case in projects similar to the 3D
Models project in the example above that may require multiple implementation
planning documents for each part of the application. In the process of planning
or implementing some projects, we may develop additional supporting documents or
appendixes that go beyond the required scope of the project planning process
described in this document. Those documents should accompany the required ones
in the same subdirectory for the project.

```{warning}
Subdirectories require an `index.md` in order to be included in the documentation site's table of contents.

Because project documents prefix their titles with a date, we can safely use a glob to include all project planning documents in a project directory and have them intuitively ordered by date.

Refer to the [project `index.md` templates](/projects/templates/index.md) for a starting point.
```

All project documentation can be authored with any tool, but must be written in
[MyST/Commonmark+ flavored Markdown](https://myst-parser.readthedocs.io/en/latest/syntax/reference.html).

Additionally, all documents should be formatted to pass the Prettier linting
step required by the repository for Markdown documents.

When submitting a new document for a project, the author should open a pull
request with the document. The review process of the document will happen as a
PR review. Once the document is accepted and approved, it is merged and the
relevant step of the process is complete.

## Providing project updates

For all active projects (anything that isn't in the `Not Started`, `Completed`,
and `On Hold` statuses), fortnightly public updates are the best way for
Openverse contributors and maintainers to understand the health of a project.
Importantly, these updates allow us to allocate more time or material resources
to projects that need them before work stalls completely. They also help
identify projects that have stalled and may need special attention, if they
haven't seen an update in some time.

Project updates should be left as comments in the project threads by the project
lead or anyone working on a project. If you merge a significant PR related to
the project or identify a bug that impacts an open project, please leave an
update! Even if the update is "the project is blocked." or "No developments this
week.", the updates should still be posted. This removes ambiguity for folks
visiting the project, avoiding questions like "I don't see an update this week;
is it being worked on or not?"

These updates are useful for folks checking in on a project but also for the
project lead. It's an opportunity to _reflect on_ the status of the project and
any blockers, or successes to be shared.

Here are some real-life examples of useful project updates:

- https://github.com/WordPress/openverse/issues/377#issuecomment-1566296377
- https://github.com/WordPress/openverse/issues/392#issuecomment-1574444963
- https://github.com/WordPress/openverse/issues/433#issuecomment-1560213117

There are automated reminders configured for these updates via a
[daily GitHub action](https://github.com/WordPress/openverse/blob/main/.github/workflows/project_thread_update_reminders.yml)
that comments on the project thread, prompting the project lead to provide an
update.

## Project Lifecycle

There a few stages in the project process. None is inherently more important
than the next. At each stage of the project lifecycle, an appropriate status
will be applied to the project thread. The correct status can be found in the
title of each project lifecycle section. You can find a
[list of all statuses](#project-statuses-reference) at the end of this document.

### Creation (`status: Not Started`)

When contributors have decided to work on a project, we immediately create a
project thread to capture this intent. You can use
["Project Thread" issue template](https://github.com/WordPress/openverse/blob/main/.github/ISSUE_TEMPLATE/project_thread.md)
to create a new project thread. At this point, it is okay if we don't have any
of the metadata for the project. Please just fill in as many of the fields in
the
[template](https://github.com/WordPress/openverse/blob/main/.github/ISSUE_TEMPLATE/project_thread.md)
as you can.

The post should include a small description explaining the goal and outcomes of
the project. For example:

> This is a project thread for using a cookie to store user session information,
> especially information related to preventing layout shift caused by server
> rendering and media queries.

This stage is the smallest and is meant to express our intent to work on the
project. At this time it is important to link to any background on the project
that could help the eventual project lead. Some ideas for this content include:

- Links to existing issues or draft PRs related to the project
- References to similar functionality in other projects, or 3rd party
  documentation for a relevant integration
- Links to past chat threads related to the project

In conclusion, the deliverable for this stage is a new project thread which
expresses our intent to work on a feature and why. The project thread should
also be added to our GitHub Project Board, which can be done using the
"Projects" section of the sidebar when viewing an issue in the GitHub UI. To
learn more about our use of project boards please see the
[Managing and working with projects](#managing-and-working-with-projects)
section of this document.

### Kickoff (`status: In Kickoff`)

- [Kickoff/Project Proposal template](./templates/project-proposal.md)

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
7. A list of the requested technical implementation plans for the projects. Some
   projects will require multiple implementation plans (one for each the
   catalogue, API, and frontend, for example), and capturing that now will help
   understand the scope of the planning and implementation work that will arise
   down the road.

Leads are not expected to know the answers to all of these questions. Rather,
leads should **ask questions** directly in the document, tagging relevant
contributors who can bring needed expertise and guidance. The goal is to lead
the process of requirement and assumption discovery.

> **Note**
>
> **On Analytics**: Leads must endeavour to describe metrics and analysis that
> should be completed before the changes for the project's ultimate goal are
> implemented. Whenever possible or relevant, projects should have success
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
["Project Proposal" PR template.](https://github.com/WordPress/openverse/blob/main/.github/PULL_REQUEST_TEMPLATE/project_proposal.md)

#### The review process

Project proposals will be open for a two-week review period. In cases where
relevant contributors are AFK or otherwise unavailable, or a project proposal
experiences low engagement for a number of reasons, project proposal deadlines
will be extended by one week at a time as-necessary.

#### Wrapping up

Finally, the plan is merged, then the project thread is given a substantial
update. At this point we should be able to fill in most project metadata and
some additional details:

- Create GitHub issues for all necessary implementation plans and link to them
  in the project thread body. This allows implementation plans to be assigned
  and scheduled properly.
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

At this point it may be relevant to share our intent to work on this project to
a larger audience outside of our contributor base. It might also be a good time
to connect with any external collaborators and share the project details with
them.

### Implementation Plans (`status: In RFC`)

- [Implementation Plan Template](./templates/implementation-plan)

Implementation plans are the next type of RFC created for a project. The main
goal of an implementation plan is to produce a discrete and ordered list of
steps for implementing the project's requirements. As much as possible, these
steps should be organised into parallelisable work streams that can be
distributed across multiple team members (if desired).

Implementation plans share some philosophical goals with project plans. They
should seek to uncover and discover new or unforseen details about a project.

#### Required content

Every plan should accomplish the following:

- Describe a step by step process for implementing the project.
- Identify tools and dependencies of the project.
  - Examples:
    - New PyPI, NPM, or binary dependencies added by the project
    - Infrastructure that will need to be provisioned or modified
      - In particular, identify significant/unprecedented cost increases or
        decreases associated with related infrastructure changes.
    - New cloud services, paid or otherwise
      - Explore when we will need to start paying, free trials, non-profit
        pricing, etc.
  - If there are multiple options for any of these, identify relevant pros/cons
    of the different choices. Make a recommendation or ping for specific help to
    decide.
- Identify any design requirements of the project.
- Identify work-streams that can run in parallel.
- Identify work dependencies, especially cross-project dependencies that will
  need to be coordinated. For example:
  - List feature flags that will be used
  - Will a frontend feature be blocked by an API feature?
- Explore API version conflicts and ensure that versioning is respected
- Identify hard blockers that will prevent further work on the project
- Identify areas of technical ambiguity that cannot be predetermined during
  planning (i.e., after we've implemented _x_, we'll be able to make an informed
  decision about _y_).
- Identify atomic blocks of work so that work can be split into individual,
  small, easily reviewable PRs
  - Ideally PRs can be reviewed by anyone capable of reviewing in the relevant
    parts of the codebase, not only people intimately familiar with the project
  - This isn't always possible, but it is good to strive for it as much as we
    can
- Any milestones. Moments when significant or discrete chunks of work have been
  completed, or sub-features can ship.
- Any accessibility concerns or requirements.
- Rollback
  - How do we rollback this solution in the event of failure?
  - Are there any steps that can not easily be rolled back?
- Privacy
  - How does this approach protect users' privacy?
- Localization
  - Any translation or regional requirements?
  - Any differing legal requirements based on user location?
- Risks
  - What risks are we taking with this solution?
  - Are there risks that once taken can’t be undone?
- Prior art
  - Include links to documents and resources that you used when coming up with
    your solution.
  - Credit people who have contributed to the solution that you wish to
    acknowledge.

> **Note**
>
> We do not have any recommendations about time estimates in this section.

#### The review process

Technical implementation plans will be open for a two-week review period. In
cases where relevant contributors are AFK or otherwise unavailable, or a
implementation plan experiences low engagement for a number of reasons,
implementation plan deadlines will be extended by one week at a time as
necessary.

#### Wrapping up

Finally, the implementation plan is merged into the repo. Project contributors
create GitHub issues for all of the work identified in the implementation plan.
This process can be quite time-consuming for large projects. Generally, it makes
sense to create issues in the order which they must be completed; this allows
work to begin if, for some reason, there is delay in creating issues for work at
the end of a project. It also however makes sense to prioritize issues that are
"good first issues" and "help wanted" issues contributors outside of the core
maintainers can help with.

It is important to make sure dependencies are documented when creating these
issues. Issues which depend on another issue or set of issues should be labeled
as "blocked" and reference the blocking issue(s).

Whenever possible, issues should be written so that an implementer can complete
an atomic unit of work without needing to understand the full scope and
technicalities of the project. The issue description should contain all
necessary information to complete the issue. This can include linking to
specific relevant sections of the existing implementation plan(s).

### Implementation (`status: In Progress`)

In the implementation phase, contributors begin work on the project. At this
point the work has been divided into discrete tasks and ordered according to
priority. Contributors should feel the benefits of all the planning and textual
material generated in earlier phases. For the most part, contributors should
feel as though they are just able to "do the work".

It's likely during implementation we'll come across faulty assumptions or new
problems which require design. It is important that any realization like this
which blocks or delays the delivery of the project be clearly documented in the
project thread updates.

Ideally, issues stand on their own and do not require reading the full
implementation plans. For some issues, complexity prevents this from being
possible. If the contributor working on an issue is still unable to achieve
clarity on the details of an issue, even after reading the relevant parts of the
implementation plan, this would be a signal that details were not sufficiently
captured during implementation.

If at any point during implementation, it is discovered that the implementation
planning did not sufficiently capture the details of the project, we will put
the project back into a planning status. Someone familiar with the broader scope
of the project will be assigned to explore the discovered discrepancies and
sufficiently resolve them for the project to continue in confidence.

This is distinct from when the implementation plan has explicitly called out
that an ambiguity exists that will need to be resolved after a specific part of
the implementation is complete. The main idea here is that if at any point
during implementation, contributors are unclear on what they are meant to
implement or how they're meant to implement it, and this wasn't an expected part
of the project during planning, then something potentially big was missed during
planning.

In these cases, it is worth taking a step back to ensure that the full scope of
the plan is defined and being followed.

#### Notes for Implementers

With sufficient planning, it may make certain issues able to be easily
implemented at the same time, in a single PR. However, this should be avoided.
The implementation plan will have split the work into small, atomic, and
digestible chunks of work that progress the project at an appropriate pace. Keep
in mind that small PRs are reviewed _much_ faster than bigger PRs. While
implementing two or three issues in one go may _feel_ faster, it is often slower
and riskier, due to increased review overhead, than going step-by-step.

#### Notes for code reviewers

Code reviewers should focus primarily on the technical aspects of the
implementation required by the issue. At times, during the course of a project,
unforeseen ambiguities will discovered during implementation and sometimes an
alarm bell must be rung. However, these should be reserved for issues that will
cause long-term harm to the project. Merely disagreeing with a particular detail
of the project's implementation details is not sufficient for holding up a PR
that is part of a larger, carefully planned project, for which a technical
implementation plan has already been reviewed and approved. Therefore, avoid
raising objections to the broad technical decisions of a PR unless they do cause
long term harm to the project. This allows projects to move along at an
expedient pace and trusts that the project planners did their due diligence in
considering alternatives.

Of course, exceptions to this do exist and reviewers are expected to point out
when there is a significant issue with the implementation details of a PR that
will cause long-term harm.

Reviewers should also be mindful to point out when an implementer has
implemented multiple issues in a single PR, in a manner which makes reviewing
difficult or much more time-consuming.

### Delivery (`status: Shipped`)

After shipping, the project enters a period of evaluation. We do this to measure
the success of the project and determine if it achieved the desired goal, but
also to reflect on and make improvements to our own team processes.

The success criteria for this phase are determined and refined in earlier stages
of the project. At this point we should have a set of measurable criteria by
which to evaluate the project. This might be things like analytics events around
usage of a feature; a reduction in or the disappearance of a production bug; or
changes in traffic to Openverse, as examples.

During this phase, the project lead should report updates on these metrics
regularly to help the team make a determination about changing the project
status to `Success` or `Rollback`. Please make these updates on the project
thread using the [standard suggestions](#providing-project-updates). Rolling
back a project is not a decision we should take lightly, and by providing
regular updates project leads can prevent this action from seeming like a
surprise or a rash decision to others.

Frequent feedback on the success criteria can also help contributors come up
with fast-follow improvements or modifications to the feature that may prevent
rollback. Project leads should identify these types of improvements in their
project thread updates as well.

After the designated evaluation period we will make a decision about rolling
back the project, or marking it as successful.

> **Note**
>
> If a shipped project is erroring or otherwise disrupting service to Openverse
> users, the project should be rolled back immediately, regardless of the
> evaluation period.

### After Completion (`status: Success`, `status: Rollback`)

Finally, the team should take some time to reflect on the project. A
project-specific retrospective should be held between the contributors and
stakeholders of the project.

If the evaluation period of a project is longer than one week, consider holding
the retrospective _before_ the project is resolved. It is important that a
retrospective is timely and happens as close to the experience of a project as
possible.

This may also be a time to make any marketing or other public announcements
about a project, if relevant. Marketing and communications work should be scoped
in the earlier project stages but is likely to be implemented here.

## Managing and working with projects

We use a new
[Github Project Board](https://github.com/orgs/WordPress/projects/70/views/1) to
track all of the projects in Openverse. This board gives us a single view to see
all projects and some additional metadata:

- The lighthouse goal assigned to each project
- Estimated start/end dates for the project
- The status of the project

At the time of writing, projects are added to this board manually. In the future
we may develop automations, for example one which automatically adds any issue
with the "project" label to this board.

This board should be checked regularly as a 'dashboard' to answer some critical
questions:

- Are we making progress on our current open projects?
- Are there any projects we should put on hold?
- Are any projects blocked or in need of major intervention?
- Are there any projects we need to start now, or soon, in order to meet our
  goals for the year?

### Project Statuses Reference

Here is a description of each project status.

- `Not Started`: Has not started yet.
- `In Kickoff`: Project proposal is in progress.
- `In Rfc`: Technical implementation plan is in progress.
- `In Progress`: Under active development.
- `On Hold`: Stalled or blocked after work started.
- `Shipped`: Launched. Success criteria are under evaluation.
- `Success`: Completed. Success criteria are met.
- `Rollback`: Completed. Success criteria are not met. Work is reverted.
