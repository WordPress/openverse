# Deployment

This document describes the steps necessary for deploying the catalog on our AWS EC2 instance.
For convenience (and access frequency), instructions for deploying an update are provided first.
If you wish to deploy a new instance, see [Deploying a fresh instance](#deploying-a-fresh-instance).

**Note**: All steps assume that the environment variable `IS_PROD` is set to `true` in the bash session being used for deployment.
If it is not `export`ed for the session, `IS_PROD=true` will need to be prepended to all `just` commands (e.g. `IS_PROD=true just build`)

## Deploying an update to DAG files

1. `git pull` _(Yes, that's it! Airflow will take a few moments to populate the changes.)_

## Deploying an update to the Docker image or non-DAG code

1. Verify that any new Airflow Variables, Airflow Connections, or environment variables have been added or updated.
2. Run `just deploy` within the repository's folder.

## Deploying a fresh instance

1. Clone the repository onto the target machine.
2. Run `just dotenv` to create a new `.env` file from the template.
3. Generate a secure password for the `airflow` account on the Airflow Metastore DB, and update the account using `ALTER USER airflow WITH PASSWORD '<generated-password>';`  _(Note: this process will be changed in [gh-260](https://github.com/WordPress/openverse-catalog/issues/260))_
4. Create an `AIRFLOW__CORE__FERNET_KEY` using the instructions described in the `.env` file
5. Change the following variables in the `.env` file:
   - **(Required)**
      - `AIRFLOW__CORE__SQL_ALCHEMY_CONN` (using the password created above)
      - `AIRFLOW__CORE__HIDE_SENSITIVE_VAR_CONN_FIELDS`
      - `AIRFLOW_VAR_ENVIRONMENT` (set to `prod`)
      - `AIRFLOW_CONN_AWS_DEFAULT`
      - `AIRFLOW_CONN_POSTGRES_OPENLEDGER_UPSTREAM`
      - `AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING`
      - `AWS_ACCESS_KEY`
      - `AWS_SECRET_KEY`
   - **(Recommended)**
       - `AIRFLOW_PORT`
       - `LOADER_FILE_AGE`
       - Any API key variables
6. Run `just build`, verify the image built correctly
7. Run `just up`, verify that the Airflow container has started successfully
8. Run `just airflow "users create -r Admin -u <username> -f <first-name> -l <last-name> -p <password> --email <email>"` with desired information to create an Administrator account for the Airflow UI
