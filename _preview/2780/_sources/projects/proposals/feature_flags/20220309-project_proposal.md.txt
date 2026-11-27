# 2022-03-09 Project Proposal: Feature flags

**Author**: @dhruvkb

## Reviewers

- [x] @sarayourfriend
- [x] @zackkrida

## Rationale

So far we have built features on a branch other than `main` and kept those
branches separate until the features were ready to be visible. This has worked
out so far but it is

- **untenable**

  Branches tend to drift when commits are pushed to `main` (like constant
  bug-fixes) and conflicts tend to emerge when the commits touch the same files.

- **wasteful**

  Considerable effort goes into keeping the branches in sync that is not
  affordable in a small team. Also if the feature is squash-merged into `main`,
  a lot of history is lost inside one commit.

- **un-_fun_**

  Everyone wants to build exciting features, not exercise Git-fu when there are
  conflicts or when it's time to finally merge the feature in.

## Goals

Feature flags, as an alternative to the current methodology, should allow us to
do the following:

### Must haves

These features are strict requirements and solutions not providing them will be
disqualified.

1. Develop right on `main`, keeping visibility hidden until we can go live.
   1. Allow code for both live and in-dev features to coexist.
   1. Deployments to prod such as fixes should not be blocked.
1. Keep the code separate from the feature visibility configuration[^separate].
1. Toggle the state (enabled, disabled, switchable) of features based on the
   environment.

[^separate]:
    Separate not in the sense of being placed somewhere else, just being
    untangled or decoupled.

### Good to haves

These features are not strictly needed and a solution lacking them will not be
discarded.

1. Enable features to go-live without technically needing a new release.
1. Associate certain metadata or sub-attributes linked to features such as
   conditions for toggling etc.
1. Nested feature flags, with the parent flag acting as shortcut to toggle all
   its children.

## Implementation

This RFC considers feature flags for the frontend. The API can just use `beta/`
instead of `v1/` to sufficiently mark unstable endpoints.

### States

Each flag can have 3 statuses.

- **enabled**

  There is no fencing, everyone can access the feature, even if they don't like
  or want it.

- **disabled**

  The feature is not visible and accessible, and trying to access it should
  yield an error message.

- **switchable**

  The feature can be turned on or off by the user. Preferences may be recorded
  in a cookie.

Based on the one of the three statuses of the flag above, and the preference of
the user (if status is switchable), the feature can have two states.

- **on**

  When either

  - status is "enabled"
  - status is "switchable" and preference is "on"

- **off**

  When either

  - status is "disabled"
  - status is "switchable" and preference is "off"

### Sources

The feature flag state is determined in two steps.

#### Conf files

Conf files are JSON files that define the feature flags. Here is a sample of
what the schema of this file looks like:

```js
{
  features: {
    feature_name_1: {
      // feature flag name
      status: "enabled", // enabled | disabled | switchable
      description: "Feature 1 does ...", // what the feature does
      data: {
        // optional, any data you want to store related to this feature
        release_date: "2023-01-01",
      },
    },
    feature_name_2: {
      status: "switchable",
      default: "on", // whether the feature is opt-in or opt-out
      description: "Feature 2 does ...",
    },
  },
}
```

Conf files being JSON can be read in any part of the codebase, without any
additional libraries. Note that conf files only define the status of the flag
and not the final state of the feature.

#### Cookies

For flags that are set to switchable in the conf files, we use the state in the
cookie to determine whether the flag is set to on or off. This cookie has the
following schema.

```js
{
  features: {
    feature_name_1: "on",
    feature_name_2: "off",
  },
}
```

The cookie is only referred to for flags that are set to switchable, any other
feature definitions in the cookie should be dropped or ignored. If the cookie
does not mention the flag, the `default` value from the config is read.

Regardless of the storage mechanism we will need a few other key things.

### Store

To prevent feature flags from being all over the place, we can keep them store
in a Pinia store and just use the store wherever there is a check. This allows
us to toggle features from a centralised place.

Since keys will be added and removed periodically, the store must not expose
feature flags directly but rather expose a getter that can handle
fallback-to-default.

The flags can be populated in the store from whatever source we choose.

### Utilities

A composable can be provided that interacts with the Pinia store to provide
`isFeatureEnabled` functionality. The composable can directly be pulled into a
component and used as a boolean `ref`.

### Directive

To prevent a lot of `v-if="isFeatureEnabled(feature)"` statements in the
templates, we can create a new directive.

```
v-flag:{feature_name: str}="{flag_state: str}"
```

This directive takes the `feature_name: str` argument and the
`flag_state: boolean` value. The component is only rendered when the state of
the feature flag matches the given value.

The component is shown if the flag is

- enabled
- switchable (with the user having chosen to enable it)

