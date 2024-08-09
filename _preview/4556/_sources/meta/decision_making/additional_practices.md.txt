# Additional practices

The goal of the practices described in this document are to help the team adhere
to the general guidelines of the
[decision-making process](./process_description.md) without overburdening
participants with too many discussions.

## Current-round call out

In the PR description or top-post of a GitHub discussion, discussion leaders
should include the following text:

```md
This discussion is following the Openverse decision-making process. Information
about this process can be found
[on the Openverse documentation site](https://docs.openverse.org/meta/decision_making/index.html).
Requested reviewers or participants will be following this process. If you are
being asked to give input on a specific detail, you do not need to familiarise
yourself with the process and follow it.

## Current round

This discussion is currently in the **{Clarification, Revision, Decision,
Continued Revision} round**.

The deadline for review of this round is **{date}**
```

When a round ends, discussion leaders should leave a comment announcing the next
round along with the length of time allotted for it.

## Discussion dashboard

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

### Column descriptions

For the most part, the columns correspond 1-to-1 with rounds of the Openverse
consent decision-making process. However, the following columns are unique and
bear explanation:

- "Proposal requested": This column is meant for requested proposals or
  discussions for which no formal proposal yet exists. This column should be
  populated by the issues that document the request.
- "Discussion pending": This column is meant for proposals that have been
  written, but cannot yet start the decision-making process (likely due to
  contributor unavailability).

## Minimising parallel discussions

In the past, Openverse maintainers have been prone to feeling overwhelmed or
over encumbered by too many ongoing discussions demanding their attention. The
following practices are meant to mitigate the chances of this happening by
creating tools and processes for keep the number of active discussions per
participant to 2 or fewer.

### Checking the dashboard

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
- If a discussion could happen synchronously (if all participants have time
  available), then you may be able to pull people in who are waiting for a
  discussion to restart during the revision round, even if they're already
  participating in the discussion

In either case, it is still courteous to check with the individuals and make it
clear that they can push the discussion to someone else (provided they're not a
necessary subject-matter expert).

### Project level process discussions

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
   time-sensitive discussions and could lead to synchronous "lightning process"
   meetings to make faster decisions and reduce the ongoing discussion burden on
   team members. Even in this case, limit to 1 ongoing team-wide process
   discussion per group of contributors. This is less useful if everyone on the
   team wishes to give input in the discussion, although people are free to
   asynchronously give input before the fact.

For both, we will aim to limit the process discussions to one discussion at a
time for any given team member. This is recommended to avoid discussion burn out
as I think I've observed process discussions feeling much heavier weight and
burdensome than technical discussions. It also makes sure there is still room
for team members to be involved in one other separate technical discussion and
feel like they can still focus on their other work duties.

## Speeding up decision-making

The base process should help the Openverse project make decisions more quickly
and effectively. However, the following additional practices are available to
help move things along at an even faster clip, if so desired.

### "Shortcutting" a round

At any point during a round, any participant may say something along the lines
of "no (further) discussion needed on my part" in order to short-cut their
participation in the round. If all participants are finished sharing their part
in a given round, the author can choose to move to the next round, even if the
time period for the round has not been completed. This can be particularly
helpful for simpler discussions.

### Going synchronous

If all the participants of a particular discussion are able to participate in a
synchronous decision-making process, they may elect to do so. This can be
particularly useful for relatively small but impactful decisions where the
discussion periods would unnecessarily drag the process out. In these cases,
participants should hold a synchronous conversation with the understanding that
someone will take notes for each round, recording the feedback shared. **The
notes should be shared afterwards in the original proposal venue and should
include explicit headings per round.** If necessary, the synchronous discussion
can be broken into two separate sections to allow time for revision.

Even in these cases, however, the text of the proposal should still be written
in a GitHub PR or discussion and available for all participants to read _before_
the lightning process.
