# PR project: Openverse PRs

The [Openverse PRs](https://github.com/orgs/WordPress/projects/98) project board
tracks all PRs through their lifecycle, as they move from creation to merge (or
closure). This board does not track any issues, so all workflows for this board
are tied to events occurring for pull requests.

```{note}
GitHub treats PRs as a subcategory of issues, all issue related automations have
PR counterparts but not vice versa.
```

```{caution}
The PRs board is currently private. It may be made public in the future.
```

## Event automations

### PR is created

If a new PR is created, it is automatically added to the project board. PRs from
the infrastructure repository are also added to the board.

- [Built-in workflow (monorepo)](https://github.com/orgs/WordPress/projects/98/workflows/8656692)
- [Built-in workflow (infra)](https://github.com/orgs/WordPress/projects/98/workflows/8674459)

### PR is closed or merged

If a PR is closed or merged, it moves into the "Merged" column. Understandably,
this is slightly misleading for PRs that were closed unmerged.

- [Built-in workflow (closed)](https://github.com/orgs/WordPress/projects/98/workflows/8656664)
- [Built-in workflow (merged)](https://github.com/orgs/WordPress/projects/98/workflows/8656665)

### PR is reopened

If a previously closed, but unmerged, PR is reopened, it goes back to the "Needs
Review" column, even if had been reviewed before being closed.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8674442)

### PR is added to the project

The status of this PR will be set to "Needs review" and thus, it will be
included under the "Needs review" column. This is not affected by whether the PR
is actually ready or in a draft state.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8674448)

### PR is closed and inactive

If a PR is closed (includes merged) and has not been updated in two weeks, it
will automatically be archived from the project board. This is different from
the archival threshold of the issues board (8 days).

- [Built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8674454)

### PR has required approvals

If a PR has the required number of approvals, it moves into the "Approved"
column. PRs with fewer approvals than the merge requirement are not affected.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8674451)

### PR has requested changes

If a PR was reviewed with change requests, it moves into the "Changes requested"
column. Even one change request qualifies the PR for this automation.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8674445)
