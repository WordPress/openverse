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

> **Note** At some point between creation and kickoff we need to make a
> determination about who the lead of a project is. Often this has happened
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
infrastructural considerations or towards team processes and execution strategy.

#### Required content

Every plan should contain the following information:

1. Which of our year goals does this project advance?
2. How will we measure the success of this project? Share any new analytics
   tracking or metrics we will need to evaluate the success.
3. Who will work on the project? Consider any sponsored developers needed, along
   with any external contributors or collaborators who need to be involved.
4. Are there any infrastructural changes or costs associated with this project?
5. Is there any marketing outreach that should be coordinated with this project?
   How is the project presented and made visible to our users?
6. Will any outside stakeholders or communities need to approve parts of the
   project, or confirm their interest?

This required information does not mean that leads must fully understand every
aspect of a project. Instead, leads should **ask questions** directly in the
document, tagging relevant contributors who can bring needed expertise and
guidance.

#### Tone and audience

This document should be readable by anyone unfamiliar with the specific
implementation details of Openverse. The discussion should largely mirror this
and be about the intentions, assumptions, and expectations of a project rather
than the technical details of it (which are covered in the next step). As
projects often focus on providing value to our users, consider if this document
wer1e to be read by Openverse users, not just contributors. Would it effectively
convey the value of the work?

#### Formatting and process for Project Proposals

Proposals are delivered as Pull Requests to the `wordpress/openverse`
repository. Project proposals can be authored in any tool but are shipped as a
markdown file in the `rfcs/` directory, using a filename formatted as
`YYYYMMDD-proposal_title.md`.

The PR description should use the "Project Proposal" PR template [to be
created]:

```md
<!--
  This should be two weeks from the publish date of the proposal.
  One week extensions will be granted in the case of critical contributors being unavaliable or the author's personal avalibility.
-->

## Due date: yyyy-mm-dd

<!--
  Suggest two members of @WordPress/openverse to review the discussion.
  Please share the reasoning between choosing these members. Ideally authors should select for:

  - Relevant expertise or experience, or
  - Expressed interest in the project
-->

## Assigned reviewers

- [ ] TBD
- [ ] TBD

## Description

<!-- Start the conversation. Please @ anyone relevant and try to ask questions to help facilate discussion. Try not to repeat anything here that is better suited for the proposal itself.  -->
```

#### The review process

Project proposals will be open for a two-week review period. In cases where
relevant contributors are AFK or otherwise unavaliable, or a project proposal
experiences low engagement for a number of reasons, projects proposal deadlines
will be extended by one week.

Projects, their deadliens, and reviewers, will be added to our
[Action Items project board](https://github.com/orgs/WordPress/projects/59/views/1?query=is%3Aopen+sort%3Aupdated-desc)
for tracking with our other action items.

#### Wrapping up

Finally, the plan and technical proposals are merged and the project thread is
given a substantial update. At this point we should be able to fill in all
metadata, including some additional fields:

- Links to the kick off and technical implementation documents
- Links to any other external documents or supporting materials
- List stakeholders:
  - Implementers
  - Planners
  - Designers
  - Anyone else who is expecting the feature or has authoritative input over the
    project
  - Anyone who the implementers will depend on to be able to complete any of the
    steps of the project (no matter how obvious this might seem)
- Links to all milestones and relevant issues.

### Implementation RFCs (`status: in rfc`)

[TBD]

### Implementation (`status: in progress`)

In the implementation phase, contributors begin work on the project. At this
point the work has been divided into descrete tasks and ordered according to
priority. Folks who have _not read_ the motivating documents or who even lack a
full understanding of the project should be able to jump in and work on
individual pieces of the project by _exclusively_ reading the information
present in the GitHub issue or task they are being assigned.

> **Warning** If this isn't possible, planning was insufficient and we may want
> to place the project in `status: on hold` to re-adjust. It's a very important
> aspect of the work.

#### Providing project updates

Project updates should be left as weekly comments in the project threads. Even
if the update is "the project has stalled." or "No developments this week", the
updates should still be posted. This removes ambiguity for folks visiting the
project, avoiding questions like "I don't see an update this week; is it being
worked on or not?"

These updates are useful for folks checking in on a project but also for the
project lead. It's an opportunity to _reflect on_ the status of the project and
any blockers, or successes to be shared.

Here is an update template to be followed:

```md
## Update YYYY-MM-DD

_A very brief, nearly single line summary giving a cleardescription of the
project. Example: We continue to ship frontend PRs and are 75% complete with the
milestone. Blocked on design approval from community contributors for the new
signup flow._

### Done

_List recently-completed tasks here_

### Next

_List this week's tasks here_

### Blockers

_List any blockers for the week_
```

### Delivery (`status: shipped`)

Project completion is a time for celebration, and reflection.

### After Completion (`status: success`, `status: reverted`)

[TBD]

### Reference: Project Statuses

- `not started`: Has not started yet.
- `in kickoff`: Project proposal is in progress.
- `in RFC`: Technical implementation plan is in progress.
- `in progress`: Under active development.
- `on hold`: Stalled or blocked after work started.
- `shipped`: Launched. Success criteria are under evaluation.
- `success`: Completed. Success criteria are met.
- `rollback`: Completed. Success criteria are not met. Work is reverted.

## Open Questions

1. Should the lead of a project also be the primary implementor of the work,
   generally speaking? Should we actively avoid this? Does this relationship not
   matter?