It internally intefaces with the utility to evaluate whether the component is
rendered or not. Here is
[some code](https://github.com/mblarsen/vue-browser-acl/blob/4e3bb90d2ba4fcc3edd30b27737f4531dc464329/index.js#L136-L163)
that can be used to avoid rendering.

### Drawbacks

This implementation has the main drawback of leaving `v-flag` directives around
the codebase that are equivalent `v-if="true"` when the feature has been
permanently enabled. Similarly a script utility `isFeatureEnabled` that always
evaluates to `true` is another a no-op.

We can periodically clean them up or create tickets to remove them after a
feature is completely and irreversibly live. This is important to prevent cruft
from accumulating in in the codebase.

## Proof-of-concept

[Link to `WordPress/openverse-frontend` PR](https://github.com/WordPress/openverse-frontend/pull/1270)

## Disqualified alternatives

One alternative to feature flags is what we have been doing in that past which
is working on a branch that gets merged into `main` later. This is bad for
reasons listed above in [§Rationale](#rationale).

Another terrible alternative it to just work on `main` and never deploy till the
feature is ready. This might work if the site didn't have any bugs or pressing
issues (that need to be solved and deployed fast) or if features were getting
ready super-fast (allowing us to deploy them with the fixes). Neither is true
for us.

### Binned sources

Just skip this section and proceed to [§Sources](#sources).

#### 1. Environment variables

<details>
  <summary>
    Feature flag env vars can be prefixed with a string like <code>FF_</code> to separate them from the other env vars.
  </summary>
  <div>

##### Pros

1. Effortless to set up.
1. Universal way to configure applications.
1. Low maintenance as every feature can be one env var.
1. Fairly easy to test considering env vars can be set per-session, per-command,
   per-container and per-machine (as needed).
1. Managing a couple of `.env` files is not hard.
1. Server-side envs can help tree-shake the off features in prod.

##### Cons

1. Will need a deployment to change the environment variables.
1. Can get complicated if we need to build a lot of scaffolding around it.
1. Managing a lot of `.env` files is not easy.
1. Flags will be primitive and will not allow complex data.
1. Nested flags and flags with metadata will need hacks.

##### Considerations

Feature flag env vars can be prefixed with a string like `FF_` to separate them
from the other env vars.

The limitation for the data to be a string means any extra metadata must be
JSON-stringified and then parsed in the code. Only primitive flag states can be
handled conveniently.

Nesting flags will use hacks like artificial separators e.g. `FF_PARENT__CHILD`.
Looks ugly and confusing.

  </div>
</details>

#### 2. Growthbook

<details>
  <summary>
    GrowthBook is an open-source platform for feature flagging. It provides SDKs and a UI to manage feature flags.
  </summary>
  <div>

##### Pros

1. High-level solution with UI.
1. Supports features we'd want later like A/B testing.
1. Can record a large number of metrics.
1. Actively maintained and FOSS.
1. No redeployment necessary, flags can be toggled remotely.
1. Allows flags to have many sub-attributes.

##### Cons

1. Adds API calls to the server startup.
1. Separate service that needs to be self-hosted and set up.
1. Will need Dockerisation of the dev workflow.
1. Might be overkill if we don't want the extra features.
1. We might not even want to use the metrics.

##### Reference

- [Home](https://www.growthbook.io)
- [Docs](https://docs.growthbook.io)

  </div>
</details>

#### 3. API

<details>
  <summary>
    Our API could serve as a decent source of feature flag statuses by storing them as Django model.
  </summary>
  <div>

##### Pros

1. Can be managed using Django admin.
1. No redeployment necessary, flags can be toggled remotely.
1. Allows flags to have many sub-attributes, essentially models.
1. The frontend depends on the API anyway, so just add more of it.

##### Cons

1. Need to mock the API calls in dev environments.
1. Adds coupling between frontend features and the API.

  </div>
</details>

#### 4. Query params

<details>
  <summary>
    We can clearly demarcate feature flag params with a prefix such as <code>ff_</code>
  </summary>
  <div>

##### Pros

1. Even more effortless to set up.
1. We've done this before for the embedded mode,
   [_remember_](https://github.com/WordPress/openverse-frontend/pull/65)?
1. Testing is easy because tests can append the right flag param to the URL.

##### Cons

1. Configuration will need to live in the codebase so change of state will need
   deployment.
1. Exposes half-baked features to users who know the flag.
1. Transient, so switchable flags must be set on every URL or stored in cookies.
1. Flags will be primitive and will not allow complex data. Even stringified
   JSON would be bad in URLs.

##### Considerations

We can clearly demarcate feature flag params with a prefix such as `ff_` (or
`feature/` 🚳) to separate them from the actual query params and process them
separately.

Due to their nature being run-time rather than build-time, they are best used in
pairing with another storage (as an override for the default) rather than on
their own.

For example, we can have a feature flag which is set to switchable via a config
file. This prevents users from accessing this feature. However, a developer who
still wants to use this feature can send the query param as true and access it.

  </div>
</details>
