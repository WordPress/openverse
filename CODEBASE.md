# Codebase overview

This document will give you a high level overview of the modules and components of the application and how they work together.

## Dependencies

The CC Search frontend is built using [Vue.JS](https://vuejs.org/) as its main view library. It uses [Vue-Router](https://router.vuejs.org/) as its routing library and Vuex(https://github.com/vuejs/vuex) as state-management library. On our production environment, we also use [Server Side Rendering](https://ssr.vuejs.org/) of the Vue app.

The app uses [CC Vocabulary](https://github.com/creativecommons/vocabulary) as a base CSS library.

[Webpack](https://webpack.js.org/) and [Babel](https://babeljs.io/) are used for build and compilation.

[Jest](https://jestjs.io/) is used for unit tests.

## Module structure

Caveat: this section doesn't render well on Github (or any other Markdown viewer). It's better to read this in raw format or in a text editor.

Below is a folder structure in the order recommended to understand how the app and its components are initialized.

-- src/
 |
 |-- main.js
 |     Main entry point of the app. Initializes the base modules such as analytics, stores and routing system. Renders the root component.
 |
 |-- App.vue
 |     App root component. All other components have this component as its parent
 |
 |-- router/(client|server).js
 |     Where the routes are defined. This is where the definitions of which page component will render for every route.
 |
 |-- store/*.js
 |     This is where the application stores are defined. Each store defines its base state, action and mutation handlers.
 |
 |-- pages/*.vue
 |     This is where the each page component is defined. Page components are the base components for each route. They define the page structure
 |     and how its sub-components are rendered. They also contain logic for loading data required to render its child components.
 |
 |-- components/*.vue
 |     Where individual sub-components are defined. Examples of sub-components include the navigation bar, individual photo details,
 |     photo tags, search results grid, etc..
 |
 |-- api/*.js
 |     Modules responsible for wrapping calls to the [CC Catalog API](https://github.com/creativecommons/cccatalog-api). This API
 |     is the base backend used to get the search results and image details.
 |
 |-- featureFlags/index.js
 |     A module used to read feature flags from environment variables, which are defined during build time, and exposing their values to the app.
 |     These feature flags are used mainly to enable/disable any given feature when necessary. Used mostly when testing new features and their behaviour before
 |     enabling them to all users.
 |
 |-- analytics/*.js
 |     Module responsible for sending real time events to Google Analytics triggered by user interaction with the application.
 |
 |-- assets/
 |     Where the static assets are stored. Assets include mostly image and svg files.
 |
