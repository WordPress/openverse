# Quickstart guide

This is the quick start guide for setting up and running the ingestion server
locally.

## Prerequisites

Refer to the [general setup guide](/general/general_setup.md) for setting up the
prerequisites. Refer to the 'Ingestion server' column in the
[requirement matrix](/general/general_setup.md#requirement-matrix) to know what
you need to run this.

## Starting up

1. Ensure you download, install and set up all prerequisites. Ensure that the
   Docker daemon is running.

2. Clone the repository to your computer. Then switch to the cloned directory.
   If you're planning to contribute, fork the repo and clone your fork instead.

   ```{note}
   We recommend cloning with the `--filter=blob:none` flag as it dramatically
   reduces the filesize and download time by creating a "blobless clone".
   You can learn more about these [here](https://gist.github.com/leereilly/1f4ea46a01618b6e34ead76f75d0784b).
   ```

   ```bash
   git clone --filter=blob:none https://github.com/WordPress/openverse.git # or your fork
   cd openverse/
   ```

   If you followed the general setup guide and installed
   [GitHub CLI](/general/general_setup.md#github-cli), you can clone more simply
   using the `gh` command.

   ```bash
   gh repo clone WordPress/openverse -- --filter=blob:none  # or your fork
   cd openverse/
   ```

3. Bring the ingestion server up, along with all their dependent services.

   ```bash
   just ingestion_server/up
   ```

   The `ingestion_server/up` recipe orchestrates the following services: `db`,
   `upstream_db`, `es`, `indexer_worker` and `ingestion_server`.

   Now you should be able to access the following endpoints:

   - The list of ingestion jobs on
     [http://localhost:50281/task](http://localhost:50281/task)

   You can view logs for the service using `./ov just logs ingestion_server`.

## Shutting down

Refer to the [common instructions](/general/quickstart.md#shutting-down).
