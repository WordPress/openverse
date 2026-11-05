# Quickstart guide

<!-- the main entrypoint of the Openverse documentation system -->

This guide covers the steps to get the Openverse stack running locally on your
computer. This guide is for setting up the full stack, which includes the API,
the ingestion server and the frontend.

## Stack-specific quickstarts

It is very unlikely that you want to contribute to everything, everywhere, all
at once. In all likelihood, you intend to contribute to a narrower slice of the
stack. In such cases, you might find it more beneficial to go through one of
these stack-specific quickstart guides.

- [API](/api/guides/quickstart.md)
- [Frontend](/frontend/guides/quickstart.md)
- [Ingestion server](/ingestion_server/guides/quickstart.md)
- [Documentation](/meta/documentation/quickstart.md)

That said, there is something very appealing about running the full stack
locally, which this guide is all about.

## Prerequisites

Refer to the [general setup guide](/general/general_setup.md) for setting up the
prerequisites.

## Starting up

1. Ensure you download, install and set up all prerequisites. Ensure that the
   Docker daemon is running.

2. Clone the repository to your computer. Then switch to the cloned directory.
   If you're planning to contribute, fork the repo and clone your fork instead.

   ```console
   $ git clone https://github.com/WordPress/openverse.git # or your fork
   $ cd openverse/
   ```

   If you followed the setup guide and installed
   [GitHub CLI](/general/general_setup.md#github-cli), you can clone more simply
   using the `gh` command.

   ```console
   $ gh repo clone WordPress/openverse # or your fork
   $ cd openverse/
   ```

3. Install all dependencies. This step installs dependencies for the frontend,
   the documentation and the automations (both Node.js and Python) but won't
   install API or ingestion server dependencies because they are meant to run
   using Docker containers.

   ```console
   $ just install
   ```

   To be more specific with your install, you can run either of the following.

   ```console
   $ just node-install # only frontend and Node.js automations
   $ just py-install # only documentation and Python automations
   ```

4. Spin up and orchestrate all Docker services.

   ```console
   $ just up
   ```

   The `up` recipe orchestrates the following services: `cache`, `db`,
   `upstream_db`, `es`, `indexer_worker`, `ingestion_server`, `web`, `proxy`,
   `webserver`, `scheduler`, `s3`, `plausible-ch`, `plausible-db` and
   `plausible`.

   The `up` recipe also prints out services that have ports exposed to the host
   (this can also be seen by running `just ps`):

   ```
   ================================================================================
                                    Service Ports
   ================================================================================
   webserver (catalog):
   -  http://0.0.0.0:9090 (→ 8080)
   ingestion_server (ingestion_server):
   -  http://0.0.0.0:50281 (→ 8001)
   plausible (plausible/analytics):
   -  http://0.0.0.0:50288 (→ 8000)
   web (api):
   -  http://0.0.0.0:50280 (→ 8000)
   -  http://0.0.0.0:50230 (→ 3000)
   s3 (minio/minio):
   -  http://0.0.0.0:5010 (→ 5000)
   -  http://0.0.0.0:5011 (→ 5001)
   db (postgres):
   -  http://0.0.0.0:50254 (→ 5432)
   es (docker.elastic.co/elasticsearch/elasticsearch):
   -  http://0.0.0.0:50292 (→ 9200)
   cache (redis):
   -  http://0.0.0.0:50263 (→ 6379)
   ================================================================================
   ```

   For example, you can access the following endpoints:

   - the list of ingestion jobs on
     [http://localhost:50281/task](http://localhost:50281/task)
   - the API documentation on [http://localhost:50280](http://localhost:50280)
   - the Plausible UI on [http://localhost:50288](http://localhost:50288)

5. Load the sample data. This step can take a few minutes to complete.

   ```console
   $ just init
   ```

   ````{admonition} Troubleshooting
   If this step fails, cleaning up and restarting usually fixes it.

   ```console
   $ just down -v
   $ just api/init
   ```
   ````

6. With the data loaded, the API can now return JSON responses to your HTTP
   requests.

   ```console
   $ just api/stats
   just _curl-get "images/stats/" localhost:50280
   curl "http://localhost:50280/v1/images/stats/"
   [{"source_name":"flickr","display_name":"Flickr","source_url":"https://www.flickr.com","logo_url":null,"media_count":2500},{"source_name":"stocksnap","display_name":"StockSnap","source_url":"https://stocksnap.io","logo_url":null,"media_count":2500}]%
   ```

   ````{tip}
   [`jq`](https://stedolan.github.io/jq/) is a tool for parsing and manipulating
   JSON data. If you have `jq` installed, you can pipe the response to it and
   transform it.

   ```console
   $ just api/stats | jq '.[0]'
   {
     "source_name": "flickr",
     "display_name": "Flickr",
     "source_url": "https://www.flickr.com",
     "logo_url": null,
     "media_count": 2500
   }

   $ just api/stats 'audio' | jq '[.[] | .source_name]'
   [
     "freesound",
     "jamendo",
     "wikimedia_audio"
   ]
   ```

   `jq` is great, we recommend you
   [download](https://stedolan.github.io/jq/download/) it.
   ````

7. To bring up the frontend, we have another `just` recipe. We have `just`
   recipes for almost everything.

   ```console
   $ env API_URL="http://localhost:50280" just frontend/run dev
   ```

   Now you should be able to access the following endpoints:

   - the Openverse search engine frontend on
     [http://localhost:8443](http://localhost:8443)

## Shutting down

1. You can <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the frontend process.

2. For services running inside Docker, like the API, ingestion server and
   Plausible, use another `just` recipe to bring them down.

   ```console
   $ just down
   ```

   ````{tip}
   If you include the `-v` flag, all Docker volumes (including their data) will
   be deleted too, which is useful in case you want a fresh start.

   ```console
   $ just down -v
   ```
   ````
