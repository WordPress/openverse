# 2023-06-01 Implementation Plan: Nuxt 3 Migration

**Author**: @obulat

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @sarayourfriend
- [ ] @zackkrida

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/411)
- [Project Proposal](https://docs.openverse.org/projects/proposals/nuxt_3_migration/20230604-project_proposal_nuxt_3_migration.html)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

Nuxt team has created Nuxt bridge to facilitate the migration from Nuxt 2.
However, there seems to be
[no support for Nuxt Bridge in Nuxt i18n](https://github.com/nuxt-modules/i18n/discussions/1334#discussioncomment-1967220),
so the best way forward is to migrate directly to Nuxt 3.

Nuxt 3 migration will require a lot of changes split into several PRs.

One set of changes is required for Nuxt 3, but can also work in the current Nuxt
2 app. An example of such change is the conversion of `onBeforeRouteEnter` to
`middleware`: both work well in Nuxt 2, but only `middleware` can access `store`
in Nuxt 3. These changes are described in the "Changes to main" section below,
should be merged directly into `main` branch.

The other changes like actually updating the `nuxt` version would break the
current app. To make sure that we can split these changes into several distinct
steps without breaking the production app, we should use a separate branch,
`nuxt3`, that would gradually get more and more features re-enabled.

### Nuxt 3 / Vue 3 features in Openverse: discussion

#### Autoimports

Nuxt 3 auto imports composables and components. Unlike the usual global imports,
these imports are handled in such a way that only the imports that are actually
used are left in the production files. The Nuxt team have optimized the way they
work both in the working app and in the IDEs, so I think we _should_ use the
auto import feature and not go against the framework and disable it. In the
current setup, our test suite throws warnings when a child component is not
imported. We would need to make sure that this does not happen with Nuxt 3.

#### `script setup`

The new way of writing components in Vue 3 is using `script setup` which reduces
the number of code lines by automatically exporting the variables for use in the
components. While we can eventually move to using `script setup` throughout the
app, this conversion is out of scope for this project. We can, however, convert
some components if they need extensive code changes anyways, or if the behavior
within them changes significantly and the `script setup` simplifies the
component. The decision wether to convert components to `script setup` would be
at the discretion of the PR implementer.

#### Testing

Vue 3 recommends to use Vitest for better performance and integration with
`vite` (which will replace `webpack` in our setup). I have not had an
opportunity to test it out, but I think it would make sense to convert our unit
tests to `Vitest`. The decision on whether to keep using the current
dependencies or convert to `Vitest` should be based on the ease of conversion.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

Openverse frontend uses Nuxt 3, and all current features (including i18n,
sitemaps, SEO) work.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

This section describes the known steps that need to be taken to migrate to
Nuxt 3. However, it is possible that there will be some unknown steps that will
be discovered during the implementation.

- [ ] Add changes that can be done in Nuxt 2 (see "Changes to main")
- [ ] Create a `nuxt3` branch with the first PR as described in the "Nuxt 3
      branch"
- [ ] Add all other Nuxt 3 changes, as described in the "Nuxt 3 branch"
- [ ] Re-enable Playwright tests
- [ ] Make all unit tests pass

### Changes to main

- Deprecation of CJS modules (the ones that use `require` and `module.exports`):
  - `case` package that we use for `kebab-case`, `title` case and `camelCase`
    function is CJS. We can either find replacements that use `ESM` modules,
    vendor in these functions, or use a workaround that `vite` suggests (instead
    of `const { kebab } = require "case"` use
    `import casePkg; const { kebab } = casePkg;`)
  - home gallery uses `require` when importing the images dynamically. There is
    a small number of them, so we should just move them to `static` folder (or
    `public` in Nuxt 3) and use static `import`s.
  - [ ] #2342 Tailwind config should be converted to TypeScript.
- Moving functionality inside the `setup` function would make it easier to
  handle with Vue 3/Nuxt 3:
  - Refactor `search.vue` page: move the route watcher and `fetchMedia`
    functions to `setup`
- Refactor image and audio single result pages to show the skeleton page when
  the "image"/"audio" is `null`. This is required because the way data is
  fetched changes, and _is_ the correct way it _should_ be set up (instead of
  not handling the case of `image` being `null` and instead relying on the error
  page redirect)
- [x] #2234 Replace `onBeforeRouteEnter` router guards that don't have access to
      `pinia` stores with router `middleware` that does
- [x] #2233 Remove `@nuxtjs/style-resources` - this module was used to
      auto-import `scss` variables into all components. We don't use `scss`
      anymore

### Changes in Nuxt 3 branch

- The first PR should update the bare minimum to get the app working with Nuxt
  3:
  - update `nuxt` itself and `i18n`, `tailwind` and `svg-sprite` modules (and
    the way they are set up). Remove/comment out other modules, plugins,
    middleware.
  - update the Typescript config and node version.
  - Move the functions that are called at the app set up from
    `middleware`/`layout`s to `app.vue`.
  - Convert the layouts and pages to use `NuxtPage` instead of `NuxtChild` and
    `slot` instead of `Nuxt`. For other necessary changes, look up the Nuxt 3
    docs.
  - Use the new way of declaring `async components`
  - Remove `Vue.set`
  - Move `key` from items inside a `v-for` to the surrounding `template`. This
    PR would produce an app version that can be run with the `pnpm dev` or
    `pnpm build && pnpm start` commands, but would have significantly less
    functionality and many console errors/warnings, so it would probably be
    pushed using `--no-verify` git flag.
- Set up unit tests and add `.skip` to all the tests that are failing.
  Temporarily remove the setting that disallows error logs in the test console.
- Correctly set up the head using `useHead` and `i18n`
- Remove the `@nuxtjs/composition-api` imports, replacing them with the
  corresponding `useNuxtApp` or `i18n` import. If not yet possible, comment out
  the import and the functionality that uses it.
- Remove all `v-on="$listeners"`, making sure that the `on` handlers are still
  passed to the correct component/element.
- Remove the `.native` modifiers, and convert `VLink` to use `NuxtLink`. The
  `VButton` that has `as="VLink"` can be tricky here, so we would need to make
  sure it works.
- Rewrite data fetching to use the new `useAsyncFetch` composable.
- Re-add the modules listed in the "Modules" section.

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

There should be no changes to infrastructure.

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

Nuxt uses `module`s for adding functionality. The table below describes the
changes that need to be made to the modules we use.

### Nuxt module changes

| Module name                        | Change needed                                                                                        | Links                                                                                                                                                    |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `"@nuxt/typescript-build"`         | Delete as TypeScript is natively supported by Nuxt 3                                                 |                                                                                                                                                          |
| `"@nuxtjs/composition-api/module"` | Delete - natively supported by Nuxt 3                                                                |                                                                                                                                                          |
| `"portal-vue/nuxt"`                | Delete - natively supported by Vue 3 / Nuxt 3                                                        |                                                                                                                                                          |
| `"cookie-universal-nuxt"`          | Delete - natively supported by Nuxt 3, [useCookie](https://nuxt.com/docs/api/composables/use-cookie) |                                                                                                                                                          |
| `"@nuxtjs/svg-sprite"`             | Update to current that supports Nuxt 3                                                               |                                                                                                                                                          |
| `"@nuxtjs/eslint-module"`          | Update to current that supports Nuxt 3                                                               | https://github.com/nuxt-modules/eslint                                                                                                                   |
| `"@pinia/nuxt"`                    | Update to current version that supports Nuxt 3                                                       |                                                                                                                                                          |
| `"@nuxtjs/proxy"`                  | Replace with Nitro routeRules or use `proxyRequest`                                                  | https://stackoverflow.com/questions/76120894/how-do-i-set-proxy-with-baseurl-with-nuxt3-and-nitro-config, https://github.com/nuxt/nuxt/discussions/15907 |
| `"@nuxtjs/redirect-module"`        | Define Nitro routeRules in `nuxt.config`                                                             | https://nitro.unjs.io/config/#routerules                                                                                                                 |
| `"@nuxtjs/sentry"`                 | No official support                                                                                  | Workaround in https://github.com/nuxt-community/sentry-module/issues/530                                                                                 |
| `"vue-plausible"`                  | Update to current version that supports Nuxt 3 or https://github.com/nuxt-modules/plausible          | Note: enabling outbound tracking breaks links with target blank in `vue-plausible`                                                                       |
| `"@nuxtjs/sitemap"`                | Replace with `nuxt-simple-sitemap`                                                                   | https://github.com/harlan-zw/nuxt-simple-sitemap                                                                                                         |

We should probably add [`nuxt-vitest`](https://github.com/danielroe/nuxt-vitest)
for testing in Nuxt. The package is under active development, so we should pin
to the patch version

The migration to Nuxt 3 also means migration from Vue 2 (with added composition
API) to Vue 3. Below is a list of breaking changes that need to be addressed in
Openverse.

#### Vue 3 breaking changes

- [ ] `v-model`
      [changes](https://v3-migration.vuejs.org/breaking-changes/v-model.html)
- [ ] `key` usage on `template v-for` instead of the components inside that
      `template`
- [ ] [`v-on:event.native` removed](https://v3-migration.vuejs.org/breaking-changes/v-on-native-modifier-removed.html) -
      after removing `.native`, check that links work as expected, sending the
      analytics events
- [ ] [`$listeners` has been removed / merged into `$attrs`](https://v3-migration.vuejs.org/breaking-changes/listeners-removed)-
      remove the `$listeners` everywhere and make sure that we have
      `v-bind="$attrs"` everywhere we had `$listeners` before
- [ ] [`$attrs` includes `class` & `style`](https://v3-migration.vuejs.org/breaking-changes/attrs-includes-class-style.html) -
      remove `v-bind="$attrs"` from the root element in components where
      `inheritAttrs="false"`
- [ ] `Vue.set` is not necessary anymore to keep array/object reactivity
- [ ] [async components change of syntax](https://v3-migration.vuejs.org/breaking-changes/async-components.html)
      (for components that use `Comp = () => import("component.vue")`)
- [ ] [`emits` option](https://v3-migration.vuejs.org/breaking-changes/emits-option.html) -
      replace the `defineEvents` custom implementation

#### Nuxt 3 breaking changes

- [ ] `NuxtLink` is now a wrapper around both external and internal links, so we
      can replace our custom `VLink` component with it.
- [ ] `app.vue` is a single place where we can put the code that needs to run
      once when the app starts up. Currently, we have some layout code that is
      duplicated, and `middleware` code that is run before the first load. We
      should move it to `app.vue`
- [ ] [Pages and layouts changes](https://nuxt.com/docs/migration/pages-and-layouts)

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

Migrate to a non-Nuxt SSR solution for Vue. This would require significant
changes to code for an unclear benefit.

## Design

<!-- Note any design requirements for this plan. -->

The designs should stay exactly the same.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

The Nuxt 2 changes can be worked on immediately. The changes to Nuxt 3 branch
can be parallellized after the initial PR.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Since Nuxt 3 specific features will be in a separate branch, if there is a need
to roll back after merging `nuxt3` branch, we can revert the merge commit.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

Nuxt 3 is ready for production, but several modules that we need are still in
beta. We might need to patch them ourselves if we find bugs.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
