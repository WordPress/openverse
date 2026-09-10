# 2022-11-24 Project Proposal: Monorepo

**Author**: @dhruvkb

## Reviewers

- [x] @zackkrida
- [x] @AetherUnbound

## Rationale

For a comprehensive discussion about the pros, the cons and the counterpoints to
each see [discussion](https://github.com/WordPress/openverse/issues/192). Some
of the more nuanced points are listed below, biased towards the overall benefits
of a monorepo to justify the RFC. This RFC also proceeds to go into the
implementation details hoping that the benefits are cumulatively enough of an
improvement to convince everyone to migrate.

### Benefits of monorepo

1. Single place for everything:

   **Current criticism:** We currently have many repos, and issues and PRs
   spanning all of them. While this makes it easier for us as maintainers to
   focus our efforts, it's not easy for contributors. Let's say you were a new
   contributor looking for good-first Python issues. We shouldn't expect them to
   search in 3 repos `openverse`, `openverse-api` and `openverse-catalog`. We
   address this by making tools like Overvue or using search terms like this:

   ```
   is:open is:issue repo:WordPress/openverse-catalog repo:WordPress/openverse repo:WordPress/openverse-api repo:WordPress/openverse-frontend repo:WordPress/openverse-infrastructure sort:updated-desc
   ```

   The search term above perfectly illustrates the problem: we forgot about the
   extension. It's unwieldy and hard to quickly reach and share.

   **Monorepo solution:** We could use GitHub's own filters to narrow down what
   we're looking for.

1. Meta-issues:

   **Current criticism:** If an issue spans more than a single layer of the
   stack, we need to open a meta issue in `WordPress/openverse`, open sub-issues
   in each of the different repos, then manually close meta issues after the
   sub-issues are closed. Same goes for PRs. We make individual PRs for every
   layer and then have to cross-reference them so that reviewers can see the
   full picture. Meta issues are good when a work needs to split into subtasks,
   but they are not good for cross-repo work splitting, especially when the work
   happens completely outside the knowledge of the meta-issue.

   **Monorepo solution:** A monorepo allows our cross-layer PRs to be viewed
   more holistically and be reviewed as a complete change.

1. No more sync:

   Current criticism: We use complex sync workflows to keep files in sync. Some
   workflows need to by synced to some repos only. Some workflows shouldn't even
   be in the repo they're synced from. Some files need subtle differences so we
   compile Jinja templates for them. We also sync GitHub labels and branch
   management rules. It's a mess (I would know!).

   **Monorepo solution:** A monorepo eliminates all of this and saves the time
   and effort that goes into maintaining these systems.

1. Unified documentation:

   **Current criticism:** Having many repos, each with its own doc site means
   two things. Common docs such as contribution process needs to be repeated
   several times and repo-specific docs get siloed and can only reference each
   other with external links. Also changing docs in one repo will break any
   links pointing to it.

   **Monorepo solution:** A better system would be one cohesive doc site, for
   which the API already has a framework that other repos can just use.

1. Infra included:

   **Current criticism:** Our deployment workflows have code duplication.
   Secrets are stored in lots of repos, we keep secrets synced using Terraform.
   Containers are used in the infra repo but published in their individual
   repos.

   **Monorepo solution:** Monorepo enables the infra to coexist with the code
   (albeit in a separate module). Apart from the (encrypted) private secrets,
   the IaC could be open-sourced similar to the rest of the codebase. Our
   deployment workflows can share code and deployment secrets.

1. GitHub Milestones:

   Milestones are confined by repository boundaries. To have milestones that
   cover issues in different layers of our stack, the only way is for them to be
   in a monorepo. This is a limitation imposed by GitHub and there is no
   workaround for this.

The overarching theme is that there are workarounds for everything. We have been
working with split repos quite productively for over a year. My proposition is
the the monorepo solutions are better than workarounds.

## Migration path

First we will merge the API and the frontend repos into `WordPress/openverse`.
This decision was made for the following reasons.

1. API and frontend are tightly linked. The frontend is a direct consumer of
   what the API produces.

1. The API and frontend form the "service" side of Openverse that directly faces
   the users (both API consumers and Search engine users).

1. The frontend uses ECS deployments and the API is well on the same track. This
   makes it possible for them to share some deployment code.

1. I am very familiar with the scripts repo, the API and the frontend so merging
   them would be easier. Adding a third component would make the task daunting.

1. Merging incurs a productivity hit for the initial transition. So merging
   everything in one swoop is not ideal. While we merge these three, effort can
   be diverted to the catalog.

1. The API’s comprehensive tooling for developer documentation can benefit
   frontend devs and create a unified docs site for contributors.

1. The merge of two JavaScript codebases provides fertile ground for testing
   `pnpm` workspaces.

   - It also allows us to merge the browser extension later and split the design
     system/component library stuff into a separate package.

1. The API is already organised by stack folders so the `frontend/` directory
   will fit right in with the others like `api/` and `ingestion_server/`.
   Similarly the scripts repo is nicely organised in folders, reducing
   conflicts.

1. The API and frontend share identical tooling for Git hooks, linting and
   formatting. We will fight our tools less and encounter minimal friction.

   - The frontend's approach for `pre-commit` expanded this type of usage to the
     API as well!

   - We're expanding the use of double-quoted strings to JavaScript to further
     unify our style guides.

1. The entire system can be integration tested during releases. The real API,
   populated with test data, can replace the Talkback server as long as we
   disable network calls and make output deterministic.

The `WordPress/openverse` repo will absorb the `WordPress/openverse-api` and
`WordPress/openverse-frontend` repos. The `WordPress/openverse-catalog` will
also be merged, _later_.

### Reference

I'm following the steps listed below in a fork at
<s>[@dhruvkb/monopenverse](https://github.com/dhruvkb/monopenverse/)</s>
[@dhruvkb/monoverse](https://github.com/dhruvkb/monoverse/). You can refer to
the fork, but note that it is a comes from a place of haste and has not been
treated with the same level of love and care that the final treatment will
receive.

### Step 0: Prerequisites

#### Get the timing right

The first step will be to release the API and frontend, call a code freeze on
both of them and pause work on both. This is to prevent the repos from
continuing to drift as we merge a snapshot of them into the
`WordPress/openverse` repo.

This can prove difficult given how productive our team is, so we will need to
channel this productivity towards the catalog in the meantime. I can foresee the
end-to-end migration taking one week (ideal scenario) to becoming workable
again, and another week (for us to iron out any gaps in the docs and
references).

##### Timeline breakdown

- Day 1: Merging the repos and resolving conflicts, restoring broken workflows
  except deploys
- Day 2: Restoring deployment workflows including staging auto-deploy
- Day 3: Transfer of issues from individual repos to monorepo
- Day 4: Documentation fixes
- Day 5: Housekeeping

The second week is planned as a buffer in case any of these tasks ends up taking
more time than a day, if something breaks or if someone falls ill etc. The ideal
scenario is that we're completely back next week, the worst one takes two.

Note that in the transition period nothing will break. The old repos will
continue to exists as they are, till we ensure everything works and then we
archive the current split repos.

### Step 1: Merge with histories

This should be quick save for a few merge conflicts. In case of conflict refer
to the resolution adopted by
[@dhruvkb/monoverse](https://github.com/dhruvkb/monoverse/), and apply the
resolution to the files. Do not blindly copy code from
[@dhruvkb/monoverse](https://github.com/dhruvkb/monoverse/) as it might be out
of sync with the current state of the files.

Add remotes.

```bash
$ git remote add api ../openverse-api
$ git remote add frontend ../openverse-frontend
```

#### Merging API

```bash
$ git pull api main --allow-unrelated-histories
```

| Expected conflicts      | Resolution                                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| .github/CODEOWNERS      | Folderwise separation of owners, use from [@dhruvkb/monoverse](https://github.com/dhruvkb/monoverse/) |
| .prettierignore         | Merge entries from all repos, use from [@dhruvkb/monoverse](https://github.com/dhruvkb/monoverse/)    |
| .pre-commit-config.yaml | Python + Node.js linting, use from [@dhruvkb/monoverse](https://github.com/dhruvkb/monoverse/)        |
| justfile                | Split into many smaller `justfile`s and one root<sup>a</sup>                                          |
| .gitignore              | Split into many smaller `.gitignore`s and one root<sup>b</sup>                                        |
| CONTRIBUTING.md         | Write new, referencing doc site                                                                       |
| README.md               | Write new, referencing doc site                                                                       |

```bash
$ git add . # Stage files with conflicts resolved
$ git commit -m "Merge branch 'main' of openverse-api"
```

**a:** see the following:

- https://github.com/dhruvkb/monoverse/blob/main/justfile
- https://github.com/dhruvkb/monoverse/blob/main/automations/justfile
- https://github.com/dhruvkb/monoverse/blob/main/api/justfile
- https://github.com/dhruvkb/monoverse/blob/main/ingestion_server/justfile
- https://github.com/dhruvkb/monoverse/blob/main/load_testing/justfile

**b:** see the following

- https://github.com/dhruvkb/monoverse/blob/main/.gitignore
- https://github.com/dhruvkb/monoverse/blob/main/api/.gitignore
- https://github.com/dhruvkb/monoverse/blob/main/ingestion_server/.gitignore
- https://github.com/dhruvkb/monoverse/blob/main/ingestion_server/test/.gitignore
  (unchanged)
- https://github.com/dhruvkb/monoverse/blob/main/load_testing/.gitignore
  (unchanged)
- https://github.com/dhruvkb/monoverse/blob/main/nginx/.gitignore (unchanged)

#### Merging frontend

Change workdir to WordPress/openverse-frontend repo.

```bash
$ mkdir frontend
```

Move everything into it except the following directories and files:

| File / directory        | Reason                                 |
| ----------------------- | -------------------------------------- |
| .git/                   | For obvious reasons                    |
| .github/                | Must be in the root                    |
| .npmrc                  | For `pnpm` workspaces                  |
| .pnpmfile.cjs           | For `pnpm` workspaces                  |
| .editorconfig           | Useful across the monorepo             |
| .eslintignore           | Read by ESLint running in pre-commit   |
| .eslintrc.js            | Read by ESLint running in pre-commit   |
| .prettierignore         | Read by Prettier running in pre-commit |
| prettier.config.js      | Read by Prettier running in pre-commit |
| .pre-commit-config.yaml | Read by pre-commit                     |
| LICENSE                 | Root-level docs                        |
| README.md               | Root-level docs                        |
| CODE_OF_CONDUCT.md      | Root-level docs                        |
| CONTRIBUTING.md         | Root-level docs                        |

```bash
$ git add . # Stage all renamed files
$ git commit -m "Nest code under \`frontend/\`"
```

Switch to the monorepo.

```bash
$ git pull frontend main --allow-unrelated-histories
```

Since we fixed these files when merging the API, almost all these conflicts are
redundant.

| Expected conflicts      | Resolution                      |
| ----------------------- | ------------------------------- |
| .github/CODEOWNERS      | Use existing                    |
| .prettierignore         | Use existing                    |
| .pre-commit-config.yaml | Uncomment the commented regions |
| .gitignore              | Use existing                    |
| prettier.config.js      | Use existing                    |
| README.md               | Use existing                    |
| CONTRIBUTING.md         | Use existing                    |

#### Housekeeping

1. Create "stack: \*" labels to help with issue and PR management.
   Spoiler/foreshadowing: these labels will be used for more things later.

1. Migrate issues from `WordPress/openverse-frontend` and
   `WordPress/openverse-api`. We can directly transfer the issues, retaining all
   their comments. Apply the "stack: frontend" / "stack: backend" label to them
   after moving.

```bash
# Substitute repo with WordPress/openverse-frontend and WordPress/openverse-api
$ gh api \
    -X GET \
    repos/WordPress/<repo>/issues \
    -f pulls=false \
    -f state=all \
    --jq '.[].number' \
    --paginate \
  | xargs \
    -n 1 \
    -I num \
  gh issue transfer \
    num \
    WordPress/openverse \
    -R WordPress/<repo>
```

With this done, we can archive the API and frontend repo. The following notice
will be added to the `README.md` files for clarification before archiving.

> **Note**
>
> This repository has moved to
> [WordPress/openverse](https://github.com/wordpress/openverse) as part of a
> monorepo.

### Step 1. Restore functionality

#### Combine linting

All lint steps can be combined in `.pre-commit-config.yaml`. This also implies
the CI jobs can now be merged.

1. Remove pre-commit scripts from `frontend/package.json` and the
   `install-pre-commit.sh` script.

1. Remove `lint` job from CI, there are plenty of those.

#### `pnpm` workspace

1. Move `frontend/.pnpmfile.cjs` outside to the root directory, update the
   reference to `frontend/package.json`.

1. Remove `frontend/.npmrc` created earlier because `pnpm` will automatically
   use the one in the root of the workspace.

1. Create `pnpm-workspaces.yaml` file, see
   https://github.com/dhruvkb/monoverse/blob/main/.pre-commit-config.yaml.

1. Update the `package.json` files, see the following:

   - https://github.com/dhruvkb/monoverse/blob/main/package.json
   - https://github.com/dhruvkb/monoverse/blob/main/frontend/package.json
   - https://github.com/dhruvkb/monoverse/blob/main/automations/js/package.json

1. `pnpm i` in the monorepo root.

1. Update the recipe `pnpm` in `frontend/justfile` to include
   `--filter "openverse-frontend"`.

1. `git commit -m "Setup workspaces"`

### Step 3. Restore workflows

#### New actions

To clean up the workflows we will define three new actions. The code for all
three is available at
[@dhruvkb/monoverse](https://github.com/dhruvkb/monoverse/).

1. `setup-env` to setup Just, Node.js and Python or a subset of these.
1. `load-img` to download Docker images into `/tmp` and load them in Docker.
1. `build-docs` to build and merge Sphinx, Storybook and Tailwind Config Viewer.

#### Update workflows

Workflows with major changes:

- `ci_cd.yml` from the API will absorb `ci.yml` from the frontend
- `lint.yml` will be deleted

Updates:

- `migration_safety_warning.yml`
- `generate_pot.yml`

With this done, the development on the API and frontend can continue inside
their subdirectories. The development of both parts will be independent, at
least until we reach [long-term consolidation](#step-5-long-term-consolidation).

#### Deployment

##### Staging

The soon-to-be-ECS-based API and ECS-based frontend will continue to deploy to
staging via the CI + CD pipeline, with deployment starting as soon as all CI
checks have passed. They will use similar code as the frontend auto-deploy for
staging used currently.

These will be separate jobs with specific
[path-based filters](https://github.com/dorny/paths-filter).

##### Production

For production, we will not be able to use GitHub Releases and will have to use
a manually-triggered workflow to build the assets and tag them. The tag can be
set via a workflow input (simple) or can be calculated based on the update scope
of major, minor or patch (not as simple).

### Step 3. Housekeeping and DX cleanup

There will be a few rough edges that I cannot foresee and we can continuously
fix those as we spot them. But up to this point we should be in a position where
we can continue to build the API and the frontend independently but from one
repo.

1. The action `banyan/auto-label` will need to be configured (`auto-label.json`)
   to add the "stack: \*" labels based on the modified directory.

### Step 4. Documentation merge

The following documentation files will need reorganisation or merge.

- README.md (both repos)
- CODE_OF_CONDUCT.md (both repos)
- CONTRIBUTING.md (both repos)
- CONTRIBUTORS.md (API only; also why?)
- DOCUMENTATION_GUIDELINES.md (API only)
- TESTING_GUIDELINES.md (frontend only)
- DEPLOYMENT.md (frontend only)

I will need more information about this because IANAL.

- LICENSE (both repos)

### Step 5. Long-term consolidation

This is the long term combination of code for the frontend and the API. Ideas
like end-to-end testing go here. This is beyond my imagination at the moment,
and more importantly, beyond the scope of this RFC. It will surely be covered in
future RFCs.

Thanks for reading and providing feedback.
