# Contributing to CC Open Source

Thank you for your interest in contributing to CC Open Source! This document is a set of guidelines to help you contribute to this project.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](https://creativecommons.github.io/community/code-of-conduct/).

## Project Documentation

Please consult the [README](./README.md) file at the root of this repository.

## How to Contribute

Please read the processes in our general [Contributing Code](https://creativecommons.github.io/contributing-code/) guidelines on the Creative Common Open Source website. It contains some general instructions that should be followed when contributing to any of the Creative Commons open-source repositories.

### Bugs

If you find a bug, please open an issue in this repository describing the bug. The bug description should contain:

* Step-by-step to reproduce
* What the expected behaviour is
* Which browsers, including their versions, and operating system were used to reproduce the bug

Example of a good bug description:

```
License filters don't work as expected

How to reproduce:

- Go to home page
- Search for any term (eg: nature)
- In the search results page, click on Filter and select CC-BY-SA on the "All licenses" select
- Click on the third image (<link to image>)
- The image isn't licensed as CC-BY-SA but as CC-BY-NC instead

Expected behaviour

- Only images licensed as CC-BY-SA should be displayed in the search results page

Browser used:

Safari 12.0.3, MacOS 10.14.3
Firefox 66.0.2, MacOS 10.14.3
```

After that, don't forget to tag the issue with the "Bug" label.

### Proposing changes or new features

If you have an idea of a new feature or change to how the CC Search frontend works, please file an issue so we can discuss the possibility of that change or new feature being implemented and released in the future. This lets us come to an agreement about the proposed idea before any work is done.

### Pull requests

Before you start writing code, make sure there is an issue open. Pull requests without a link to an existing issue won't be merged.

If you want to get started contributing code to this project but don't know exactly what to work on, we compiled a good list of issues labeled as [Good first issues](https://github.com/creativecommons/cccatalog-frontend/labels/good%20first%20issue) which are small in scope and not so complex to solve. There is also issues labeld as [Help wanted](https://github.com/creativecommons/cccatalog-frontend/labels/help%20wanted) which can be a bit more complex but are good examples of thigns we are currently accepting help from the community.

Once you open your Pull Request, make sure that its description contains the following information:

* Short description explaining the high-level reason for the pull request

* *Link to existing Issue #

* If this Pull Request contains any UI changes, provide an image or GIF displaying the changes

Any code modifications will have to be accompanied by the appropriate unit tests. This will be checked and verified during code review. Once the Pull Reques is opened, our CI server will run the unit test suite and run a code linter to verify that the code follows the coding guidelines.

If you want to run the unit tests and linter on your machine, run the following commands:

`npm run unit` for unit tests

`npm run lint` for linter.

You can also configure your editor of choice with a ESLint plugin so you can get the linter feedback as you write code.

## Questions or Thoughts?

Talk to us on [our developer mailing list or Slack community](https://creativecommons.github.io/community/).
