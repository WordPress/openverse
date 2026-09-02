# Project Proposal - 2022-02-23

- [x] @dhruvkb

- [x] @sarayourfriend

**Milestone:** https://github.com/WordPress/openverse-frontend/milestone/5

## Rationale

Currently we use Vuex for global state management. This works fine for Vue 2 but
has some considerable disadvantages for Vue 3, especially when it comes to
TypeScript support and composition-api usage. We should switch to Pinia instead.
It is the new
[official default recommendation](https://blog.vuejs.org/posts/vue-3-as-the-new-default.html)
of the Vue project for state management instead of Vuex. Evan You, the creator
of Vue,
[has confirmed](https://twitter.com/youyuxi/status/1463429442076745730?lang=en)
that Vuex 5 and Pinia are defacto the same.

Pinia also has better interoperability between Vue 2's composition-api and Vue
3, and would allow us to decouple our state-management API usage from Nuxt.
Currently we rely on Nuxt's home-grown `useStore` composable from the
`@nuxtjs/composition-api` extension on top of `@vue/composition-api` but there's
no guarantee that that composable will stick around in Nuxt 3. Besides, it is
not easy to watch for changes in the store from within the `setup` function, at
least when rendering on the server, and it caused problems with rendering the
correct search input text on SSR.

Moving to Pinia will allow us to reduce the current verbosity of the store
introduced by module, action and mutation constants. In the long run, it will
simplify the unit tests setup.

## Alternatives

We could just stick with the current Vuex approach and during the Nuxt bridge
upgrade replace all usages of `useStore` with `useNuxtApp().$store` instead.
This would introduce more code changes during the Nuxt bridge upgrade BUT would
prevent us from having to re-write our entire state management strategy before
migrating to Nuxt 3.

## Potential risks

- Pinia is currently maintained by a Vue core member, but it's still not the
  official Vue Vuex implementation. However, its development is closely linked
  with the development of the new version of Vuex and they strive for the same
  API and some feature parity, so we should be able to move to Vuex 5 whenever
  it is released if we decide to do so.
- Store changes affect the app as a whole, and changes can cause a lot of
  disruption. To mitigate this, we can ensure that each store rewrite is
  accompanied with a full rewritten unit test, and try to use types as much as
  possible.

## Conversion to Pinia

There are some important differences between Vuex (the version we are currently
using)and Pinia in store structure.

### Dividing the store: Vuex modules and Pinia stores

Vuex uses a single store which can have multiple modules that can be namespaced.
In our setup we have several namespaced modules inside `src/store` that Nuxt
uses to create a single store. In Pinia, the equivalent of a Vuex namespaced
module is a single store. Namespacing is achieved by giving a store its `id`.
All Pinia stores are separate modules, and are usually kept in a `src/stores`
folder to emphasize that. To use a store `X` from store `Y`, you need to call
`useXStore` inside `storeY`. I couldn't find a way to create a central store
equivalent to what we have now. So, when using the store in components, we would
have to import all the stores that the component uses, instead of using a single
`useStore()` call. This means that there will be more than single-line changes
in the components.

### Pinia store definitions

Pinia currently supports two types of store definitions: **options store** and
**setup store**. As a team, we lean towards using the _setup store_, not the
_options store_.

**Options store** is similar to the Vuex store: it has `state`, `getters` and
`actions`. It could be easier to convert the current Vuex modules into the Pinia
options stores as the structure is almost the same, with the main difference
being the fact that the mutations are converted into actions, and lack of
`context` parameter for actions, and `state` parameter for mutation.

**Setup store** is a newer kind of store that is more compatible with the
composition API. The store definition itself is very similar to `setup` function
we use in the components. For more context on the `setup store`, watch a talk by
Eduardo San Martin Morote (the creator of Pinia) where he explains the setup
syntax on minute 22:
[Everything Beyond State Management in Stores with Pinia by Eduardo San Martin Morote - GitNation](https://portal.gitnation.org/contents/everything-beyond-state-management-in-stores-with-pinia).
In short, the **advantages** of using the setup store are:

1. It is very similar to the components `setup` function, so it will be easier
   cognitively to switch between the store code and the component code.

2. We can use other composables within the store.

3. It is easier to use other stores from inside a store: you would only need to
   call `useXStore` once to use it in different `actions`. For example, when
   fetching media for search and fetching a single media item details, we use
   `UsageData` store to send the usage statistics. With the options store, we
   would have to use `const usageDataStore = useUsageDataStore()` for each
   action, and with the setup store we can set it up once and use in any action
   that needs it.

These advantages strongly outweigh some potential **downsides** to using the
setup store:

1. Setup stores are not well documented. Most of the documentation examples use
   the options store.

2. Setup store does not force us to separate the store code into state, getters
   and actions, so we would have to make effort to somehow make sure that the
   stores are well-organized, and not just a pile of spaghetti code.

View a sample simple store in the
[Pinia repository](https://github.com/vuejs/pinia/blob/f9ba40a7e86e39f5336b587d248f234ccdbad5ca/packages/pinia/test-dts/storeSetup.test-d.ts).

## Prior work

[Original issue](https://github.com/WordPress/openverse-frontend/issues/756)
with a discussion of Pinia conversion and initial plan.
[@dhruvkb's PoC PR with Pinia setup and conversion of active-media store to a Pinia options store, which was later rewritten as a setup store](https://github.com/WordPress/openverse-frontend/pull/906)

## Implementation plan

We have considered two options, converting stores one by one, or converting all
stores in a feature branch, and decided that the first option is preferable.

1. Convert the store from Vuex to Pinia gradually, one store at a time. @dhruvkb
   has created an excellent PoC PR for a gradual conversion to Pinia while
   keeping other stores in Vuex.

To minimise disruption, each store can be changed using a lock-based approach
where the developer takes a lock on the store using a notification to the group,
makes a PR updating a single store and its usages and this lock is released
after the PR is merged.

This prevents PRs from diverging too much and allows a seamless transition for
all involved.

2. Create a feature base branch, do all the conversion in it, and only merge a
   fully-converted store into main. This will ensure that we are merging a
   fully-working converted store, and if we find any blocking concern, we can
   easily revert the changes by closing the feature branch.

While Pinia docs suggest that it is possible to migrate large projects from Vuex
to Pinia module by module, they also say that using `disableVuex: false` is not
recommended. ~Also, I'm not sure how to use Pinia stores from Vuex modules, and
we do have several interdependent modules that call one another.~ In this case,
we can use Pinia stores inside the Vuex stores by calling `useXStore()` inside
getters, mutations and actions.

## Converting a Vuex namespaced store module to a Pinia store

There is an excellent guide on conversion in Pinia docs. This section will give
steps that need to be followed for each store, and add some details specific to
Openverse setup.

For each store, there are several things that need to be done:

- convert the store creation to use `defineStore`.
- convert state to `reactive`
- convert `getters` without params to `computed` and `getters` with parameters
  to functions.
- convert `actions` and `mutations` to functions. They will no longer use the
  `context` or `state` parameter, and will, instead of using an all-capital
  constant for a name, be renamed to use camelCase (e.g. `[FETCH_MEDIA]` will
  become `fetchMedia`).
- return the necessary state properties, getters and actions.
- adjust the types where necessary.
- remove the unused constants from - `~/constants/mutation-types.js`,
  `~/constants/action-types.js`, `~/constants/store-modules.js`.
- refactor the use of the store in components.
- add or refactor the store unit test.
- refactor the unit tests for components that use this store.
- add e2e tests for the changes in components.

### State

When using the setup store, we should try to use a `reactive` to create the
initial state object, and not a set of `ref`s. Otherwise, we can create errors
by accidentally having a state property name and an action parameter that is
updating it with the same name. This doesn't work:

```js
const message = ref("string message")
function setMessage({ message }) {
  message.value = message
}
```

Here, the destructured parameter name `message` shadows the state property name
`message`, and the `setMessage` doesn't update the state as could be expected.

We can use `const { param1, param2 } = toRefs(state)` to enable store
destructuring, and make each property reactive. If we do not return all of the
state properties, such as when some properties only used from inside the store
itself (e.g. `status` for `activeMediaStore`), we can also add a `readonly`
state `state: readonly(state)` property to the return to make it testable.

### Actions

Pinia allows changing the state directly in the components (which was frowned
upon by Vuex) so we could do away with mutations in theory. But it is better to
keep using separate functions (actions) to update the state to keep state
changes limited to one file and make it easier to debug.

When using the `setup store`, we don't need the strict divide between mutations
that can change the state, and actions that cannot. This way, we can clean up
the code from one-line mutations and test them simply by testing the resulting
state. However, testing the network-based state changes is not possible this
way, so it is better to leave even one line mutations that are based on the
network responses. For example, `fetchMedia` in the `mediaStore` sets
`isFetching` to true before sending the request, and to `false` after getting a
200 OK response. So, the state test would not detect the changes, and we can use
the `hasBeenCalled` mock tests in such cases instead.

### Type hinting

In the interest of a quick migration, we can continue to use the existing type
definitions for the state and the various mutations/actions from the
`types.d.ts` file. Some definitions in the file are out of date (as was the case
for `ActiveMediaState`), so it is useful to check them.

### Testing

One of the acceptance criteria for the store conversion PRs should be 100% unit
test coverage for the store module, and added e2e tests for the component
changes. It is also important to ensure that e2e tests cover both SSR and
client-side rendering. One of the acceptance criteria for the store conversion
PRs should be 100% unit test coverage for the store module, and added e2e tests
for the component changes. It is also important to ensure that e2e tests cover
both SSR and client-side rendering. Pinia Docs has a cookbook page about testing
Pinia stores, and testing components that use Pinia stores. Please note that the
setup for component testing with Vue 2 is
[slightly different from the Vue 3 setup](https://pinia.vuejs.org/cookbook/testing.html#unit-test-components-vue-2).

## Steps

0. Install Pinia and test compatibility. Create a sample Pinia store in the
   `stores` directory.

1. Replace Vuex stores with their Pinia counterparts. The order should be from
   smallest modules with fewer connections to the largest modules with more
   connections to other modules:

- `active-media` and `nav` stores - already refactored in
  [#906](https://github.com/WordPress/openverse-frontend/pull/906)
- `search` store - another PoC split into 3 PRs
  ([#1038](https://github.com/WordPress/openverse-frontend/pull/1038),
  [#1039](https://github.com/WordPress/openverse-frontend/pull/1039),
  [#1040](https://github.com/WordPress/openverse-frontend/pull/1040)) to ensure
  that Pinia stores can be used from Vuex stores, and figure out testing.
- `user` store
- `usage-data` store
- `provider` store
- `media` store

2. In the end, with no Vuex stores remaining, Vuex and all associated
   dependencies will be removed. The `store/index.js` file can also be removed
   after the complete migration to Pinia. The `disableVuex: false` flag should
   also be removed.
