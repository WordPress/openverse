This is a temporary repository for the CC Search project while migrating from Automattic to Creative Commons. See all the repositories in the project below:

|Original Repo|Automattic Repo|
|--|--|
[creativecommons/cccatalog-frontend](https://github.com/creativecommons/cccatalog-frontend) | [Automattic/ccsearch-frontend](https://github.com/Automattic/ccsearch-frontend)
[creativecommons/cccatalog](https://github.com/creativecommons/cccatalog) | [Automattic/ccsearch-catalog](https://github.com/Automattic/ccsearch-catalog)
[creativecommons/cccatalog-api](https://github.com/creativecommons/cccatalog-api) | [Automattic/ccsearch-api](https://github.com/Automattic/ccsearch-api)


Repos have been renamed into a `ccsearch-` namespace, for now. All branch names and code has been preserved, with the *following exceptions*:

- GitHub Actions are commented out
- `CODEOWNERS` files and `.cc-metadata.yml` files are deleted

The rest of this README is the unmodified original readme, which may reference documentation on creativecommons.org, opensource.creativecommons.org, or Creative Commons' internal employee wiki. These references will be updated in time.

---

# Creative Commons Catalog
*Mapping the commons towards an open ledger and cc search.*

## Description

This repository contains the methods used to identify over 1.4 billion Creative
Commons licensed works. The challenge is that these works are dispersed
throughout the web and identifying them requires a combination of techniques.
Two approaches are currently explored:

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

CC Catalog uses AWS Data Pipeline service to automatically create an Amazon EMR
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
[ex_cc_links]: src/ExtractCCLinks.py

## API Data

[Apache Airflow](https://airflow.apache.org/) is used to manage the workflow for
various API ETL jobs which pull and process data from a number of open APIs on
the internet.

### Common API Workflows

The Airflow DAGs defined in [`common_api_workflows.py`][api_flows] manage daily
ETL jobs for the following platforms, by running the linked scripts:

- [Met Museum](src/cc_catalog_airflow/dags/provider_api_scripts/metropolitan_museum_of_art.py)
- [PhyloPic](src/cc_catalog_airflow/dags/provider_api_scripts/phylopic.py)
- [Thingiverse](src/cc_catalog_airflow/dags/provider_api_scripts/Thingiverse.py)

[api_flows]: src/cc_catalog_airflow/dags/common_api_workflows.py

### Other Daily API Workflows

Airflow DAGs, defined in their own files, also run the following scripts daily:

- [Flickr](src/cc_catalog_airflow/dags/provider_api_scripts/flickr.py)
- [Wikimedia Commons](src/cc_catalog_airflow/dags/provider_api_scripts/wikimedia_commons.py)

In the future, we'll migrate to the latter style of Airflow DAGs and
accompanying Provider API Scripts.

### Monthly Workflow

The Airflow DAG defined in [`monthlyWorkflow.py`][mon_flow] handles the monthly
jobs that are scheduled to run on the 15th day of each month at 16:00 UTC. This
workflow is reserved for long-running jobs or APIs that do not have date
filtering capabilities so the data is reprocessed monthly to keep the catalog
updated. The following tasks are performed:

- [Cleveland Museum of Art](src/cc_catalog_airflow/dags/provider_api_scripts/ClevelandMuseum.py)
- [RawPixel](src/cc_catalog_airflow/dags/provider_api_scripts/RawPixel.py)
- [Common Crawl Syncer](src/cc_catalog_airflow/dags/commoncrawl_s3_syncer/SyncImageProviders.py)

[mon_flow]: src/cc_catalog_airflow/dags/monthlyWorkflow.py

### DB_Loader

The Airflow DAG defined in [`loader_workflow.py`][db_loader] runs every minute,
and loads the oldest file which has not been modified in the last 15 minutes
into the upstream database. It includes some data preprocessing steps.

[db_loader]: src/cc_catalog_airflow/dags/loader_workflow.py

### Other API Jobs (not in the workflow)

- [Brooklyn Museum](src/cc_catalog_airflow/dags/provider_api_scripts/BrooklynMuseum.py)
- [NYPL](src/cc_catalog_airflow/dags/provider_api_scripts/NYPL.py)
- Cleveland Public Library

## Development setup for Airflow and API puller scripts

There are a number of scripts in the directory
[`src/cc_catalog_airflow/dags/provider_api_scripts`][api_scripts] eventually
loaded into a database to be indexed for searching on CC Search. These run in a
different environment than the PySpark portion of the project, and so have their
own dependency requirements.

[api_scripts]: src/cc_catalog_airflow/dags/provider_api_scripts

### Development setup

You'll need `docker` and `docker-compose` installed on your machine, with
versions new enough to use version `3` of Docker Compose `.yml` files.

To set up environment variables, navigate to the
[`src/cc_catalog_airflow`][cc_airflow] directory, and run
```shell
cp env.template .env
```
If needed, fill in API keys or other secrets and variables in `.env`. This is
not needed if you only want to run the tests. There is a
[`docker-compose.yml`][dockercompose] provided in the
[`src/cc_catalog_airflow`][cc_airflow] directory, so from that directory, run

```shell
docker-compose up -d
```

This results, among other things, in the following running containers:

- `cc_catalog_airflow_webserver_1`
- `cc_catalog_airflow_postgres_1`

and some networking setup so that they can communicate.  Note:
- `cc_catalog_airflow_webserver_1` is running the Apache Airflow daemon, and also
has a few development tools (e.g., `pytest`) installed.
- `cc_catalog_airflow_postgres_1` is running PostgreSQL, and is setup with some
databases and tables to emulate the production environment. It also provides a
database for Airflow to store its running state.
- The directory containing the DAG files, as well as dependencies will be
mounted to the `usr/local/airflow/dags` directory in the container
`cc_catalog_airflow_webserver_1`.

At this stage, you can run the tests via:

```shell
docker exec cc_catalog_airflow_webserver_1 /usr/local/airflow/.local/bin/pytest
```
Edits to the source files or tests can be made on your local machine, then tests
can be run in the container via the above command to see the effects.


If you'd like, it's possible to login to the webserver container via

```shell
docker exec -it cc_catalog_airflow_webserver_1 /bin/bash
```

It's also possible to attach to the running command process of the webserver
container via

```shell
docker attach --sig-proxy=false cc_catalog_airflow_webserver_1
```
Attaching in this manner lets you see the output from both the Airflow webserver
and scheduler, which can be useful for debugging purposes.  To leave the
container, (but keep it running), press `Ctrl-C` on *nix platforms

To see the Airflow web UI, point your browser to `localhost:9090`.

If you'd like to bring down the containers, run
```shell
docker-compose down
```
from the [`src/cc_catalog_airflow`][cc_airflow] directory.

To reset the test DB (wiping out all databases, schemata, and tables), run
```shell
docker-compose down
rm -r /tmp/docker_postgres_data/
```

[dockercompose]: src/cc_catalog_airflow/docker-compose.yml
[cc_airflow]: src/cc_catalog_airflow/

## PySpark development setup

### Prerequisites

```
JDK 9.0.1
Python 3.6
Pytest 4.3.1
Spark 2.2.1
Airflow 1.10.4

pip install -r requirements.txt
```

### Running the tests
```
python -m pytest tests/test_ExtractCCLinks.py
```

## Authors

See the list of [contributors][contrib] who participated in this project.

[contrib]: https://github.com/creativecommons/cccatalog/contributors

## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
