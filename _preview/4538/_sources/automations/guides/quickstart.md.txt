# Quickstart Guide

This is a quickstart guide for locally running Openverse repository automation
scripts written in Node.js or Python.

## Prerequisites

Follow the [general setup guide](/general/general_setup.md) to set up `ov`.

## Installation

`ov just install` in the repository root directory will install all Python and
Node.js dependencies for automations as well as other parts of the repository.
If you wish to install only dependencies for automations, run the following:

- `ov pdm install` in `automations/python`
- `ov pnpm install --filter=automations`

## Running a Script

### Python

Run Python automation scripts using the `automations/python/run` just recipe.
Ex.:

```bash
ov just automations/python/run print_labels.py
```

The recipe is an alias for running `ov pdm run <script>` inside the
`automations/python` directory. This facilitates correct `PYTHONPATH`
configuration as expected by many scripts.

### Node.js

Run Node.js automation scripts using the `automations/js/run` just recipe. Ex.:

```bash
ov just automations/js/run render-jinja.js
```

The recipe is an alias for running `ov pnpm exec <script>` inside the
`automations/js` directory. As such, any `automations/js` dependencies that make
executable scripts available can also be run using the same recipe.

## Environment Variables

Many Openverse automation scripts expect to run inside a GitHub actions context
and require specific environment variables to operate. Refer to individual
script documentation (or implementation when no module documentation exists) to
know which environment variables are expected. If a script requires environment
variables, you must pass them yourself via the command line or use another
method to make the variables available to the script.
