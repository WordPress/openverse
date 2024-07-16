# Local HTTPS testing

To access the API over HTTPS, we need to proxy to it using NGINX. Note that this
proxy is different from the API NGINX image that is specifically aimed at
serving static files in live environments.

## Prerequisites

Make sure you have gone through the
[quickstart guide](/api/guides/quickstart.md) before attempting this as this is
a slightly more advanced process.

Additionally, you will need to install `mkcert`.
[Follow `mkcert`'s installation guide](https://github.com/FiloSottile/mkcert?tab=readme-ov-file#installation)
to do so.

```{caution}
`ov` does not yet support mkcert. You must run this command without `ov`
on your host system for it to work.
```

## Steps

1. Create certificates for NGINX to use.

   ```{caution}
   Run this on your host system, `ov` does not support mkcert.
   ```

   ```bash
   just docker/nginx/cert
   ```

   This will create a certificate file `openversse.crt` and a key file
   `openverse.key` in the `docker/nginx/certs/` directory.

2. Start the API along with its dependencies:

   ```bash
   ov just api/up
   ```

   The `api/up` recipe orchestrates the following services: `cache`, `db`,
   `upstream_db`, `es`, `indexer_worker`, `ingestion_server`, `web` and `proxy`.

   Note that the `proxy` service here is the NGINX instance that will handle our
   HTTPS requests.

3. Make an API call over HTTPS.

   ```bash
   ov just api/stats images https://localhost:50243
   ov just _curl-get "images/stats/" https://localhost:50243
   [{"source_name":"flickr","display_name":"Flickr","source_url":"https://www.flickr.com","logo_url":null,"media_count":2500},{"source_name":"stocksnap","display_name":"StockSnap","source_url":"https://stocksnap.io","logo_url":null,"media_count":2500}]%
   ```
