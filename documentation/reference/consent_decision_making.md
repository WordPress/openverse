# Consent decision-making

The Openverse project uses a decision-making model based on
the
[Sociocracy practice of "consent decision-making"](https://patterns.sociocracy30.org/consent-decision-making.html).
We hope this will accomplish the following:

- Bring expediency to decision-making by giving guidelines for how and what
  types of feedback to give
- Clarify the types of feedback expected during the decsion-making process, including which types of feedback must be addressed and which are marginal 
  before a proposal can be ratified for implementation
- Give specificity in feedback expectations, both for who will participate in a
  decision-making process and what responsibilities and tools they have for
  participating
- Reaffirm trust between contributors when evaluating proposals

Historically, each of these have presented problems for the Openverse project as
it has grown. Decision-making can drag on for months, proposal reviews get stuck
in feedback cycles over issues that could be addressed later on, and there were
few, if any, expectations around who would participate in a discussion or what
the expectations of that participation was. Adopting the process described
below, we hope, will address some of the underlying causes of these problems, in
addition to the benefits described above.

The process described below is heavily modified from the regular Sociocratic
process. The differences come from two directions:

- The needs of an asynchronously coordinated base of contributors
- Internal feedback and iteration on the initial process, even after
  modification for asynchrony

> ## When to follow this process
>
> Whether this process is followed for any given proposal or discussion is left
> entirely to the discretion of the people relevant to the discussion. We
> believe that this process helps the project's contributors make expedient and
> clear decisions. However, it should not become an obstacle that is followed
> for every tiny decision. If a decision can efficiently be made without this
> process, contributors are invited to do so.
>
> For the purposes of project planning, however, this process should be the
> default and should be the strong preference, keeping in mind that it can be
> made faster via [round shortcutting](#shortcutting-a-round) and the
> [synchronous lightening process](#optional-synchronous-lightening-process).

## Continuous improvement and exceptions to every rule

**This process is not set in stone.** Nor is it a set of laws that must be
followed at all times. This document uses prescriptive language filled with
imperatives primarily to prevent the process itself from being filled with
contingencies at every turn. However, as with every other aspect of our ever
evolving processes, these are merely suggestions that we expect contributors to
adhere to. They cannot cover every situation and undoubtedly there are
exceptional situations where following these suggestions to the letter would be
antithetical to the goals of the project and even of the process itself.

If during your time as an Openverse contributor, you feel there are ways in
which this process can be improved and iterated upon, please know that this
process should be iterated upon and that suggestions for improvement are open
from any contributor to the project.

## Terms

- "Author": The person making the proposal.
- "Participants": All participants of the decision-making process, including the
  author, the requested participants, and ad-hoc participants.
- "Reactions": A broad class of feedback that can include personal preferences
  as well as general doubts about the validity or safety of the solutions
  described in the proposal.
- "Question": A request for clarification, explanation, or additional information about an aspect of the proposal.
- "Objection": An explained uncertainty about the appropriateness, efficacy, or
  safety of a solution
- "Paramount objection": An objection outlining an issue that would cause harm
  to the project or its contributors; especially issues that could cause harm
  and are difficult to reverse and not strictly necessary to accomplish the
  goals of the project
- "Ratified proposal": A proposal that has undergone the formal decision-making
  process and has been accepted as a valid solution by the participants of the discussion.
- "Process proposal": A proposal to change processes followed by the
  contributors in the course of stewarding the project towards success.
- "Purpose": The motivation for the proposal. This is typically a statement
  describing the problem the proposal aims to solve. In the original Sociocratic
  model this is called the "driver".

## Major differences from the original process

Aside from being conducted primarily as an asynchronous process, Openverse's
consent decision-making process has the following major differences from the
Sociocratic model.

### Reactions

While the original process has a separate reactions round, in Openverse's
process, reactions can be shared at any time. Be careful to ensure that they're
not objections (which should, with few exceptions, be reserved for the objection
round). Examples of reactions are:

- "I love this approach"
- "I like this proposal, but I don't understand X part of it yet"
- "I don't think this will work, but I left some questions to clarify the areas
  I have concerns over"
- "I don't understand the underlying problem, so the solution seems too abstract
  to me"
- "I don't think this solution will solve the problem as described"

Note that these are not questions (they do not ask for clarification) nor are
they objections (they do not point to specific problems with the proposed
solution).

### Removal of initial rounds

Because our process is primarily asynchronous, because our decision-making
happens in public, and because the outcomes of our discussions are ultimately
documented in GitHub or other accessible venues, we can skip some of the initial
rounds. Specifically, the "consent to driver" and the "present the proposal"
rounds cannot work in the same way. Typically, the purpose of a proposal will
have been clarified through a previous discussion. Proposals raised without
prior "buy-in" from other contributors should be done so carefully, with the
understanding that participants may question the purpose and need for the
proposal. The presentation of a proposal happens implicitly when the GitHub PR
or discussion is opened to contain the proposal, so we do not need a special
step for this.

## Process summary

Full descriptions of each of these rounds of discussion are below. This section
is meant as a summary for getting an initial overview for people new to the
process or refreshing the broad intentions for folks already familiar with it.

These steps are ordered and must be followed in the order they are presented
here.

> **Nota bene**: The "goal" column is a very brief summary and is not intended
> to encapsulate the full scope of the round. Please refer to the
> [round descriptions below](#round-descriptions) for more details and examples.

| round                                                 | Suggested span      | Goal                                                                                      |
| ----------------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------- |
| [Question round](#question-round)                     | 3 days              | Clarify the proposal; share initial reactions                                             |
| [Revision round](#revision-round)                     | Author's discretion | Update the text of the proposal to reflect the outcome of the previous round              |
| [Objection round](#objection-round)                   | 2 days              | Identify paramount and non-paramount objections                                           |
| [Objection revision round](#objection-revision-round) | Author's discretion | Work with participants to revise the text of the proposal to address paramount objections |
| [Ratification](#ratification)                         | N/A                 | Mark as accepted and create issues to implement the proposal                              |
| [Tabling](#tabling)                                   | N/A                 | Indicate that a proposal will not be implemented                                          |

## Proposal requirements

Project proposals and technical implementation plans should follow the formats
outlined in [the documentation for those processes](./docs/projects/README.md).
All proposals should include a summary of the purpose of the proposal and the
problem(s) it attempts to address.

Every proposal must include the following boilerplate text in the PR description
or at the top of the GitHub Discussion:

```md
## Decision-making process

For the purposes of this discussion, we will follow
[Openverse’s decision-making model](https://wordpress.github.io/openverse/reference/consent_decision_making.html).
Please note that this process follows formalised steps with specific
expectations of participants. Before contributing, please read
[this document](https://wordpress.github.io/openverse/reference/consent_decision_making.html)
as well as
[Openverse’s Code of Conduct](https://github.com/WordPress/openverse/blob/main/CODE_OF_CONDUCT.md).
Please note that the consent decision-making document linked above also includes
instructions for opting out of a decision discussion you do not wish to
or cannot participate in.

## Current round

The discussion is currently in the **{Question, Reaction, Revision, Objection
raising, Objection revision}** round.
```

## Round descriptions

The following general guidelines apply to all rounds:

- Reactions may be shared at any of the "feedback" rounds (Question and
  Objection).
- Proposal authors are not obligated to respond to every question, reaction, or
  objection that is raised, except for paramount objections. While there is an
  expectation that the author will address outstanding questions, it isn't
  necessary to respond to every non-paramount objection before moving on to
  subsequent rounds or ratifying the proposal. It is, of course, in the best
  interest of the project and the proposal that as much clarity as possible is
  achieved.
- Authors may table a proposal at any time at their discretion. If the proposal
  is tabled, discussion should not be expected to continue, but may, if there is
  something important being discussed.
- Any round with a suggested length of time is subject to
  [shortcutting as described below](#shortcutting-a-round) or to extension at
  the discretion of the participants.

### Question round

This round lasts for 3 business days after the discussion starts but can be
extended if questions reveal significant gaps in the proposal that must be
understood before the proposal can be revised in the revision step. These
questions are different from objections in that they’re not in the form of "we
cannot do this because x part of the proposal will not work". Rather, they are
clarifying questions in the form of:

- "I don’t understand y in the proposal, can you clarify what is meant by this?"
- "I think a gap exists in the proposed solution here [clarify where]. Can you
  fill in the details in this area?"

In short, the goal of the question round is for everyone participating to fully
understand the proposal. Participants are urged that many objections can be
restated as questions. This helps promote good faith between participants and
allows the author to clarify things they might have missed in the initial draft
of the proposal. This does _not_ mean that known paramount objections should be
reserved by participants. If you know that a proposed solution is impossible or
illegal, please do raise this concern as soon as possible.

Note that the author does not have to respond to every question. However, they
should keep them in mind during the revision round.

#### Reactions

This round also invites participants to share reactions, positive or negative,
separate from potential paramount objections. This is an excellent round
to highlight positive aspects of the proposal, regardless of any paramount 
objections. You may also share non-paramount
objections at this round. For example, “I find JavaScript harder to work with
than Python” is an objection but not a paramount objection. What makes an
objection “paramount” is clarified further in the
[Objection round](#objection-round) below.

Reactions are expected during this round because, similar to questions,
they can help prompt further clarification from the author to be address in the
revision round.

#### Purpose

Proposals should all include an explicit "purpose". Often these are informed by
the needs of a particular project associated with the proposal or with a
requested discussion as the result of a retrospective or other self-feedback
mechanism. However, contributors may, at their discretion, raise proposals for
discussion that do not have prior conversations. In these cases, the question
round is also understood to include an evaluation and clarification of the
purpose of the proposal. For regularly requested proposals, however, the purpose
is taken to be accepted and should not be the focus

### Revision round

At this round, the author has the opportunity to revise the proposal in response
to the questions and reactions raised. This round has no set time period. The
author should use their discretion and give an expected time when the revised
version will be ready. The expected date of completion for the revision is both
for accountability (to prevent projects from being stalled indefinitely) and for
clarity of expectations for the other participants in the process. If the author
requires additional time beyond their initial estimation, they should let the
other participants know as soon as possible, keeping in mind that other
discussions may be stalled in the meantime.

**No revisions should be made to the proposal before
this point other than grammatical or spelling corrections**. The reason for this
is to allow the question round to fully complete without the proposal changing
during the discussion. This allows clarification to happen fully without having
to track ongoing changes to the proposal and sets the expectation that changes
the proposal incorporate all the clarifying questions asked in addition to any
information surfaced in the reaction round. This helps to minimise the
potentially "frantic" nature of a discussion that is happening about a proposal
document that is changing simultaneously with the discussion.

### Objection round

This round lasts for 2 business days. Participants are now invited to share
“paramount objections” to the proposal, if any exist. Objections are considered
“paramount” only if:

- They point to an issue that prevents the team from achieving its goals
  (whether these are technical, community, or interpersonal). These issues can
  also be said to "harm" the project or its contributors.
- The objection reveals something that is irreversible (or extremely difficult
  to reverse) of which the participants are not at least “okay” with or “sure
  of”. For example, a proposal to switch to using MySQL when we’re currently
  invested heavily in Postgres would require significant time investment that
  would be difficult to reverse. If the participants are not absolutely certain
  that it is the best decision, then any objection to making the switch would be
  paramount.

Note that during this round, like the question round, the author should not
modify the text of the proposal. The focus of the author in this round should be
to clarify objections (especially paramount objections) and decide whether
the proposal can address them. This
allows time for participants to fully digest the proposal and raise all
objections without further revision happening. Participants are expected to help
each other decide whether an objection is paramount. Whether an objection is
paramount can be questioned by the author, but they should prefer to defer to
the participants and trust their judgement.

If there are no paramount objections then the process has finished and the
proposal is [ratified](#ratification). In that case mark the discussion as
ratified, however this can be best done with the tool being used (merge the PR,
close the discussion, etc). The author is responsible for updating the “Current
round” text to signify the proposal’s ratification.

After the 2-day period, if the author does not think they can address
the paramount objections, then the proposal is [tabled](#tabling). For projects
where we absolutely want to implement, this should be rare.
However, sometimes a paramount objection may be raised that requires completely
re-writing the proposal from the ground up. In that case, we will follow this
process again from the start with the new proposal, so we will end the process
for the first proposal at this round and wait for a new one to be raised. In
these cases, the author should update the “Current round” text to note that the proposal was tabled and that a new proposal has been requested.

### Objection revision round

This round, similar to the previous revision round, lasts as long as the author
of the proposal needs it to last to completely address the paramount objections.
The author should work with the person who raised the objection to revise the
proposal to address the issue to resolution. The goal of this round is to reach
a "good enough" middle ground solution that either completely addresses the
paramount objection or mitigates the potential harm identified.

As stated in the previous round’s description, objection revision should only
happen if paramount objections can indeed be revised to remove the harm. If the
paramount objection involves a core issue of the proposal that cannot be
revised, then an entirely new proposal should be written, rather than the
"revision" replacing the entire existing proposal. It may be the case that in
the process of revision, the author of the proposal realises that they need to
"return to the drawing board". Please keep in mind that this is not a failure
and should be celebrated. So long as the objections were truly paramount, the
participants in the discussion and the author of the proposal have successfully
prevent long-term harm to the goals or people on the project. That is good news.

Once the paramount objections are addressed, we will consider the proposal to be
accepted. The team as a whole can move on the next step of the project, whether
that is implementation planning or implementation itself.

## Outcomes

There are two possible outcomes for any proposal that follows this process:
ratification or tabling.

### Ratification

Ratification occurs once all paramount objections have been addressed and the
author is satisfied with the state of the proposal. At this point any necessary GitHub issues should be created and linked to the proposal.

### Tabling

Tabling can occur in the following cases:

- At any time, at the discretion of the author
- Before a proposal is written, if the team reneges on a requested discussion
- After a proposal is written, but before the discussion happens, if it is clear
  the proposal will not fit the needs of the project
- During the objection round when insurmountable paramount objections are raised

In the final case, the participants of the discussion are responsible for
deciding whether a new proposal should be requested.

In any case, the proposal (if one exists) or the issue (if a proposal does not
exist) should be updated to reflect the tabled status and the reason why it was
tabled. It should also indicate whether a new proposal is requested. If a
proposal exists, the author is tasked with this responsibility. If no proposal
yet exists, then someone must volunteer to document the reasons for this
outcome.

## Additional practices

The following additional conventions will help our team make expedient decisions
while still following the formalised process laid out above.

### Discussion Dashboard

The
[discussion dashboard is implemented as a GitHub project](https://github.com/orgs/WordPress/projects/79/views/1)
for tracking the different rounds of a proposal. Proposal authors are expected
to correctly add and update proposals as they move through the different rounds
of discussion. This dashboard is used to
[help ensure we do not assign contributors to more than two discussions in parallel](#minimising-parallel-discussions),
so it is imperative that we maintain its accuracy.

Each discussion should be tracked as a single card, with issues removed from the
"Pending proposal" column if a GitHub PR is opened. If a GitHub discussion is
used for the proposal, because those cannot be represented in GitHub project
boards, the issue should be used to track the status through the columns.

This dashboard also serves as a record of decisions made on the team since the
dashboard's inception. Historical decisions that happened before the dashboard
started being used are not documented there.

#### Column descriptions

For the most part, the columns correspond 1-to-1 with rounds of the Openverse
consent decision-making process. However, the following columns are unique and
bear explaining:

- "Proposal requested": This column is meant for requested proposals or
  discussions for which no formal proposal yet exists. This column should be
  populated by the issues that document the request.
- "Discussion pending": This column is meant for proposals that have been
  written, but cannot

### Minimising parallel discussions

In the past, Openverse maintainers have been prone to feeling overwhelmed or
over encumbered by too many ongoing discussions demanding their attention. The
following practices are meant to mitigate the chances of this happening by
creating tools and processes for keep the number of active discussions per
participant to 2 or fewer.

#### Checking the dashboard

Before requesting participation from specific people on a discussion, check the
[discussion dashboard](#discussion-dashboard) to ensure they're not already
involved in 2 ongoing discussions. If specific participants are required for a
given proposal (due to the relevance of their expertise in the proposal), then
you may open the proposal, but it should be left in the "pending discussion"
column.

Tips for checking the dashboard and not accidentally over-encumbering people:

- Check for discussions in the "pending discussion" column. If someone is
  already assigned to discussions there, then know that any new discussions that
  _must_ involve them will need to be triaged with the other discussion
- If a discussion could happen using the "lightening process", then you may be
  able to pull people in who are waiting for a discussion to restart during the
  revision round, even if they're already participating in the discussion

In either case, it is still courteous to check with the individuals and make it
clear that they can push the discussion to someone else (provided they're not a
necessary subject-matter expert).

#### Project level process discussions

Because project level process discussions usually effect all maintainers and
sometimes other contributors, they naturally garner the expectation of
involvement from broader sets of people than technical discussions. In addition
to the guidelines above for general discussions, we need additional special
guidelines to ensure we do not become over encumbered with process discussions
specifically. In particular, retrospectives may give rise to several discussions
that need to happen at once. In these cases, and others where process
discussions begin to dominate the discussion backlog, we'll need to triage
discussions. If discussions truly need the involvement of the entire team, we
can follow two processes:

1. Put (and prioritise) the discussions into the "proposal requested" column of
   the discussion dashboard and only allow one team-wide discussion to occur at
   a time. Limiting this to 1 allows other non-team-wide discussions to also
   happen at the same time without flooding the discussion board with team-wide
   discussions and halting other, smaller, often technical discussions.
2. Split the group into groups of three or four people who can participate in
   different parts of the discussion. This is useful if there are multiple
   time-sensitive discussions and could lead to synchronous "lightening process"
   meetings to make faster decisions and reduce the ongoing discussion burden on
   team members. Even in this case, limit to 1 ongoing team-wide process
   discussion per group of contributors. This is less useful if everyone on the
   team wishes to give input in the discussion, although people are free to
   asynchronously give input before the fact.

For both, we will aim to limit the process discussions to one discussion at a
time for any given team member. This is recommended to avoid discussion burn out
as I think I’ve observed process discussions feeling much heavier weight and
burdensome than technical discussions. It also makes sure there is still room
for team members to be involved in one other separate technical discussion and
feel like they can still focus on their other work duties.

### Speeding up decision-making

The base process should help the Openverse project make decisions more quickly
and effectively. However, the following additional practices are available to
help move things along at an even faster clip, if so desired.

#### "Shortcutting" a round

At any point during a round, any participant may say something along the lines
of "no (further) questions", "no reaction", or "no objection" in order to
short-cut their participation in the round. If all participants are finished
sharing their part in a given round, the author can choose to move to the next
round, even if the time period for the round has not been completed. This can be
particularly helpful for simpler discussions where the 2 business day
recommended time periods can feel overly slow.

#### Optional, synchronous "lightening process"

If all the participants of a particular discussion are able to participate in a
synchronous version of the process outlined above, they may elect to do so. This
can be particularly useful for relatively small but impactful decisions where
the 2 business day periods would unnecessarily drag the process out. In these
cases, participants should hold a synchronous conversation with the
understanding that someone will take notes for each round, recording the
questions, reactions, and any objections that arise. **The notes should be
shared afterwards in the original proposal venue and should include explicit
headings per round.** If necessary, the synchronous discussion can be broken
into two separate sections to allow time for the revision round after reactions
are shared.

Even in these cases, however, the text of the proposal should still be written
in a GitHub PR or discussion and available for all participants to read _before_
the lightening process.

Differences in structure for the "lightening process" from the asynchronous
process are as follows:

- Rather than tying the question and reaction rounds together, they are separate
  rounds. Therefore, the rounds are as follows:
  1. Question
  1. Reaction
  1. Revision
  1. Objection
  1. Objection revision
- Each round should have notes taken clearly documenting the questions,
  reactions, objections, and discussions for each (as appropriate). Priority
  should be given to questions and objections that require revising the
  proposal.

## How to follow the process in different settings

The team has agreed to use GitHub for all discussions, with links shared on the
[WordPress Make Openverse blog](https://make.wordpress.org/openverse/) to help
visibility for certain discussions.

There are two tools in GitHub that can be used for conducting a discussion: PRs
and GitHub Discussions. We do not use GitHub issues because they do not allow
for threading.

### PRs

GitHub PRs are used for project proposals, implementation planning RFCs, and
other proposals that will be documented as Markdown files in the repository.

GitHub PRs have the following ways of interacting with comments:

- Inline comments on specific lines of text or code
  - These allow opening "threads" and can be resolved
- General PR comments
- Review comments

Each of these can serve their own purposes:

- Inline comments
  - These are perfect to supplement the question and objection rounds. If a
    question is about a specific part of the proposal (rather than a more
    general clarification), participants can leave the question directly on the
    part in question. Similarly, paramount objections specific to one part of
    the proposal can be left as inline comments attached to a review requesting
    changes.
- General PR comments
  - For questions or non-paramount objections raised regarding the proposal in
    general or for the reaction round.
  - In addition to the PR description, the author of the PR will also create a
    new top-level PR comment when a new round starts.
- Review comments
  - These should be used in the objection raising round. Leave an approving
    review if you have no paramount objections or "request changes" if you have
    a paramount objection. Attach inline comments as needed in either case.

### GitHub Discussions

Because the format is slightly more limited than PRs, we will have a top-level
comment per round created by the author. Responses from participants should be
contained within the thread for each round. However, paramount objections during
the Objection round, should be raised as individual threads. Still, the author
should still create a top-level comment closing the previous round and opening
the objection round. If the proposal goes into objection revision, the
discussion for addressing a given objection can happen in the accompanying
thread.
