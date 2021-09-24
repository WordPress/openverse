# Web API

## Introduction

The Openverse API is a system that allows programmatic access to public domain digital media. It is our ambition to index and catalog [billions of openly-licensed works](https://stateof.creativecommons.org/), including articles, songs, videos, photographs, paintings, and more. Using this API, developers will be able to access the digital commons in their own applications.

## Running on the host

1. Change into the API directory.
   ```bash
   cd openverse_api/
   ```

2. Setup environment if you haven't already.
   ```bash
   pipenv install
   ```

3. Start the Django dev server. Pipenv will automatically read the necessary environment variables from `.env`.
   ```bash
   pipenv run python manage.py runserver
   ```

## Running the tests

### Inside Docker (preferred)

1. Ensure that Docker containers are up. See the section above for instructions.
   ```bash
   docker-compose ps
   ```

2. Run the tests in an interactive TTY connected to a `web` container.
   ```bash
   docker-compose exec web bash ./test/run_test.sh
   ```

### On the host

1. Start the Django dev server. See the section above for instructions.

2. Change into the API directory.
   ```bash
   cd openverse_api/
   ```

3. Run the tests in a separate terminal instance. Pipenv will automatically read the necessary environment variables from `.env`.
   ```bash
   pipenv run ./test/run_test.sh
   ```

## API documentation

You can view the API documentation views at the `/v1/` endpoint. You can find more details about the API endpoints with examples on how to use them in the docs.

## Django admin

You can view the custom administration views at the `/admin/` endpoint. You can use the username 'deploy' and password 'deploy' to log in.

## Configuration

All configuration is performed through environment variables. See the `.env.docker` file for a comprehensive list of all environment variables. The ones with sane defaults have been commented out.

## Deployment

<!-- TODO -->
