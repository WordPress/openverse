# Consent decision-making

The Openverse maintainers have elected to adopt a decision-making model based on
the
[Sociocracy practice of "consent decision-making"](https://patterns.sociocracy30.org/consent-decision-making.html).
We hope this will accomplish the following:

- Bring expediency to decision-making by giving guidelines for how and what
  types of feedback to give
- Adopt more specific standards about what types of feedback must be addressed
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

- The needs of a largely asynchronously coordinated base of contributors
- Internal feedback and iteration on the initial process, even after
  modification for asynchrony

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
  as well as general scepticisms about the validity or safety of the solutions
  described in the proposal.
- "Question": A request for clarification or explanation of an aspect of the
  proposal. Questions may also request additional information be added to the
  proposal.
- "Objection": An explained uncertainty about the appropriateness, efficacy, or
  safety of a solution
- "Paramount objection": An objection outlining an issue that would cause harm
  to the project or its contributors; especially issues that could cause harm
  and are difficult to reverse and not strictly necessary to accomplish the
  goals of the project
- "Ratified proposal": A proposal that has undergone the formal decision-making
  process and has been accepted as a valid solution for the problem it tries to
  address by the participants of the discussion.
- "Process proposal": A proposal to change processes followed by the
  contributors in the course of stewarding the project towards success.
- "Purpose": The motivation for the proposal. This often includes the problem
  the proposal aims to solve. In the original Sociocratic model this is called
  the "driver".

## Major differences from the original process

### Reactions

Reactions can be shared at any time. Be careful to ensure that they're not
objections (which should, with few exceptions, be reserved for the objection
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
stages. Specifically, the "consent to driver" and the "present the proposal"
stages cannot work in the same way. Typically, the purpose of a proposal will
have been clarified through a previous discussion. Proposals raised without
prior "buy-in" from other contributors should be done so carefully, with the
understanding that participants may question the purpose and need for the
proposal. The presentation of a proposal happens implicitly when the GitHub PR
or discussion is opened to contain the proposal, so we do not need a special
step for this.

## Process summary

Full descriptions of each of these stages of discussion are below. This section
is meant as a summary for getting an initial overview for people new to the
process or refreshing the broad intentions for folks already familiar with it.

These steps are ordered and must be followed in the order they are presented
here.

1. Question stage
   - Suggested span: 3 days
   - Goal: clarify the proposal and uncover initial uncertainties or issues
   - Note: at this point, participants may question the purpose of the proposal
     if it was not previously agreed upon in a previous discussion. If the
     proposal was requested as a product of an earlier discussion, then the
     purpose was already agreed upon and should not itself come under question.
2. Revision stage
   - There is no suggested time span, but the author should clearly note when
     they expect to finish revision and for the next stage to start
   - Goal: revise the text of the proposal to reflect discussions during the
     question stage
3. Objection stage
   - Suggested span: 2 days
   - Goal: identify unresolved issues that would cause harm to the team,
     contributors, or the project
   - Note: participants must clearly note whether each objection they raise is
     considered paramount or non-paramount in their own estimation
4. Objection revision stage
   - Suggested span: as long as it takes for the author and paramount objection
     raisers to revise the proposal together.
   - Goal: revise the proposal in collaboration with individual participants to
     address and resolve paramount objections
   - Note: if during this stage it is determined that the proposal cannot be
     revised to address the paramount objection(s), then the proposal is tabled
5. Ratification
   - Suggested span: N/A
   - Goal: if there are no paramount objections during the objection stage, mark
     the proposal as ratified and create issues to implement the proposal (if
     needed)
6. Tabling
   - Suggested span: N/A
   - Goal: to end discussions for proposals that cannot be ratified, either due
     to voluntary withdrawal of the proposal by the author or due to
     insurmountable paramount objections

## Proposal requirements

Project proposals and technical implementation plans should follow the formats
outlined in [the documentation for those processes](./docs/projects/README.md).
All proposals should include a summary of the purpose of the proposal and the
problem(s) it attempts to address.

## Stage descriptions

## Additional practices

The following additional conventions will help our team make expedient decisions
while still following the formalised process laid out above.

### "Shortcutting" a round

At any point during a round, any participant may say something along the lines
of "no (further) questions", "no reaction", or "no objection" in order to
short-cut their participation in the round. If all participants are finished
sharing their part in a given round, the author can choose to move to the next
round, even if the time period for the round has not been completed. This can be
particularly helpful for simpler discussions where the 2 business day
recommended time periods can feel overly slow.

### Discussion Dashboard

The
[discussion dashboard is implemented as a GitHub project](https://github.com/orgs/WordPress/projects/79/views/1)
for tracking the different stages of a proposal. Proposal authors are expected
to correctly add and update proposals as they move through the different stages
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

For the most part, the columns correspond 1-to-1 with stages of the Openverse
consent decision-making process. However, the following columns are unique and
bear explaining:

- "Proposal requested": This column is meant for requested proposals or
  discussions for which no formal proposal yet exists. This column should be
  populated by the issues that document the request.
- "Discussion pending": This column is meant for proposals that have been
  written, but cannot

### Minimising parallel discussions

#### Checking the dashboard

Before requesting participation from specific people on a discussion, check the
[discussion dashboard](#discussion-dashboard) to ensure they're not already
involved in 2 ongoing discussions. If specific participants are required for a
given proposal (due to the relevance of their expertise in the proposal), then
you may open the proposal, but it should be left in the "pending discussion"
column.

In addition to the general courtesy described in the previous section asking
authors to review the discussion dashboard before pinging individuals, we will
also want to have some practices to minimise team-wide process decisions. In
order to do this, we’ll need to triage discussions, in particular if a
retrospective brings up several important decisions that need to be made. In
those cases, if they’re truly decisions with team-wide implications, we can
follow two processes:

1. Establish a team-wide discussion backlog and only allow one team-wide
   discussion to occur at a time. Limiting this to 1 allows other non-team-wide
   discussions to also happen at the same time without flooding the discussion
   board with team-wide discussions and halting other, smaller, often technical
   discussions.
2. Split the team into groups of three or four people who can participate in
   different parts of the discussion. This is useful if there are multiple
   time-sensitive discussions and could lead to synchronous “lightening process”
   meetings to make faster decisions and reduce the ongoing discussion burden on
   team members. Even in this case, limit to 1 ongoing team-wide process
   discussion per team-member.

For both, we will aim to limit the process discussions to one discussion at a
time for any given team member. This is recommended to avoid discussion burn out
as I think I’ve observed process discussions feeling much heavier weight and
burdensome than technical discussions. It also makes sure there is still room
for team members to be involved in one other separate technical discussion and
feel like they can still focus on their other work duties.

### Current round call out

The author must maintain a heading at the top of the PR description, discussion
question, or P2 post with the current round the discussion is in. This prevents
accidental back-sliding into already completed rounds or jumping ahead to rounds
not yet started. The call-out is embedded with the informational block linking
to the process documentation. This is maintained in addition to the process
described below in the "How to follow the process…" section where the author
will add a top-level comment introducing each new round when it starts.

### Optional, synchronous "lightening process"

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

Even in these cases, however, the proposal should still be written in a GitHub
PR or discussion.
