# Nuxt vue-app template overrides

Due to a CSS ordering bug that we haven't been able to find any other solutions for, we've had to override the Nuxt templates for the `App.js` and `index.js` files to prevent any Vue components from being imported before the static CSS assets in the `nuxt.config.ts`.

## Described changes

There are two basic changes we're making all with a single goal: stop the importing of our custom `error.vue` component coming before our static CSS assets. The generated page apparently depends on this specific ordering of file imports, which is far far from ideal. Alas, there doesn't appear to be another clear solution to this problem at the moment, so we're stuck with this hack.

To update these files, it's probably easiest to just copy `App.js` and `index.js` from `node_modules/@nuxt/vue-app/template` into this directory and then apply the following transformations.

In `index.js`, move the import of `NuxtError` and `Nuxt` below importing `App`. `NuxtError` imports our custom error component and `Nuxt` imports `NuxtError`.

In `App.js`, move the `css.forEach` loop above importing `NuxtError`.
