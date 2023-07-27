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
- [Milestone for pre-migration changes](https://github.com/WordPress/openverse/milestone/9)
- [Milestone for Nuxt 3 migration](pending)

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
`nuxt3`, that would gradually get more and more features re-enabled. The
frontend development should be frozen on `main` until the `nuxt3` branch is
ready to be merged into `main`, to prevent the need for large rebases.

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
some components if they need extensive code changes anyway, or if the behavior
within them changes significantly and the `script setup` simplifies the
component. The decision whether to convert components to `script setup` would be
at the discretion of the PR implementer, but we should not refactor for
refactoring's sake alone, after all.

#### Testing

Vue 3 recommends to use Vitest for better performance and integration with
`vite` (which will replace `webpack` in our setup). I have not had an
opportunity to test it out, but I think it would make sense to convert our unit
tests to `Vitest`. The decision on whether to keep using the current
dependencies or convert to `Vitest` should be based on the ease of conversion.
[Type tests is also interesting and may be useful in some places.](https://vitest.dev/guide/testing-types.html)
We should add
[`eslint-plugin-vitest`](https://github.com/veritem/eslint-plugin-vitest#credits)
which basically a port of eslint-plugin-jest with necessary modifications.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

Openverse frontend uses Nuxt 3, and all current features (including i18n,
sitemaps, SEO) work.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

A lot of effort was made to describe all the necessary changes for migration.
However, it is possible that there will be some unknown steps that will be
discovered during the implementation.

First, we should try to update everything that's possible to update in the Nuxt
2 app. Due to the freeze in this project, we have completed most of these steps,
and they are left in this plan for completeness.

Then, we should have a code-freeze on non-migration-related changes to prevent
diverging of the Nuxt 3 and the Nuxt 2 branches. We should create a separate
Nuxt 3 branch.

The first PR should update the `nuxt.config` file and update the smallest list
of dependencies necessary for the app to work, removing all others. The goal
here is just to get the main functionality to work in Nuxt 3. This PR should be
merged with `--no-verify` flag, as it will probably not build correctly, and
have a lot of console errors and warnings. Then, the additional changes
described in the "Changes to Nuxt 3 branch" can be added in parallel. This is
especially true for different modules that will need updating.

### Changes to main

- Deprecation of CJS modules (the ones that use `require` and `module.exports`):

  - [ ] [Vendor in `case` utilities #2464](https://github.com/WordPress/openverse/issues/2464).
        The package we currently use for `kebab-case`, `title` case and
        `camelCase` function is CJS. We should vendor in these functions.
  - [x] home gallery uses `require` when importing the images dynamically. There
        is a small number of them, so we should just move them to `static`
        folder (or `public` in Nuxt 3) and use static `import`s.
  - [ ] #2342 Tailwind config should be converted to TypeScript.

- [x] Refactor image and audio single result pages to show the skeleton page
      when the "image"/"audio" is `null`. This is required because the way data
      is fetched changes, and _is_ the correct way it _should_ be set up
      (instead of not handling the case of `image` being `null` and instead
      relying on the error page redirect)
- [x] [Refactor skip-to-content functionality](https://github.com/WordPress/openverse/pull/2538).
      Nuxt 3 only supports teleports in ClientOnly, so the current
      implementation is causing server-client mismatch and rehydration. We
      should move to a simple HTML anchor tag and an `id` on the content.
- [ ] Refactor the functionality that is called on app load and route
      navigation.

### Changes in Nuxt 3 branch

#### 1. The first minimal Nuxt 3 update

The first PR should update the bare minimum to get the app to use Nuxt 3. This
PR would produce an app version that can be run with the `pnpm dev` or
`pnpm build && pnpm start` commands, but would have significantly less
functionality and many console errors/warnings, so it would probably be pushed
using `--no-verify` flag. It is difficult to draw the line and say what must be
in this PR, and what can be left for the follow ups. I think this PR should:

- update `Nuxt` version to the most recent one that supports the most recent
  version of `nuxt-i18n`. Also update the related dependencies such as
  `nuxt/vue-app`.
- update `nuxt-i18n`, `pinia`, and `tailwind` modules (and the way they are set
  up).
- convert `nuxt.config` to use `defineNuxtConfig` and remove the items that
  aren't used yet (disabled modules, etc).
- update the way port is set up in `nuxt.config.ts`:
  https://nuxt.com/docs/api/configuration/nuxt-config#port
- remove/comment out other modules, plugins, middleware.
- remove `nuxt-template-overrides`.
- update the Typescript config.
- move the app setup like setting the state from cookies, updating layout
  properties from the route from `middleware` and `layout` files to `app.vue`.
  `app.vue` is a new single place in Nuxt 3 where we can put the code that needs
  to run once when the app starts up.
- rename the global `middleware/middleware.ts` to
  `middleware/middleware.global.ts`. We should also move the `modal` target to
  `app.vue`.
- rename single detail pages with dynamic parameters from `_id.vue` to
  `[id].vue`.
- convert the layouts and pages to use `NuxtPage` instead of `NuxtChild` and
  `slot` instead of `Nuxt`.
- use `definePageMeta` for setting the page key on
  [`search.vue` child pages](https://github.com/WordPress/openverse/blob/361bc0d17d86cff9d8ce927cc0f7d62e6615afb5/frontend/src/pages/search.vue#L16).
- Replace all `defineComponent` in pages with
  [`defineNuxtComponent`](https://nuxt.com/docs/api/utils/define-nuxt-component#definenuxtcomponent)
  (which have support for `asyncData` and `head`).
- _Vue 3 breaking change_:
  [async components change of syntax](https://v3-migration.vuejs.org/breaking-changes/async-components.html)
  (for components that use `Comp = () => import("component.vue")`). Use the new
  way of declaring `async components`:
  - The
    [banners inside `VBanner`](https://github.com/WordPress/openverse/blob/41b0cdb37d616b5e53ee45f77f0448b07747e04f/frontend/src/components/VBanner/VBanners.vue#L34-L38),
    and
    [headers in the `search-layout`](https://github.com/WordPress/openverse/blob/41b0cdb37d616b5e53ee45f77f0448b07747e04f/frontend/src/layouts/search-layout.vue#L73-L75).
- _Vue 3 breaking change_: Arrays and objects use proxy for reactivity, and
  don't need `Vue.set` anymore. Remove `Vue.set` from the
  [feature flag store](https://github.com/search?q=repo%3AWordPress%2Fopenverse%20Vue.set&type=code).
- _Vue 3 breaking change_: Move `key` from items inside the `template` to the
  surrounding `template v-for`.

#### 2. Update tests.

Set up unit tests and add `.skip` to all the tests that are failing. Temporarily
remove the setting that disallows error logs in the test console.

#### 3. Set page layouts using `definePageMeta`

Set page `layout`s using
[`definePageMeta`](https://nuxt.com/docs/api/utils/define-page-meta)

#### 4. Programmatic navigation

Replace all `router.push` with
[`navigateTo`](https://nuxt.com/docs/migration/pages-and-layouts#programmatic-navigation)

#### 5. Add `svg-sprite` module

Add `svg-sprite` module. There is an issue with the path resolutions in the
current version of the module. I've opened a
[PR](https://github.com/nuxt-community/svg-sprite-module/pull/282) in the
repository, but got no response yet. There is also an issue with the imports not
resolving correctly in tests. We might want to vendor in and simplify this
module to get it working correctly.

#### 6. Set up SEO using `useHead` and `i18n`

Correctly set up the head using `useHead` and `i18n` using
[i18n](https://v8.i18n.nuxtjs.org/guide/seo) and
[Nuxt](https://nuxt.com/docs/getting-started/seo-meta#seo-and-meta) docs.

#### 7. Update `useRouter` and `useRoute` imports

Replace `@nuxtjs/composition-api` with `#imports` in `useRouter` and `useRoute`
imports in components. Replace all instances of `route.value` with `route`.

#### 8. Replace `useLocalePath` imports

Replace imports of `app` for `localePath` to import `useLocalePath` from
`#imports`.

#### 9. Replace `cookie-universal-nuxt` with Nuxt native `useCookies` composable

Replace usages of `cookie-universal-nuxt` with `useCookies`. I couldn't find how
to get _all_ cookies as we do in `middleware` to set up the `ui` store state.

#### 10. Finish removing `@nuxtjs/composition-api` imports

Remove the `@nuxtjs/composition-api` imports, replacing them with the
corresponding `useNuxtApp` or `i18n` import. If not yet possible, comment out
the import and the functionality that uses it.

#### 11. Remove `.native' modifier

_Vue 3 breaking change_:
[`v-on:event.native` removed](https://v3-migration.vuejs.org/breaking-changes/v-on-native-modifier-removed.html) -
after removing `.native`, check that links work as expected: send analytics
events or correctly handle audio track interactions.

#### 12. Remove `$listeners`

_Vue 3 breaking change_:
[`$listeners` has been removed / merged into `$attrs`](https://v3-migration.vuejs.org/breaking-changes/listeners-removed).
Remove all `v-on="$listeners"`, making sure that the `on` handlers are still
passed to the correct component/element.

#### 13. Add `emits` options to components that are missing it

_Vue 3 breaking change_:
[`emits` option](https://v3-migration.vuejs.org/breaking-changes/emits-option.html)
is now "recommended" in the eslint plugin, so we would need to add all of the
emitted events. There is also a new
[`defineEmits` helper](https://vuejs.org/api/sfc-script-setup.html#defineprops-defineemits)
that _could_ replace our `defineEvents` custom implementation. However, it can
only be used in the new `script setup` syntax, which we are not using yet. To
prevent scope creep for this project, we will not be converting `defineEvents`
to `defineEmits` here. We could refactor the components to use `script setup`
and `defineEmits` later, after this project is done. It could be a separate
milestone for converting all components that emit events to script setup.

#### 14. Remove v-bind="$attrs" where it was used to pass `class` and `style`

_Vue 3 breaking change_:
[`$attrs` includes `class` & `style`](https://v3-migration.vuejs.org/breaking-changes/attrs-includes-class-style.html) -
remove `v-bind="$attrs"` from the root element in components where
`inheritAttrs="false"`

#### 15. Update `v-model` to the new syntax

_Vue 3 breaking change_: - `v-model`
[changes](https://v3-migration.vuejs.org/breaking-changes/v-model.html) - make
sure
[all usages of `v-model`](https://github.com/search?q=repo%3AWordPress%2Fopenverse%20v-model&type=code)
are updated to the new syntax.

#### 16. Replace `VLink` with `NuxtLink`

New [`NuxtLink`](https://nuxt.com/docs/api/components/nuxt-link) component is
used for both external and internal links. Remove `.native` modifiers from it.
The `VButton` that has `as="VLink"` can be tricky here, so we would need to make
sure it works.

#### 17. Replace `useFetch` with `useAsyncData`

Rewrite data fetching to use the new
[`useAsyncData` composable](https://nuxt.com/docs/getting-started/data-fetching#useasyncdata).

#### 18. Update sitemap module

Replace `"@nuxtjs/sitemap"` with
`nuxt-simple-sitemap`(https://github.com/harlan-zw/nuxt-simple-sitemap)

#### 19. Update redirects

Set up all `"@nuxtjs/redirect-module"` redirects with Nitro routeRules
(https://nitro.unjs.io/config/#routerules)

#### 20. Update Plausible module

Add [`plausible` module](https://github.com/nuxt-modules/plausible)

#### 21. Update proxying

Replace `"@nuxtjs/proxy"` with
[Nitro routeRules](https://stackoverflow.com/questions/76120894/how-do-i-set-proxy-with-baseurl-with-nuxt3-and-nitro-config)
or use [`proxyRequest`](https://github.com/nuxt/nuxt/discussions/15907)

#### 22. Update Sentry module

Replace `sentry` module

#### 23. Update ESLint settings to use Vue 3 recommended rules

Update `eslint` plugins. Lint code with the new settings.

#### 24. Re-enable Playwright tests

Re-enable the Playwright tests and make sure they pass.

#### 25. Re-enable unit tests

Re-enable all skipped unit tests and make sure they pass and are linted with
eslint.

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

Dockerfile will need to be updated:

The `static` will need to be changed to `/` here:

`RUN echo "{\"release\":\"${SEMANTIC_VERSION}\"}" > /home/node/frontend/src/static/version.json`

PORT should be set correctly for the production build (I'm not yet sure what
exactly "correctly" means here)

We should test that the Docker build works as expected.

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

Nuxt uses `module`s for adding functionality. The table below describes the
changes that need to be made to the modules we use.

#### Nuxt module changes

| Module name                        | Change needed                                                                                           | Links                                                                                                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `"@nuxt/typescript-build"`         | Delete as TypeScript is natively supported by Nuxt 3                                                    |                                                                                                                                                          |
| `"@nuxtjs/composition-api/module"` | Delete - natively supported by Nuxt 3                                                                   |                                                                                                                                                          |
| `"portal-vue/nuxt"`                | Delete - natively supported by Vue 3 / Nuxt 3                                                           |                                                                                                                                                          |
| `"cookie-universal-nuxt"`          | Delete - natively supported by Nuxt 3, [useCookie](https://nuxt.com/docs/api/composables/use-cookie)    |                                                                                                                                                          |
| `"@nuxtjs/svg-sprite"`             | Update to current that supports Nuxt 3                                                                  |                                                                                                                                                          |
| `"@nuxtjs/eslint-module"`          | Update to current that supports Nuxt 3                                                                  | https://github.com/nuxt-modules/eslint                                                                                                                   |
| `"@pinia/nuxt"`                    | Update to current version that supports Nuxt 3                                                          |                                                                                                                                                          |
| `"@nuxtjs/proxy"`                  | Replace with Nitro routeRules or use `proxyRequest`                                                     | https://stackoverflow.com/questions/76120894/how-do-i-set-proxy-with-baseurl-with-nuxt3-and-nitro-config, https://github.com/nuxt/nuxt/discussions/15907 |
| `"@nuxtjs/redirect-module"`        | Define Nitro routeRules in `nuxt.config`                                                                | https://nitro.unjs.io/config/#routerules                                                                                                                 |
| `"@nuxtjs/sentry"`                 | No official support                                                                                     | Workaround in https://github.com/nuxt-community/sentry-module/issues/530                                                                                 |
| `"vue-plausible"`                  | ~~Update to current version that supports Nuxt 3 or~~ Move to https://github.com/nuxt-modules/plausible | Note: enabling outbound tracking breaks links with target blank in `vue-plausible`                                                                       |
| `"@nuxtjs/sitemap"`                | Replace with `nuxt-simple-sitemap`                                                                      | https://github.com/harlan-zw/nuxt-simple-sitemap                                                                                                         |

We should probably add [`nuxt-vitest`](https://github.com/danielroe/nuxt-vitest)
for testing in Nuxt. The package is under active development, so we should pin
to the patch version.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

Migrate to a non-Nuxt SSR solution for Vue. This would require significant
changes to code for an unclear benefit.

## Design

<!-- Note any design requirements for this plan. -->

The designs should stay exactly the same. Hopefully, all of the Playwright
visual regression tests pass after this migration.

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
