# Local HTTPS testing

To access the API over HTTPS, we need to proxy to it using NGINX. Note that this
proxy is different from the API NGINX image that is specifically aimed at
serving static files in live environments.

## Prerequisites

Make sure you have gone through the
[quickstart guide](/api/guides/quickstart.md) before attempting this as this is
a slightly more advanced process.

Additionally, you will need to install
[mkcert](/general/general_setup.md#mkcert) as described in the
[general setup guide](/general/general_setup.md).

## Steps

1. Create certificates for NGINX to use.

   ```console
   $ just docker/nginx/cert
   ```

   This will create a certificate file `openversse.crt` and a key file
   `openverse.key` in the `docker/nginx/certs/` directory.

2. Bring the ingestion server and API up, along with all their dependent
   services.

   ```console
   $ just api/up
   ```

   The `api/up` recipe orchestrates the following services: `cache`, `db`,
   `upstream_db`, `es`, `indexer_worker`, `ingestion_server`, `web` and `proxy`.

   Note that the `proxy` service here is the NGINX instance that will handle our
   HTTPS requests.

3. Make an API call over HTTPS.

   ```console
   $ just api/stats images https://localhost:50243
   just _curl-get "images/stats/" https://localhost:50243
   curl "https://localhost:50243/v1/images/stats/"
   [{"source_name":"flickr","display_name":"Flickr","source_url":"https://www.flickr.com","logo_url":null,"media_count":2500},{"source_name":"stocksnap","display_name":"StockSnap","source_url":"https://stocksnap.io","logo_url":null,"media_count":2500}]%
   ```
