# Feature flags

Feature flags control how the app works in different environments and for
different users.

## Concepts

### Status

The status of a feature can be one of three values:

- `enabled`
- `disabled`
- `switchable`

This is configurable and must be set in the feature flags configuration file,
`~/feat/feature-flags.json`.

A `switchable` flag in a public environment like 'staging' or 'production'
effectively becomes a user-level preferences toggle.

### State

The state of a feature can be one of two values:

- `on`
- `off`

This is determined by the [feature status](#status) and user-preferences.

- An `enabled` feature is always `on`.
- A `disabled` feature is always `off`.
- A switchable feature can be `on` or `off` based on the user's preference. This
  `preferredState` is recorded in a cookie. If no preference has been set, the
  [`defaultState`](#defaultstate) will be used.

### Cascade

The current environment can be 'local', 'development', 'staging' or 'production'
based on the `DEPLOYMENT_ENV` environment variable (assumed 'local' by default).

If a feature status is set for an environment, it is assumed to be same value
for all environments before it and `disabled` for all environments after it
(unless specified otherwise). For example, consider the following configuration:

```json
{
  "local": "enabled",
  "staging": "switchable"
}
```

Here the feature will be

- `enabled` for 'local' environment (configured)
- `switchable` for 'development' environment (cascaded from staging)
- `switchable` for 'staging' environment (configured)
- `disabled` for 'production' environment (default)

## File structure

The feature flags configuration file, `~/feat/feature-flags.json` contains two
top-level keys, `features` and `groups`.

### `features`

This is a mapping of feature names to feature configurations.

#### Key: title

This is an identifier for the feature. This identifier is looked up in the i18n
strings to generate a human-readable purpose (`pref-page.features.${title}`) for
the feature.

Conventionally, `_` is used as the separator for the name so that the name is a
valid JS identifier.

#### Value: configuration

This controls the behavior of the feature flag. It is an object containing three
fields, `status`, `description` and `defaultState`.

##### `status`

It is a mapping of different environments with the status of the flag in that
environment. For example, a feature that's in development may be 'switchable' in
'staging' but 'disabled' in 'production'.

##### `defaultState`

This is the state of a switchable feature when the user has not switched it. For
example, a feature that's in development may start as 'opt-in', being 'off' by
default and may gradually change to opt-out, becoming 'on' by default.

##### `description`

This is a description of the feature that appears in the internal `/preferences`
page.

⚠️ This field is not internationalised because it's for internal use only. You
should [populate `en.json5`](#key-title) if the feature is switchable and
visible to the user.

##### `storage`

This determines whether the feature is stored in a cookie (`'cookie'`) or in
`sessionStorage` (`'session'`). By default all feature flags are stored in
cookies but certain preferences that should only be applicable for a single
session can be stored in `sessionStorage` instead.

##### `supportsQuery`

By default, all switchable flags can be set per-request using the `ff_<flag>`
query parameters. This is useful for testing and debugging. However, some flags
dealing with sensitivity can be used to make malicious URLs, so they can avoid
being set via query parameters by setting this to `false`.

### `groups`

This setting pertains to how feature flags can serve as user-level preferences.
It is an array of objects, each containing two fields, `title` and `features`.

#### `title`

This is an identifier for the group. This identifier is looked up in the i18n
strings to generate a human-readable name (`pref-page.groups.${title}.title`)
and description (`pref-page.groups.${title}.desc`) for the group.

#### `features`

This is a list of strings where each string must be a
[key from the upper `features` section](#key-title). Each switchable feature
from this list will show up in the preferences modal.
