# API quickstart guide

This is the quick start guide for setting up and running the API locally.

## Prerequisites

Follow the [general setup guide](/general/general_setup.md) to set up `ov`.

## Starting up

1. Start the API along with its dependencies:

   ```bash
   ov just api/up
   ```

   The `api/up` recipe orchestrates the following services: `cache`, `db`,
   `upstream_db`, `es`, `indexer_worker`, `ingestion_server`, `web` and `proxy`.

   Now you should be able to access the following endpoints:

   - the list of ingestion jobs on
     [http://localhost:50281/task](http://localhost:50281/task)
   - the API documentation on [http://localhost:50280](http://localhost:50280)

1. Load the sample data. This step can take a few minutes to complete.

   ```bash
   ov just api/init
   ```

   ````{admonition} Troubleshooting
   If this step fails, cleaning up and restarting usually fixes it.

   ```bash
   ov just down -v
   ov just api/init
   ```
   ````

1. With the data loaded, the API can now return JSON responses to your HTTP
   requests.

   ```bash
   ov just api/stats
   ov just _curl-get "images/stats/" http://localhost:50280
   [{"source_name":"flickr","display_name":"Flickr","source_url":"https://www.flickr.com","logo_url":null,"media_count":2500},{"source_name":"stocksnap","display_name":"StockSnap","source_url":"https://stocksnap.io","logo_url":null,"media_count":2500}]%
   ```

   ````{tip}
   Use `jq`, [one of the tools included in `ov`](/general/general_setup.md#included-tools) to filter JSON output and make it easier to read:

   ```bash
   ov just api/stats | ov jq '.[0]'
   {
     "source_name": "flickr",
     "display_name": "Flickr",
     "source_url": "https://www.flickr.com",
     "logo_url": null,
     "media_count": 2500
   }

   ov just api/stats 'audio' | ov jq '[.[] | .source_name]'
   [
     "freesound",
     "jamendo",
     "wikimedia_audio"
   ]
   ```
   ````

## Shutting down

Refer to the [common instructions](/general/general_setup.md#shutting-down).
