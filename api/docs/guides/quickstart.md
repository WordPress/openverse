# Quickstart

## Prerequisites

- [Git](https://git-scm.com/downloads)
- [Docker](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Just](https://github.com/casey/just)

## Steps

1. Ensure that the [Docker daemon](https://docs.docker.com/config/daemon/) is running.

2. Clone the repository and `cd` into it. This is the monorepo root.
   ```bash
   git clone https://github.com/WordPress/openverse-api.git
   cd openverse-api/
   ```

3. From the monorepo root, bring up the Docker Compose system. Docker Compose will automatically read the necessary environment variables from `env.docker` files from project directories.
   ```bash
   just up
   ```

4. Point your browser to `http://localhost:8000`. You should be able to see the API documentation.
   ![API ReDoc](/_static/api_redoc.png)

5. Load the sample data. This could take a couple of minutes.
   ```bash
   just init
   ```

6. Make an API request using cURL. You should receive a JSON response.
   ```bash
   just stats
   ```

   Piping the response through a pretty-printer like [`jq`](https://stedolan.github.io/jq/) should yield an output like the following.
   ```bash
   just stats | jq '.[0]'
   ```

   ```json
   {
     "source_name":   "flickr",
     "display_name": "Flickr",
     "source_url": "https://www.flickr.com",
     "logo_url": null,
     "media_count": 1000
   }
   ```

7. When done, bring the system down. To remove all volumes as well, pass the `-v` flag.
   ```bash
   just down
   just down -v # removes volumes
   ```

8. Use the `logs` command access the logs from all services. To isolate a service, pass the service name as an argument.
   ```bash
   just logs
   just logs web # only shows logs web service
   ```

### Services

The command `just up` spawns the following services:

- [PostgreSQL](https://www.postgresql.org/) x 2 instances
  - upstream data source simulator
  - API application database
- [Elasticsearch](https://www.elastic.co/elasticsearch/)
- [Redis](https://redis.io/)
- [imageproxy](https://github.com/willnorris/imageproxy)
- **web** (`api/`)
- **ingestion_server** and **indexer_worker** (`ingestion_server/`)
- **analytics** (`analytics/`)

The last three are subprojects of this monorepo.

## Troubleshooting

If the Elasticsearch container fails to start on your machine, there's a good chance the container ran out of memory. Ensure that you have allocated enough memory to Docker applications and re-run the `just up` command.

If the logs mention "insufficient max map count", you may also need to increase the number of open files allowed on your system. For most Linux machines, you can fix this by adding the following line to `/etc/sysctl.conf`:
```ini
vm.max_map_count=262144
```

To make this setting take effect, update kernel state:
```bash
sudo sysctl -p
```
