# Web API

## Introduction

The Openverse API is a system that allows programmatic access to public domain digital media. It is our ambition to index and catalog [billions of openly-licensed works](https://stateof.creativecommons.org/), including articles, songs, videos, photographs, paintings, and more. Using this API, developers will be able to access the digital commons in their own applications.

## Running on the host

1. Create environment variables from the stencil file.
   ```bash
   just env
   ```

2. Install Python dependencies.
   ```bash
   just install
   ```

3. Start the Django dev server.
   ```bash
   just dj runserver
   ```

## Running the tests

### Inside Docker (preferred)

1. Ensure that Docker containers are up.
   ```bash
   docker-compose ps
   ```

2. Run the tests in an interactive TTY connected to a `web` container.
   ```bash
   just api-test
   ```

### On the host

1. Start the Django dev server. See the section above for instructions.

2. Run the tests in a terminal on the host.
   ```bash
   just api-testlocal
   ```

## API documentation

You can view the API documentation views at the `/v1/` endpoint. You can find more details about the API endpoints with examples on how to use them in the docs.

## Django admin

You can view the custom administration views at the `/admin/` endpoint. You can use the username 'deploy' and password 'deploy' to log in.

## Configuration

All configuration is performed through environment variables. See the `env.template` file for a comprehensive list of all environment variables. The ones with sane defaults have been commented out.

Pipenv will automatically load `.env` files when running commands with `pipenv run`.

## Deployment

<!-- TODO -->
