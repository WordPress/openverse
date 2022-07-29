<img src="https://github.com/WordPress/openverse/raw/main/brand/banner.svg" width="100%"/>

<p align="center">
  <a href="https://github.com/orgs/WordPress/projects/3">Project Board</a> | <a href="https://make.wordpress.org/openverse/">Community Site</a> | <a href="https://make.wordpress.org/chat/">#openverse @ Slack</a> | <a href="https://make.wordpress.org/openverse/handbook/openverse-handbook/">Handbook</a> | <a href="https://www.figma.com/file/w60dl1XPUvSaRncv1Utmnb/Openverse-Releases">Figma Mockups</a>  | <a href="https://www.figma.com/file/GIIQ4sDbaToCfFQyKMvzr8/Openverse-Design-Library">Figma Design Library</a>
</p>

# Openverse Catalog

This repository contains the methods used to identify over 1.4 billion Creative
Commons licensed works. The challenge is that these works are dispersed
throughout the web and identifying them requires a combination of techniques.

Two approaches are currently in use:

1. Web crawl data
2. Application Programming Interfaces (API Data)

## Web Crawl Data

The Common Crawl Foundation provides an open repository of petabyte-scale web
crawl data. A new dataset is published at the end of each month comprising over
200 TiB of uncompressed data.

The data is available in three file formats:

- WARC (Web ARChive): the entire raw data, including HTTP response metadata,
  WARC metadata, etc.
- WET: extracted plaintext from each webpage.
- WAT: extracted html metadata, e.g. HTTP headers and hyperlinks, etc.

For more information about these formats, please see the
[Common Crawl documentation][ccrawl_doc].

Openverse Catalog uses AWS Data Pipeline service to automatically create an Amazon EMR
cluster of 100 c4.8xlarge instances that will parse the WAT archives to identify
all domains that link to creativecommons.org. Due to the volume of data, Apache
Spark is used to streamline the processing. The output of this methodology is a
series of parquet files that contain:

- the domains and its respective content path and query string (i.e. the exact
  webpage that links to creativecommons.org)
- the CC referenced hyperlink (which may indicate a license),
- HTML meta data in JSON format which indicates the number of images on each
  webpage and other domains that they reference,
- the location of the webpage in the WARC file so that the page contents can be
  found.

The steps above are performed in [`ExtractCCLinks.py`][ex_cc_links].

[ccrawl_doc]: https://commoncrawl.org/the-data/get-started/
[ex_cc_links]: archive/ExtractCCLinks.py

## API Data

