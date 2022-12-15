# RFCs

The Openverse contributors have committed to writing RFCs for large features or
improvements that span multiple issues.

We write RFCs in Markdown and submit PRs for them to this repository to make
them easier to comment on.

## Process

The following is the RFC process for Openverse:

1. Write an RFC document using Markdown.
2. Open a PR into this repository to add the RFC in the `rfcs` folder. Name the
   file using this format:

```
YYYYMMDD-<snake case rfc title>.md
```

3. Wait for feedback. Please `@` contributors you think might have specific and
   applicable knowledge to the problem space.
4. Revise based on feedback.
5. Allow for a minimum of **5** days for review by contributors and the
   community.
6. Continue until approval from at least two core contributors has been given
   and there are no absolute blockers raised.
7. Create the related milestone and issues for the implementation plan. Link to
   the milestone in the final RFC and merge it.

## Format

There is no concrete format for RFCs but they probably (but not necessarily)
should include the following sections:

- A list of approvers (to be filled in as approvals are given)
- A deadline for feedback (typically two weeks from the date the RFC is
  originally shared unless there are extenuating circumstances)
- The rationale/reason/goals for the proposed changes. Basically the high-level
  "why we need this".
- The existing state of things as it relates to the proposed change. Link to
  previous related RFCs and other prior art.
- Describe any proposed new dependencies/technology and why we need them. When
  appropriate, include information about alternatives that were considered. This
  can be as short as "standardizing on the Vue community solution for this
  problem".
- The list of proposed changes at a high level.
- An implementation plan. This should closely if not exactly mirror the list of
  issues that would be created for the implementation of the proposed changes
  and ideally will read like a set of high-level instructions.

If helpful for the proposed change, open a draft PR in the relevant repositories
with any exploratory code that helps support the RFC.
