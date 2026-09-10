# Quickstart

This repository contains the methods used to identify over 1.4 billion Creative
Commons licensed works. The challenge is that these works are dispersed
throughout the web and identifying them requires a combination of techniques.

Currently, we only pull data from APIs which serve Creative Commons licensed
media. In the past, we have also used web crawl data as a source.

## API Data

[Apache Airflow](https://airflow.apache.org/) is used to manage the workflow for
various API ETL jobs which pull and process data from a number of open APIs on
the internet.

### API Workflows

To view more information about all the available workflows (DAGs) within the
project, see [DAGs.md](../reference/DAGs.md).

See each provider API script's notes in their respective [handbook][ov-handbook]
entry.

[ov-handbook]: https://make.wordpress.org/openverse/handbook/openverse-handbook/

## Web Crawl Data (retired)

The Common Crawl Foundation provides an open repository of petabyte-scale web
crawl data. A new dataset is published at the end of each month comprising over
200 TiB of uncompressed data.

The data is available in three file formats:

- WARC (Web ARChive): the entire raw data, including HTTP response metadata,
  WARC metadata, etc.
- WET: extracted plaintext from each webpage.
- WAT: extracted html metadata, e.g. HTTP headers and hyperlinks, etc.

For more information about these formats, please see the [Common Crawl
documentation][ccrawl_doc].

Openverse Catalog used AWS Data Pipeline service to automatically create an
Amazon EMR cluster of 100 c4.8xlarge instances that parsed the WAT archives to
identify all domains that link to creativecommons.org. Due to the volume of
data, Apache Spark was also used to streamline the processing. The output of
this methodology was a series of parquet files that contain:

- the domains and its respective content path and query string (i.e. the exact
  webpage that links to creativecommons.org)
- the CC referenced hyperlink (which may indicate a license),
- HTML meta data in JSON format which indicates the number of images on each
  webpage and other domains that they reference,
- the location of the webpage in the WARC file so that the page contents can be
  found.

The steps above were performed in [`ExtractCCLinks.py`][ex_cc_links].

This method was retired in 2021.

[ccrawl_doc]: https://commoncrawl.org/the-data/get-started/
[ex_cc_links]:
  https://github.com/WordPress/openverse/blob/c20262cad8944d324b49176678b16b230bc57e2e/archive/ExtractCCLinks.py

## Development setup for Airflow and API puller scripts

There are a number of scripts in the directory
[`catalog/dags/provider_api_scripts`][api_scripts] eventually loaded into a
database to be indexed for searching in the Openverse API. These run in a
different environment than the PySpark portion of the project, and so have their
own dependency requirements.

For instructions geared specifically towards production deployments, see
[DEPLOYMENT.md](https://github.com/WordPress/openverse/blob/main/catalog/DEPLOYMENT.md)

[api_scripts]:
  https://github.com/WordPress/openverse/blob/main/catalog/dags/providers/provider_api_scripts

### Requirements

You'll need `docker` and `docker-compose` installed on your machine, with
versions new enough to use version `3` of Docker Compose `.yml` files.

You will also need the [`just`](https://github.com/casey/just#installation)
command runner installed.

### Setup

To set up the local python environment along with the pre-commit hook, run:

```shell
python3 -m venv venv
source venv/bin/activate
just install
```

The containers will be built when starting the stack up for the first time. If
you'd like to build them prior to that, run:

```shell
just build
```

### Environment

To set up environment variables run:

```shell
just dotenv
```

This will generate a `.env` file which is used by the containers.

The `.env` file is split into four sections:

1. Airflow Settings - these can be used to tweak various Airflow properties
2. API Keys - set these if you intend to test one of the provider APIs
   referenced
3. Connection/Variable info - this will not likely need to be modified for local
   development, though the values will need to be changed in production
4. Other config - misc. configuration settings, some of which are useful for
   local dev

The `.env` file does not need to be modified if you only want to run the tests.

### Running & Testing

There is a [`docker-compose.yml`][dockercompose] provided in the
[`catalog`][cc_airflow] directory, so from that directory, run

```shell
just up
```

This results, among other things, in the following running containers:

- `openverse_catalog_webserver_1`
- `openverse_catalog_postgres_1`
- `openverse_catalog_s3_1`

and some networking setup so that they can communicate. Note:

- `openverse_catalog_webserver_1` is running the Apache Airflow daemon, and also
  has a few development tools (e.g., `pytest`) installed.
- `openverse_catalog_postgres_1` is running PostgreSQL, and is setup with some
  databases and tables to emulate the production environment. It also provides a
  database for Airflow to store its running state.
- The directory containing all modules files (including DAGs, dependencies, and
  other tooling) will be mounted to the directory `/opt/airflow/catalog` in the
  container `openverse_catalog_webserver_1`. On production, only the DAGs folder
  will be mounted, e.g. `/opt/airflow/openverse/dags`.

The various services can be accessed using these links:

- Airflow: `localhost:9090` (The default username and password are both
  `airflow`.)
- Minio Console: `localhost:5011` (The default username and password are
  `test_key` and `test_secret`)
- Postgres: `localhost:5434` (using a database connector)

At this stage, you can run the tests via:

```shell
just test

# Alternatively, run all tests including longer-running ones
just test --extended
```

Edits to the source files or tests can be made on your local machine, then tests
can be run in the container via the above command to see the effects.

If you'd like, it's possible to login to the webserver container via:

```shell
just shell
```

If you just need to run an airflow command, you can use the `airflow` recipe.
Arguments passed to airflow must be quoted:

```shell
just run scheduler airflow config list
```

To follow the logs of the running container:

```shell
just logs
```

To begin an interactive [`pgcli` shell](https://www.pgcli.com/) on the database
container, run:

```shell
just db-shell
```

If you'd like to bring down the containers, run

```shell
just down
```

To reset the test DB (wiping out all databases, schemata, and tables), run

```shell
just down -v
```

`docker volume prune` can also be useful if you've already stopped the running
containers, but be warned that it will remove all volumes associated with
stopped containers, not just openverse-catalog ones.

To fully recreate everything from the ground up, you can use:

```shell
just recreate
```

> **Note**: Any recipes or scripts which output files to the container's mounted
> volumes will need to be run as the root user. This can be done with the
> `DC_USER=root` environment variable for `just` recipes. For example, see the
> [generate-dag-docs recipe](https://github.com/WordPress/openverse-catalog/blob/c9be67e483e49e9eda7cd21b52bcde8857cd3922/justfile#L126).

[justfile]: https://github.com/WordPress/openverse/blob/main/catalog/justfile
[dockercompose]:
  https://github.com/WordPress/openverse/blob/main/docker-compose.yml
[cc_airflow]: https://github.com/WordPress/openverse/tree/main/catalog

## Directory Structure

```text
openverse-catalog
├── .github/                                # Templates for GitHub
├── archive/                                # Files related to the previous CommonCrawl parsing implementation
├── docker/                                 # Dockerfiles and supporting files
│   └── upstream_db/                        #   - Docker image for development Postgres database
├── catalog/                                # Primary code directory
│   ├── dags/                               # DAGs & DAG support code
│   │   ├── common/                         #   - Shared modules used across DAGs
│   │   ├── data_refresh/                   #   - DAGs & code related to the data refresh process
│   │   ├── database/                       #   - DAGs related to database actions (matview refresh, cleaning, etc.)
│   │   ├── maintenance/                    #   - DAGs related to airflow/infrastructure maintenance
│   │   ├── oauth2/                         #   - DAGs & code for Oauth2 key management
│   │   ├── providers/                      #   - DAGs & code for provider ingestion
│   │   │   ├── provider_api_scripts/       #       - API access code specific to providers
│   │   │   ├── provider_csv_load_scripts/  #       - Schema initialization SQL definitions for SQL-based providers
│   │   │   └── *.py                        #       - DAG definition files for providers
│   │   └── retired/                        #   - DAGs & code that is no longer needed but might be a useful guide for the future
│   └── templates/                          # Templates for generating new provider code
└── *                                       # Documentation, configuration files, and project requirements
```

## Publishing

The docker image for the catalog (Airflow) is published to
ghcr.io/WordPress/openverse-catalog.

## Contributing

Pull requests are welcome! Feel free to [join us on Slack][wp_slack] and discuss
the project with the engineers and community members on #openverse.

## Additional Resources

- 2022-01-12: **[cc-archive/cccatalog](https://github.com/cc-archive/cccatalog):
  The old repository for this catalog contains useful information for the
  original motivations and architecture of the Catalog.**

For additional context see:

- 2020-12-07:
  [Upcoming Changes to the CC Open Source Community — Creative Commons Open Source](https://opensource.creativecommons.org/blog/entries/2020-12-07-upcoming-changes-to-community/)
- 2021-05-03:
  [CC Search to Join WordPress - Creative Commons](https://creativecommons.org/2021/05/03/cc-search-to-join-wordpress/)
- 2021-05-10:
  [Welcome to Openverse – Openverse — WordPress.org](https://make.wordpress.org/openverse/2021/05/11/hello-world/)
- 2021-12-13:
  [Dear Users of CC Search, Welcome to Openverse - Creative Commons](https://creativecommons.org/2021/12/13/dear-users-of-cc-search-welcome-to-openverse/)

## Acknowledgments

Openverse, previously known as CC Search, was conceived and built at
[Creative Commons](https://creativecommons.org). We thank them for their
commitment to open source and openly licensed content, with particular thanks to
previous team members @ryanmerkley, @janetpkr, @lizadaly, @sebworks, @pa-w,
@kgodey, @annatuma, @mathemancer, @aldenstpage, @brenoferreira, and @sclachar,
along with their
[community of volunteers](https://opensource.creativecommons.org/community/community-team/).

[wp_slack]: https://make.wordpress.org/chat/
[cc]: https://creativecommons.org
[cc_community]: https://opensource.creativecommons.org/community/community-team/
