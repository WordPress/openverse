# Process description

## Terms

- "Participants": The author, all requested reviewers, and any additional
  discussion participants.
- "Problem": A problematic aspect of the proposed solution, whether objective or
  subjective.
- "Objective problem": A problem that does not depend on an individual's
  perspective, i.e., something illegal, impossible, or too expensive.
- "Subjective problem": A problem regarding a matter of preference, e.g., a
  choice between two roughly equivalent and usable tools.
- "Blocker": A problem with a proposed solution that would cause lasting harm to
  the project or its contributors.
- "Fixable blocker": A blocker that can be addressed by revising the proposal.
- "Unworkable blocker": A blocker that cannot be addressed by revising the
  proposal. In other words, a problem that requires an entirely new proposal to
  be addressed.

## Process overview

The process is split into a series of rounds with broad expectations explained
below. Each step has a particular goal that participants should keep in mind.
The decision and continued revision round can repeat as many times as needed, at
the discretion of the participants.

| Round                                                 | Suggested span      | Goal                                                                          |
| ----------------------------------------------------- | ------------------- | ----------------------------------------------------------------------------- |
| [Clarification round](#clarification-round)           | 5 days              | Clarify the proposal; share initial thoughts                                  |
| [Revision round](#revision-round)                     | Author's discretion | Update the text of the proposal to reflect the outcome of the previous round  |
| [Decision round](#decision-round)                     | 3 days              | Decide whether the proposal can be implemented as is                          |
| [Continued revision round](#continued-revision-round) | Author's discretion | Work with participants to revise the text of the proposal to address blockers |
| [Approval](#proposal-approval)                        | N/A                 | Mark as approved and create issues to implement the proposal                  |
| [Tabling](#proposal-tabling)                          | N/A                 | Indicate that a proposal will not be implemented                              |

### Time spans

The suggested spans are just that: suggestions. If a particular proposal needs
more time for any reason, participants should note that and extend the round
duration. If reviewers are taken away from reviewing a proposal due to
extenuating circumstances like a production incident they need to be involved
in, they should note their unavailability on the discussion as soon as possible.
This expectation to notify of course does not apply if someone is taken away to
deal with life circumstances or other unexpected time AFK.

In any case, participants will work together to decide whether the proposal can
wait or if another person should be requested to replace the unavailable person.

Additionally, participants should try to maintain accountability to the
agreed-upon time spans. This means responding in a timely manner within the
window provided, understanding that authors will also need time to respond to
feedback, and following the practice described above to make explicit when they
will not be able to do so.

### Diagram

```{mermaid}
flowchart TD
    A[Proposal] --> B(Clarification Round)
    B -->|"Time: ~5 days"| C("Revision Round (if needed)")
    C -->|Time: As needed/estimated by author| D(Decision Round)
    D -.->|Fixable blockers identified| E
    E("Continued Revision Round (if needed)")
    D -.->|No blockers identified| H
    E --> D
    D -.->|Unworkable blockers identified| G
    G[Proposal tabled] -->|New proposal needed| A
    H[Proposal approved] --> I((End))
```

## Round descriptions

> **Note**
>
> While each round includes discussion guidelines and a description of purpose,
> these are flexible. Participants should use their discretion and should adapt
> the process as needed for any given proposal. If a blocker is apparent at the
> start of a discussion, do not wait for the decision round to share it. If a
> solution is known to be illegal or impossible, share that as early as
> possible. Additionally, if a proposal document has a structural issue that
> belies clarification, authors may revise to fix the proposal as soon as the
> problem is identified.

### Clarification round

The goal of this round is for participants to clarify the proposed solution and
share their initial thoughts and feelings about the proposal. We especially
encourage reviewers to look for opportunities to share explicit praise where it
is due. The broad focus should be on ensuring all participants understand what
is being proposed and why other potential solutions, if any reasonable ones
exist, were not chosen. By ensuring participants understand a proposal and that
the author has a chance to revise any initial problems identified during
clarification, we hope to cultivate an increased sense of trust: both that
reviewers are reviewing in good faith and that the author's work is respected
and understood to be the best attempt at proposing a solution to the problem.

During this round authors should refrain as much as possible from making large
changes to the proposal other than editorial/proofreading ones. This is to help
minimise confusion caused by a proposal that is changing while also being
reviewed for clarification.

#### Purpose

Proposals must all include an explicit "purpose". Often these are informed by
the needs of a particular project associated with the proposal or with a
requested discussion as the result of a retrospective or other self-feedback
mechanism. However, contributors may, at their discretion, raise proposals for
discussion that do not have prior conversations. In these cases, the
clarification round is also understood to include an evaluation and
clarification of the purpose of the proposal. For regularly requested proposals,
however, the purpose is taken to be accepted and should not be the focus of the
discussion.

### Revision round

The goal of this round is for authors to incorporate the feedback received in
the clarification round. At this time, any changes can be made to the proposal
document.

When the round starts, the author should share how long they will need to finish
revising the document. This helps give clear expectations for reviewers for when
they will need to return to the discussion and also establishes accountability
on the part of the author. Together these help prevent discussions from dragging
on or having an indefinite "slump" during revision.

### Decision round

The goal of this round is for the participants to decide whether the proposal
can be implemented in its current form. The focus of this round should be to
carefully consider any problems present with the proposal and decide whether
they are blockers or whether they can be iterated on after the initial
implementation. If further clarification is needed about an aspect of the
proposal that could cause harm, that is automatically considered to be a
blocker. If problem is a blocker, then reviewers should request changes to
address the issue, if it can be addressed. If the blocking issue cannot be
addressed (it is "unworkable"), then the proposal is tabled, though this should
be rare. Participants should all work together to help identify whether an issue
is truly a blocker or whether it is something that can be iterated on. Objective
problems should be given priority, whereas addressing subjective problems should
err on the side of avoiding the need for large revisions. If a proposal is
founded upon the usage of one tool, but another equivalent tool is also
available, it is up to the author whether they feel it is worth reworking the
proposal to use the other tool to appease the preference of the reviewer.

The idea behind this specific structure is two-fold:

- It acknowledges that Openverse maintainers are capable contributors and more
  often than propose solutions that are workable, even if they sometimes need
  revisions
- It makes explicit the expectation that we are looking for "good enough for
  now" solutions that can be iterated and improved on afterwards

Both of these help decision-making go faster, while also carefully identifying
what aspects of a proposal may need special attention either during
implementation or after the fact. Both of these are also, however, not steadfast
rules. Everyone makes mistakes and everyone can miss big or small details of a
problem that lead them down the wrong path. Working together as a team, all the
participants are tasked with deciding whether a solution is feasible and finding
ways to resolve blockers.

The suggested time span for the decision round is shorter for two reasons:

1. To encourage front-loading discussion during the clarification round
1. To acknowledge that the goal of the decision round is to decide whether the
   proposal can be implemented and iterated on or whether it has blockers

The decision round isn't necessarily another discussion round, aside from
deliberating about whether certain problems are blockers or not. Three days is
the suggested span because it allows time for at least one back and forth
between author and reviewers to decide whether problems are blockers. Further
discussion about the problems should continue during the subsequent revision
round between the person who identified the blocker and the proposal author.

### Continued revision round

If fixable blocking problems are identified during the decision round, the
author and participants should work together to revise the proposal to address
the problem so that it is no longer a blocker. This can be done either by
changing the proposal so that the problem no longer exists at all, or so that
the potential harm caused by the problem is mitigated. In other words, the
problem could still exist (whether objectively or subjectively), but the harm
caused by it is either no longer possible or sufficient guardrails or safety
measures have been taken to mitigate and address the harm or make it reversible.

After the revision is complete, the proposal goes back to the decision round.
The decision round and the continued revision round can repeat as many times as
needed until a proposal no longer has blockers.

### Proposal approval

Proposals are approved when the requested reviewers have voiced approval and
there are no outstanding blockers.

At this stage, authors will create any new milestones or issues to track the
work needed to implement the accepted solution. Milestones should be linked in
the proposal text.

### Proposal tabling

Proposals are tabled when unworkable blockers are identified. In cases where a
proposal was requested as part of a project, a new proposal should be requested
that approaches the problem in a new way to avoid causing the same problems.
