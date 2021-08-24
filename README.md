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

### Daily API Workflows

Workflows that have a `schedule_string='@daily'` parameter are run daily. The DAG 
workflows run `provider_api_scripts` to load and extract media data from the APIs. 
Below are some of the daily DAG workflows that run the corresponding `provider_api_scripts` 
daily:

- [Met Museum Workflow](openverse_catalog/dags/metropolitan_museum_workflow.py)
  ( [API script](openverse_catalog/dags/provider_api_scripts/metropolitan_museum_of_art.py) )
- [PhyloPic Workflow](openverse_catalog/dags/phylopic_workflow.py)
  ( [API script](openverse_catalog/dags/provider_api_scripts/phylopic.py) )
- [Flickr Workflow](openverse_catalog/dags/flickr_workflow.py)
  ( [API script](openverse_catalog/dags/provider_api_scripts/flickr.py) )
- [Wikimedia Commons Workflow](openverse_catalog/dags/wikimedia_workflow.py)
  ( [Commons API script](openverse_catalog/dags/provider_api_scripts/wikimedia_commons.py) )

### Monthly Workflow

Some API ingestion workflows are scheduled to run on the 15th day of each 
month at 16:00 UTC. These workflows are reserved for long-running jobs or
APIs that do not have date filtering capabilities so the data is reprocessed 
monthly to keep the catalog updated. The following tasks are performed monthly:

- [Cleveland Museum of Art](openverse_catalog/dags/provider_api_scripts/cleveland_museum_of_art.py)
- [RawPixel](openverse_catalog/dags/provider_api_scripts/raw_pixel.py)
- [Common Crawl Syncer](openverse_catalog/dags/commoncrawl_scripts/commoncrawl_s3_syncer/SyncImageProviders.py)
- [Brooklyn Museum](openverse_catalog/dags/provider_api_scripts/brooklyn_museum.py)
- [NYPL](openverse_catalog/dags/provider_api_scripts/nypl.py)

### DB_Loader

The Airflow DAG defined in [`loader_workflow.py`][db_loader] runs every minute,
and loads the oldest file which has not been modified in the last 15 minutes
into the upstream database. It includes some data preprocessing steps.

[db_loader]: openverse_catalog/dags/loader_workflow.py

See each provider API script's notes in their respective [handbook][ov-handbook] entry.

[ov-handbook]: https://make.wordpress.org/openverse/handbook/openverse-handbook/

## Development setup for Airflow and API puller scripts

There are a number of scripts in the directory
[`openverse_catalog/dags/provider_api_scripts`][api_scripts] eventually
loaded into a database to be indexed for searching in the Openverse API. These run in a
different environment than the PySpark portion of the project, and so have their
own dependency requirements.

[api_scripts]: openverse_catalog/dags/provider_api_scripts

### Development setup

You'll need `docker` and `docker-compose` installed on your machine, with
versions new enough to use version `3` of Docker Compose `.yml` files.

To set up environment variables, navigate to the
[`openverse_catalog`][cc_airflow] directory, and run

```shell
cp env.template .env
```

If needed, fill in API keys or other secrets and variables in `.env`. This is
not needed if you only want to run the tests. There is a
[`docker-compose.yml`][dockercompose] provided in the
[`openverse_catalog`][cc_airflow] directory, so from that directory, run

```shell
docker-compose up -d
```

This results, among other things, in the following running containers:

- `openverse_catalog_webserver_1`
- `openverse_catalog_postgres_1`

and some networking setup so that they can communicate. Note:

- `openverse_catalog_webserver_1` is running the Apache Airflow daemon, and also
  has a few development tools (e.g., `pytest`) installed.
- `openverse_catalog_postgres_1` is running PostgreSQL, and is setup with some
  databases and tables to emulate the production environment. It also provides a
  database for Airflow to store its running state.
- The directory containing the DAG files, as well as dependencies will be
  mounted to the `usr/local/airflow/dags` directory in the container
  `openverse_catalog_webserver_1`.

At this stage, you can run the tests via:

```shell
docker exec openverse_catalog_webserver_1 /usr/local/airflow/.local/bin/pytest
```

Edits to the source files or tests can be made on your local machine, then tests
can be run in the container via the above command to see the effects.

If you'd like, it's possible to login to the webserver container via

```shell
docker exec -it openverse_catalog_webserver_1 /bin/bash
```

It's also possible to attach to the running command process of the webserver
container via

```shell
docker attach --sig-proxy=false openverse_catalog_webserver_1
```

Attaching in this manner lets you see the output from both the Airflow webserver
and scheduler, which can be useful for debugging purposes. To leave the
container, (but keep it running), press `Ctrl-C` on \*nix platforms

To see the Airflow web UI, point your browser to `localhost:9090`.

If you'd like to bring down the containers, run

```shell
docker-compose down
```

from the [`openverse_catalog`][cc_airflow] directory.

To reset the test DB (wiping out all databases, schemata, and tables), run

```shell
docker-compose down -v
```

[dockercompose]: openverse_catalog/docker-compose.yml
[cc_airflow]: openverse_catalog/

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

## Contributing

Pull requests are welcome! Feel free to [join us on Slack][wp_slack] and discuss the
project with the engineers and community memebers on #openverse.

## Acknowledgments

Openverse, previously known as CC Search, was conceived and built at
[Creative Commons][cc]. We thank them for their commitment to open source and openly
licensed content, with particular thanks to original team members @kgodey, @annatuma,
@mathemancer, @aldenstpage, @brenoferreira, and @sclachar, along with their
[community of volunteers][cc_community].

## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
[wp_slack]: https://make.wordpress.org/chat/
[cc]: https://creativecommons.org
[cc_community]: https://opensource.creativecommons.org/community/community-team/
