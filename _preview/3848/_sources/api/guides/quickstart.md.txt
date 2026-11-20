# Quickstart guide

This is the quick start guide for setting up and running the API locally.

## Prerequisites

Refer to the [general setup guide](/general/general_setup.md) for setting up the
prerequisites. Refer to the 'API' column in the
[requirement matrix](/general/general_setup.md#requirement-matrix) to know what
you need to run this.

## Starting up

1. Ensure you download, install and set up all prerequisites. Ensure that the
   Docker daemon is running.

2. Clone the repository to your computer. Then switch to the cloned directory.
   If you're planning to contribute, fork the repo and clone your fork instead.

   ```bash
   git clone https://github.com/WordPress/openverse.git # or your fork
   cd openverse/
   ```

   If you followed the general setup guide and installed
   [GitHub CLI](/general/general_setup.md#github-cli), you can clone more simply
   using the `gh` command.

   ```bash
   gh repo clone WordPress/openverse # or your fork
   cd openverse/
   ```

3. Bring the ingestion server and API up, along with all their dependent
   services.

   ```bash
   just api/up
   ```

   The `api/up` recipe orchestrates the following services: `cache`, `db`,
   `upstream_db`, `es`, `indexer_worker`, `ingestion_server`, `web` and `proxy`.

   Now you should be able to access the following endpoints:

   - the list of ingestion jobs on
     [http://localhost:50281/task](http://localhost:50281/task)
   - the API documentation on [http://localhost:50280](http://localhost:50280)

4. Load the sample data. This step can take a few minutes to complete.

   ```bash
   just api/init
   ```

   ````{admonition} Troubleshooting
   If this step fails, cleaning up and restarting usually fixes it.

   ```bash
   just down -v
   just api/init
   ```
   ````

5. With the data loaded, the API can now return JSON responses to your HTTP
   requests.

   ```bash
   just api/stats
   just _curl-get "images/stats/" http://localhost:50280
   curl "http://localhost:50280/v1/images/stats/"
   [{"source_name":"flickr","display_name":"Flickr","source_url":"https://www.flickr.com","logo_url":null,"media_count":2500},{"source_name":"stocksnap","display_name":"StockSnap","source_url":"https://stocksnap.io","logo_url":null,"media_count":2500}]%
   ```

   ````{tip}
   [`jq`](https://stedolan.github.io/jq/) is a tool for parsing and manipulating
   JSON data. If you have `jq` installed, you can pipe the response to it and
   transform it.

   ```bash
   just api/stats | jq '.[0]'
   {
     "source_name": "flickr",
     "display_name": "Flickr",
     "source_url": "https://www.flickr.com",
     "logo_url": null,
     "media_count": 2500
   }

   just api/stats 'audio' | jq '[.[] | .source_name]'
   [
     "freesound",
     "jamendo",
     "wikimedia_audio"
   ]
   ```

   `jq` is great, we recommend you
   [download](https://stedolan.github.io/jq/download/) it.
   ````

## Shutting down

Refer to the [common instructions](/general/quickstart.md#shutting-down).
