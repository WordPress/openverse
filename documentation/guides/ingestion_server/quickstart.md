# Quickstart guide

This is the quick start guide for setting up and running the ingestion server
locally.

## Prerequisites

Refer to the [general setup guide](../general_setup.md) for setting up the
prerequisites.

## Steps

1. Ensure you download, install and set up all prerequisites. Ensure that the
   Docker daemon is running.

2. Clone the repository to your computer. Then switch to the cloned directory.
   If you're planning to contribute, fork the repo and clone your fork instead.

   ```console
   $ git clone https://github.com/WordPress/openverse.git # or your fork
   $ cd openverse/
   ```

   If you followed the general setup guide and installed
   [GitHub CLI](./general_setup.md#github-cli), you can clone more simply using
   the `gh` command.

   ```console
   $ gh repo clone WordPress/openverse # or your fork
   $ cd openverse/
   ```

3. Bring the ingestion server up, along with all their dependent services. Once
   this is done, you should be able to see the list of ingestion jobs on
   [http://localhost:50281/task](http://localhost:50281/task).

   ```console
   $ just ingestion_server/up
   ```

4. Load the sample data. This step take a few minutes. If it fails, take down
   everything with `just down -v` and start again from the previous step.

   ```console
   $ just init
   ```

   The ingestion server is working fine.

5. You can use a `just` recipe to bring down all the services. If you include
   the `-v` flag, it'll remove all volumes too.

   ```console
   $ just down
   $ just down -v # delete Docker volumes
   ```

6. To see the logs for all services, you can use the `logs` recipe. To see the
   logs for a particular service, pass the service name as an argument.

   ```console
   $ just logs
   $ just logs ingestion_server # only see logs for the ingestion server
   ```
