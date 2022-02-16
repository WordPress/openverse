# Contributing to Openverse

Thank you for your interest in contributing to Openverse! This document is a set of guidelines to help you contribute to this project.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Project Documentation

Please consult the [README](./README.md) and [CODEBASE](./CODEBASE.md) files at the root of this repository.

## How to Contribute

Please read the processes in our general [Contributing Code](https://creativecommons.github.io/contributing-code/) guidelines on the Creative Common Open Source website. It contains some general instructions that should be followed when contributing to any of the WP Photos open-source repositories.

### Bugs and testing

If you find a bug, please open an issue in this repository describing the bug. You can file a bug [here](https://github.com/wordpress/openverse-frontend/issues/new?template=bug_report.md). You will see a bug report template with the required information you should provide.

After that, don't forget to tag the issue with the "Bug" label.

Please see our [testing guidelines](./TESTING_GUIDELINES.md) for general instructions and recommendations for how to test the application.

### Proposing changes or new features

If you have an idea of a new feature or change to how the Openverse frontend works, please [file an issue](https://github.com/wordpress/openverse-frontend/issues/new?template=feature_request.md) so we can discuss the possibility of that change or new feature being implemented and released in the future. This lets us come to an agreement about the proposed idea before any work is done.

If you'd like to build a new feature but don't have a specific idea, please check out the historic [public roadmap](https://docs.google.com/document/d/19yH2V5K4nzWgEXaZhkzD1egzrRayyDdxlzxZOTCm_pc/). Choose something from the pipeline of ideas and follow the same process as above.

### Pull requests

Before you start writing code, make sure there is an issue open. Pull requests without a link to an existing issue won't be merged. All pull requests _must_ target the `develop` branch of the repository.

If you want to get started contributing code to this project but don't know exactly what to work on, we compiled a good list of issues labeled as ['good first issues'](https://github.com/wordpress/openverse-frontend/labels/good%20first%20issue) which are small in scope and not so complex to solve. There are also issues labeled as ['help wanted'](https://github.com/wordpress/openverse-frontend/labels/help%20wanted) which can be a bit more complex but are good examples of things we are currently accepting help from the community.

Any code modifications will have to be accompanied by the appropriate unit tests. This will be checked and verified during code review. Once the pull request is opened, our CI server will run the unit test suite and run a code linter to verify that the code follows the coding guidelines.

If you want to run the unit tests and linter on your machine, run the following commands:

`npm run unit` for unit tests

`npm run lint` for linter.

You can also configure your editor of choice with a ESLint plugin so you can get the linter feedback as you write code.

### Types

We use JSDoc to document type definitions for functions throughout the code base with the eventual goal of using the TypeScript compiler to actually run a type-checker against our code. To facilitate this, we use the TypeScript "flavor" for JSDoc. Please familiarize yourself with the [documentation for TypeScript in JSDoc here](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html).

TypeScript support in Vue 2 (which we're currently locked into due to Nuxt's current limitations), is an afterthought. Therefore, types are primarily focused on the Vuex store and API service/utility functions. However, it is possible to add type annotations to some parts of Vue components, like the return value of the `data` function. Whenever possible, contributors should add or correct types to functions they are adding or modifying.

### Styles/CSS

We use [Tailwind CSS](https://tailwindcss.com/) for writing styles. There are some legacy components that have been written in "hand-written" CSS. Our aim is to eventually re-write these using Tailwind classes.

Our Tailwind configuration lives at [`./tailwind.config.js`](./tailwind.config.js) and is a useful reference for Openverse specific spacing and color classes. Please refer to the official [Tailwind CSS documentation](https://tailwindcss.com/docs) for a detailed and searchable list of the available classes. At times you'll need to cross reference this documentation with our specific configuration in the `tailwind.config.js` file.

We also use the [Tailwind CSS RTL](https://github.com/20lives/tailwindcss-rtl) plugin to make writing [right-to-left (RTL)](https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/dir) styles seamless. Most use cases of the right/left based classes should use the start/end variants introduced by the plugin instead.

## Questions or Thoughts?

Feel free to [join us on Slack](https://make.wordpress.org/chat/) and discuss the project with the engineers and community members on #openverse.
