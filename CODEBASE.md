# Codebase overview

This document will give you a high level overview of the modules and components of the application and how they work together.

## Dependencies

The CC Search frontend is built using [Vue.JS](https://vuejs.org/) as its main view library. The app uses [Vocabulary](https://github.com/creativecommons/vocabulary) for vue components and global CSS.

It uses [NuxtJS](https://nuxtjs.org/) as a meta framework to handle serveral key functions:

- Server Side rendering in production
- Lifecycle methods for data fetching on client and server-side page loads
- Building the application for production

If something in the codebase confuses you, it may be a feature of NuxtJS, so make sure you check out their documentation.

NuxtJS is built on top of standard libraries in the Vue ecosystem. It uses [Vue-Router](https://router.vuejs.org/) as its routing library and [Vuex](https://github.com/vuejs/vuex) as state-management library.

[Jest](https://jestjs.io/) is used for unit tests. [Cypress](cypress.io) for end-to-end (e2e) tests, to simulate the user experience and make sure all of our unit-tested components are working in harmony.

## Basic repository structure

### In the project root

The root of the repository contains several configuration files for code formatting, and configuration, for prettier, nuxt, docker, eslint, and other config files

[`nuxt.config.js`](./nuxt.config.js) is an important file. It contains several key pieces of configuration. You can [read more about the NuxtJS config file here](https://nuxtjs.org/guides/configuration-glossary/configuration-build).

- environment variables are set in the `export const env = {}` object. Varibles are set with camel case names like this `process.env.varNameGoesHere` and their default values are formatted in the more conventional `process.env.VAR_NAME_GOES_HERE` format.
- Default HTML metadata and Nuxt plugins are added
- `/src` All JavaScript code lives in the src directory.
