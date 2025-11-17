# Quickstart Guide

This is a quickstart guide for locally running Openverse repository automation
scripts written in Node.js or Python.

## Prerequisites

Refer to the [general setup guide](/general/general_setup.md) for setting up the
prerequisites. Refer to the 'Management' column in the
[requirement matrix](/general/general_setup.md#requirement-matrix) to know what
you need to run this.

## Installation

`./ov just install` in the repository root directory will install all Python and
Node.js dependencies for automations as well as other parts of the repository.
If you wish to install only dependencies for automations, run the following:

- `pipenv install` in `automations/python`
- `pnpm install --filter=automations`

## Running a Script

### Python

Run Python automation scripts using the `automations/python/run` just recipe.
Ex.:

```bash
./ov just automations/python/run print_labels.py
```

The recipe is an alias for running `pipenv run <script>` inside the
`automations/python` directory. This facilitates correct `PYTHONPATH`
configuration as expected by many scripts.

### Node.js

Run Node.js automation scripts using the `automations/js/run` just recipe. Ex.:

```bash
./ov just automations/js/run render-jinja.js
```

The recipe is an alias for running `pnpm exec <script>` inside the
`automations/js` directory. As such, any `automations/js` dependencies that make
executable scripts available can also be run using the same recipe.

## Environment Variables

Many Openverse automation scripts expect to run inside a GitHub actions context
and require specific environment variables to operate. Refer to individual
script documentation (or implementation when no module documentation exists) to
know which environment variables are expected.
[Pipenv automatically loads `.env` files](https://pipenv-fork.readthedocs.io/en/latest/advanced.html#automatic-loading-of-env)
so for ease of use, you may place relevant environment variables in
`automations/python/.env`. Unlike Pipenv, however, pnpm does _not_ automatically
load environment variables. If a Node.js script requires environment variables,
you must pass them yourself via the command line or use another method to make
the variables available to the script.
