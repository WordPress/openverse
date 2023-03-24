# Quickstart guide

This is the quick start guide for setting up and running the API locally.

## Prerequisites

Refer to the [general setup guide](../general_setup.md) for setting up the
prerequisites. Refer to the 'API' column in the
[requirement matrix](../general_setup.md#requirement-matrix) to know what you
need to run this.

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

3. Bring the ingestion server and API up, along with all their dependent
   services. Once this is done, you should be able to see

   - the list of ingestion jobs on
     [http://localhost:50281/task](http://localhost:50281/task)
   - the API documentation on [http://localhost:50280](http://localhost:50280)

   ```console
   $ just api/up
   ```

   The `api/up` recipe orchestrates the following services: `cache`, `db`,
   `upstream_db`, `es`, `indexer_worker`, `ingestion_server`, `web` and `proxy`.

4. Load the sample data. This step takes a few minutes. If it fails, take down
   everything with `just down -v` and start again from the previous step.

   ```console
   $ just init
   ```

   Once this step completes, you can be assured that the ingestion server is
   working fine.

5. With the data loaded, the API can now return JSON responses to your HTTP
   requests.

   ```console
   $ just api/stats
   just _curl-get "images/stats/" localhost:50280
   curl "http://localhost:50280/v1/images/stats/"
   [{"source_name":"flickr","display_name":"Flickr","source_url":"https://www.flickr.com","logo_url":null,"media_count":2500},{"source_name":"stocksnap","display_name":"StockSnap","source_url":"https://stocksnap.io","logo_url":null,"media_count":2500}]%
   ```

   If you don't have [`jq`](https://stedolan.github.io/jq/) installed, you
   should, it's great. If you do, you can pipe the response through that.

   ```console
   $ just api/stats | jq '.[0]'
   {
     "source_name": "flickr",
     "display_name": "Flickr",
     "source_url": "https://www.flickr.com",
     "logo_url": null,
     "media_count": 2500
   }
   ```

   Once this step completes, you can be assured that the API is working fine.

6. You can use a `just` recipe to bring down all the services. If you include
   the `-v` flag, it'll remove all volumes too.

   ```console
   $ just down
   $ just down -v # delete Docker volumes
   ```

7. To see the logs for all services, you can use the `logs` recipe. To see the
   logs for a particular service, pass the service name as an argument.

   ```console
   $ just logs
   $ just logs web # only see logs for the API
   ```
