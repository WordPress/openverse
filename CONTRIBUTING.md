# Contributing to CC Open Source

Thank you for your interest in contributing to CC Open Source! This document is a set of guidelines to help you contribute to this project.

<br/>

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](https://creativecommons.github.io/community/code-of-conduct/).

<br/>

## Project Documentation

Please consult the [README](./README.md) and [CODEBASE](./CODEBASE.md) files at the root of this repository.

<br/>

## How to Contribute

Please read the processes in our general [Contributing Code](https://creativecommons.github.io/contributing-code/) guidelines on the Creative Common Open Source website. It contains some general instructions that should be followed when contributing to any of the Creative Commons open-source repositories.

<br/>

### Bugs

If you find a bug, please open an issue in this repository describing the bug. You can file a bug [here](https://github.com/creativecommons/cccatalog-api/issues/new?template=bug_report.md). You will see a bug report template with the required information you should provide.

After that, don't forget to tag the issue with the "Bug" label.

<br/>

### Proposing changes or new features

If you have an idea of a new feature or change to how the CC Catalog API works, please [file an issue](https://github.com/creativecommons/cccatalog-api/issues/new?template=feature_request.md) so we can discuss the possibility of that change or new feature being implemented and released in the future. This lets us come to an agreement about the proposed idea before any work is done.

If you'd like to build a new feature but don't have a specific idea, please check our [public roadmap](https://docs.google.com/document/d/19yH2V5K4nzWgEXaZhkzD1egzrRayyDdxlzxZOTCm_pc/). Choose something from the pipeline of ideas and follow the same process as above.

<br/>

### Pull requests

Before you start writing code, make sure there is an issue open. Pull requests without a link to an existing issue won't be merged.

If you want to get started contributing code to this project but don't know exactly what to work on, we compiled a good list of issues labeled as [`good first issue`](https://github.com/creativecommons/cccatalog-api/labels/good%20first%20issue) which are small in scope and not so complex to solve. There are also issues labeled as [`help wanted`](https://github.com/creativecommons/cccatalog-api/labels/help%20wanted) which can be a bit more complex but are good examples of things we are currently accepting help from the community.

Any code modifications will have to be accompanied by the appropriate unit tests. This will be checked and verified during code review. Once the Pull Request is opened, our CI server will run the unit test suite and run a code linter to verify that the code follows the coding guidelines.

<br/>

## Running the tests

### How to Run API live integration tests
You can check the health of a live deployment of the API by running the live integration tests.

1. Change directory to CC Catalog API
```
cd openverse-api
```

2. Install all dependencies for CC Catalog API
```
pipenv install
```

3. Launch a new shell session
```
pipenv shell
```

4. Run API live integration test
```
./test/run_test.sh
```

<br/>

### How to Run Ingestion Server tests
You can ingest and index some dummy data using the Ingestion Server API.

1. Change directory to ingestion server
```
cd ingestion_server
```

2. Install all dependencies for Ingestion Server API
```
pipenv install
```

3. Launch a new shell session
```
pipenv shell
```

4. Run the integration tests
```
python3 test/integration_tests.py
```

<br/>

## Questions or Thoughts?

Talk to us on [our developer mailing list or Slack community](https://creativecommons.github.io/community/).