[Apache Airflow](https://airflow.apache.org/) is used to manage the workflow for
various API ETL jobs which pull and process data from a number of open APIs on
the internet.

### API Workflows

Our API-based workflows run at different schedules: some daily, others monthly. Please consider which to use whenever a new DAG is written, and add your new script to one of these schedules.

#### Daily

Workflows that have a `schedule_string='@daily'` parameter are run daily. The DAG
workflows run `provider_api_scripts` to load and extract media data from the APIs. The following provider scripts are run daily:

- [Flickr](openverse_catalog/dags/providers/provider_api_scripts/flickr.py)
- [Met Museum](openverse_catalog/dags/providers/provider_api_scripts/metropolitan_museum_of_art.py)
- [PhyloPic](openverse_catalog/dags/providers/provider_api_scripts/phylopic.py)
- [Wikimedia Commons](openverse_catalog/dags/providers/provider_api_scripts/wikimedia_commons.py)

#### Monthly

Some API ingestion workflows are scheduled to run on the 15th day of each
month at 16:00 UTC. These workflows are reserved for long-running jobs or
APIs that do not have date filtering capabilities, so the data is reprocessed
monthly to keep the catalog updated. The following provider scripts are run monthly:

- [Brooklyn Museum](openverse_catalog/dags/providers/provider_api_scripts/brooklyn_museum.py)
- [Cleveland Museum of Art](openverse_catalog/dags/providers/provider_api_scripts/cleveland_museum_of_art.py)
- [Common Crawl Syncer](openverse_catalog/dags/commoncrawl/commoncrawl_scripts/commoncrawl_s3_syncer/SyncImageProviders.py)
- [NYPL](openverse_catalog/dags/providers/provider_api_scripts/nypl.py)
- [RawPixel](openverse_catalog/dags/providers/provider_api_scripts/raw_pixel.py)
- [StockSnap](openverse_catalog/dags/providers/provider_api_scripts/stocksnap.py)

### TSV to Postgres Loader

The Airflow DAG defined in [`loader_workflow.py`][db_loader] runs every minute,
and loads the oldest file which has not been modified in the last 15 minutes
into the upstream database. It includes some data preprocessing steps.

[db_loader]: openverse_catalog/dags/database/loader_workflow.py

See each provider API script's notes in their respective [handbook][ov-handbook] entry.

[ov-handbook]: https://make.wordpress.org/openverse/handbook/openverse-handbook/

## Development setup for Airflow and API puller scripts

There are a number of scripts in the directory
[`openverse_catalog/dags/provider_api_scripts`][api_scripts] eventually
loaded into a database to be indexed for searching in the Openverse API. These run in a
different environment than the PySpark portion of the project, and so have their
own dependency requirements.

For instructions geared specifically towards production deployments, see [DEPLOY.md](DEPLOY.md).

[api_scripts]: openverse_catalog/dags/providers/provider_api_scripts

### Requirements

You'll need `docker` and `docker-compose` installed on your machine, with
versions new enough to use version `3` of Docker Compose `.yml` files.

You will also need the [`just`](https://github.com/casey/just#installation) command runner installed.

### Setup

To set up the local python environment along with the pre-commit hook, run:

```shell
python3 -m venv venv
source venv/bin/activate
just install
```

The containers will be built when starting the stack up for the first time.
If you'd like to build them prior to that, run:

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
2. API Keys - set these if you intend to test one of the provider APIs referenced
3. Connection/Variable info - this will not likely need to be modified for local development, though the values will need to be changed in production
4. Other config - misc. configuration settings, some of which are useful for local dev

The `.env` file does not need to be modified if you only want to run the tests.

### Running & Testing

There is a [`docker-compose.yml`][dockercompose] provided in the
[`openverse_catalog`][cc_airflow] directory, so from that directory, run

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
- The directory containing all modules files (including DAGs, dependencies, and other
  tooling) will be mounted to the directory `/usr/local/airflow/openverse_catalog`
  in the container `openverse_catalog_webserver_1`. On production, only the DAGs folder
  will be mounted, e.g. `/usr/local/airflow/openverse_catalog/dags`.

The various services can be accessed using these links:

- Airflow: `localhost:9090` (The default username and password are both `airflow`.)
- Minio Console: `localhost:5011` (The default username and password are `test_key` and `test_secret`)
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

If you just need to run an airflow command, you can use the `airflow` recipe. Arguments passed to airflow must be quoted:

```shell
just airflow "config list"
```

To follow the logs of the running container:

```shell
just logs
```

To begin an interactive [`pgcli` shell](https://www.pgcli.com/) on the database container, run:

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

`docker volume prune` can also be useful if you've already stopped the running containers, but be warned that it will remove all volumes associated with stopped containers, not just openverse-catalog ones.

To fully recreate everything from the ground up, you can use:

```shell
just recreate
```

[justfile]: justfile
[dockercompose]: docker-compose.yml
[cc_airflow]: openverse_catalog/

## Directory Structure

```text
openverse-catalog
├── .github/                                # Templates for GitHub
├── archive/                                # Files related to the previous CommonCrawl parsing implementation
├── docker/                                 # Dockerfiles and supporting files
│   ├── airflow/                            #   - Docker image for Airflow server and workers
│   └── local_postgres/                     #   - Docker image for development Postgres database
├── openverse_catalog/                      # Primary code directory
│   ├── dags/                               # DAGs & DAG support code
│   │   ├── common/                         #   - Shared modules used across DAGs
│   │   ├── commoncrawl/                    #   - DAGs & scripts for commoncrawl parsing
│   │   ├── database/                       #   - DAGs related to database actions (matview refresh, cleaning, etc.)
│   │   ├── maintenance/                    #   - DAGs related to airflow/infrastructure maintenance
│   │   ├── oauth2/                         #   - DAGs & code for Oauth2 key management
│   │   ├── providers/                      #   - DAGs & code for provider ingestion
│   │   │   ├── provider_api_scripts/       #       - API access code specific to providers
│   │   │   └── *.py                        #       - DAG definition files for providers
│   │   └── retired/                        #   - DAGs & code that is no longer needed but might be a useful guide for the future
│   └── templates/                          # Templates for generating new provider code
└── *                                       # Documentation, configuration files, and project requirements
```

## Publishing

The docker image for the catalog (Airflow) is published to ghcr.io/WordPress/openverse-catalog.

## Contributing

Pull requests are welcome! Feel free to [join us on Slack][wp_slack] and discuss the
project with the engineers and community memebers on #openverse.

## Acknowledgments

Openverse, previously known as CC Search, was conceived and built at [Creative Commons](https://creativecommons.org). We thank them for their commitment to open source and openly licensed content, with particular thanks to previous team members @ryanmerkley, @janetpkr, @lizadaly, @sebworks, @pa-w, @kgodey, @annatuma, @mathemancer, @aldenstpage, @brenoferreira, and @sclachar, along with their [community of volunteers](https://opensource.creativecommons.org/community/community-team/).

## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
[wp_slack]: https://make.wordpress.org/chat/
[cc]: https://creativecommons.org
[cc_community]: https://opensource.creativecommons.org/community/community-team/
