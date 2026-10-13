# Quickstart

This guide covers the steps to get the Openverse stack running locally on your
computer.

## Prerequisites

- [Git](https://git-scm.com/downloads)
- [Docker](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Just](https://github.com/casey/just)
- [coreutils](https://formulae.brew.sh/formula/coreutils) (only for macOS)

The following prerequisites are optional, and only needed in some very specific
cases.

- [mkcert](https://github.com/FiloSottile/mkcert)

  This is only needed to test SSL locally. Ensure that you have installed
  `mkcert` (and the corresponding NSS tools). You can run `mkcert -install` to
  verify your installation.

- [OpenSSL](https://formulae.brew.sh/formula/openssl)

  This is only need if the `psycopg2` install fails with the
  `ld: library not found for -lssl` error. Install `openssl` from Homebrew and
  set `LDFLAGS` and `CPPFLAGS` as given in the installation output.

## Steps

1. Ensure you download, install and set up all prerequisites. Ensure that the
   Docker daemon is running.

2. Clone the repository to your computer. Then switch to the cloned directory.

   ```console
   $ git clone https://github.com/WordPress/openverse.git
   $ cd openverse
   ```

3. Install all dependencies. This is generally not advisable unless you plan to
   work on everything! This step won't install API or ingestion-server
   dependencies because they are meant to run using Docker containers.

   ```console
   $ just install
   ```

4. Bring the ingestion server and API up, along with all their dependent
   services. Once this is done, you should be able to see the API documentation
   on [http://localhost:50280](http://localhost:50280).

   ```console
   $ just up
   ```

5. Load the sample data. This step take a few minutes. If it fails, take down
   everything with `just down -v` and start again from the previous step.

   ```console
   $ just init
   ```

   The ingestion server is working fine.

6. With the data loaded, the API can now return JSON responses to your HTTP
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

   The API is working fine.

7. To bring up the frontend, we have another `just` recipe. We have `just`
   recipes for almost everything. You can open
   [http://localhost:8443](http://localhost:8443) in a browser to see your very
   own copy of Openverse.

   ```console
   $ env API_URL="http://localhost:50280" just frontend/run dev
   ```

   The frontend is working fine.

8. You can <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the frontend process.
   Then use another `just` recipe to bring down all the services. If you include
   the `-v` flag, it'll remove all volumes too.

   ```console
   $ just down
   $ just down -v # delete Docker volumes
   ```

9. To see the logs for all services, you can use the `logs` recipe. To see the
   logs for a particular service, pass the service name as an argument.

   ```console
   $ just logs
   $ just logs web # only see logs for web
   ```
