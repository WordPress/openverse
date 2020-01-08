# Creative Commons Catalog
*Mapping the commons towards an open ledger and cc search.*

## Description

This repository contains the methods used to identify over 1.4 billion Creative
Commons licensed works. The challenge is that these works are dispersed
throughout the web and identifying them requires a combination of techniques.
Two approaches are currently explored:

1. [Web crawl data](#web-crawl-data)
2. [Application Programming Interfaces (APIs)](#application-programming-interfaces-apis)

## Web Crawl Data

The Common Crawl Foundation provides an open repository of petabyte-scale web
crawl data. A new dataset is published at the end of each month comprising over
200 TiB of uncompressed data.

The data is available in three formats:

- WARC: the entire raw data, including HTTP response metadata, WARC metadata, etc.
- WET: extracted plaintext from each webpage.
- WAT: extracted html metadata, e.g. HTTP headers and hyperlinks, etc.

CC Catalog uses AWS Data Pipeline service to automatically create an EMR cluster
of 100 c4.8xlarge instances that will parse the WAT archives to identify all
domains that link to creativecommons.org. Due to the volume of data, Apache
Spark is used to streamline the processing. The output of this methodology is a
series of parquet files that contain:

- the domains and its respective content path and query string (i.e. the exact
  webpage that links to creativecommons.org)
- the CC referenced hyperlink (which may indicate a license), 
- HTML meta data in JSON format which indicates the number of images on each
  webpage and other domains that they reference,
- the location of the webpage in the WARC file so that the page contents can be
  found.

The steps above are performed in
[ExtractCCLinks.py](https://github.com/creativecommons/cccatalog/blob/master/src/ExtractCCLinks.py)

## API Data

[Apache Airflow](https://airflow.apache.org/) is used to manage the workflow for
various API ETL jobs which pull and process data from a number of open APIs on
the internet.

### [Common API Workflows](src/cc_catalog_airflow/dags/common_api_workflows.py)

The Airflow DAGs defined in
[`common_api_workflows.py`](src/cc_catalog_airflow/dags/common_api_workflows.py)
manage the daily ETL jobs for the following platforms:

- [Flickr](src/cc_catalog_airflow/dags/provider_api_scripts/Flickr.py)
- [Met Museum](src/cc_catalog_airflow/dags/provider_api_scripts/MetMuseum.py)
- [PhyloPic](src/cc_catalog_airflow/dags/provider_api_scripts/PhyloPic.py)
- [Thingiverse](src/cc_catalog_airflow/dags/provider_api_scripts/Thingiverse.py)
- [Wikimedia Commons](src/cc_catalog_airflow/dags/provider_api_scripts/WikimediaCommons.py)

### [Monthly_Workflow](src/cc_catalog_airflow/dags/monthlyWorkflow.py)

The Airflow DAG defined in
[`monthlyWorkflow.py`](src/cc_catalog_airflow/monthlyWorkflow.py)

the monthly jobs that are scheduled to run on the 15th day of each month
at 16:00 UTC. This workflow is reserved for long-running jobs or APIs that do
not have date filtering capabilities so the data is reprocessed monthly to keep
the catalog updated. The following tasks are performed:

- [Cleveland Museum of Art](src/cc_catalog_airflow/dags/provider_api_scripts/ClevelandMuseum.py)
- [RawPixel](src/cc_catalog_airflow/dags/provider_api_scripts/RawPixel.py)
- [Flickr](src/cc_catalog_airflow/dags/provider_api_scripts/Flickr.py)
- [Common Crawl Syncer](src/cc_catalog_airflow/dags/commoncrawl_s3_syncer/SyncImageProviders.py)

### [DB_Loader](src/cc_catalog_airflow/dags/loaderWorkflow.py)

Scheduled to load data into the upstream database every four hours. It includes
data preprocessing steps.

### Other API Jobs (not in the workflow)

- [Brooklyn Museum](src/cc_catalog_airflow/dags/provider_api_scripts/BrooklynMuseum.py)
- [NYPL](src/cc_catalog_airflow/dags/provider_api_scripts/NYPL.py)
- Cleveland Public Library 

## Development setup for Airflow and API puller scripts

There are a number of scripts in the directory
[`src/cc_catalog_airflow/dags/provider_api_scripts`](src/cc_catalog_airflow/dags/provider_api_scripts)
eventually loaded into a database to be indexed for searching on CC Search.
These run in a different environment than the PySpark portion of the project,
and so have their own dependency requirements.

### Setup the Docker way

The advantage of this method is that it recreates the same environment for your
testing as is on production.

There is a [Dockerfile](src/cc_catalog_airflow/Dockerfile) provided in the
`src/cc_catalog_airflow` directory. With docker installed, navigate to that directory
and run

```
docker build -t cc-catalog-etl  .
```

This results in a docker image named `cc-catalog-etl` with some helpful pieces installed
(the right version of python, all dependencies, pytest). To run that image, and
sync the directory containing the source files, run

```
docker run -d -p 8080:8080 -v $(pwd)/dags:/usr/local/airflow/dags --name cc-catalog-etl-ws  cc-catalog-etl webserver
```

from the `src/cc_catalog_airflow` directory (i.e., the one containing the
Dockerfile). This results in a Docker container running the airflow webserver,
and syncs the directory containing all dags, as well as dependencies to the
`usr/local/airflow/dags` directory in the container (named `cc-catalog-etl-ws`).
To run the tests, run the following commands from the `src/cc_catalog_airflow`
directory:

1. `docker cp env.sh.template cc-catalog-etl-ws:/usr/local/airflow/env.sh`
1. `docker exec -it cc-catalog-etl-ws /bin/bash`

You should now have a bash prompt in the running container. From the airflow
home directory (i.e., the one you should have been automatically placed into
upon login), run the following commands:

1. `source env.sh`
1. `pytest`

Edits to the source files or tests can be made on your local machine, then tests
can be run in the container to see the effects.

### Setup the other way
The advantage of this method is that you don't have to install docker. You will,
however need to install a number of other dependencies, including a specific
version of Python. Furthermore, the tests are unlikely to pass on a windows
machine (unless you're using WSL). To begin with, install Python 3.7, and `pip`.
Use of `virtualenv` is recommended. Then, run the following commands in sequence
from the `src/cc_catalog_airflow` directory (with your `venv` activated, should
you use it):

1. `pip install -r requirements.txt`
1. `cp env.sh.template env.sh`
1. `echo "export AIRFLOW_HOME=${PWD}" >> env.sh`
1. `source env.sh`
1. `pytest`

## PySpark development setup

### Prerequesites

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
See the list of
[contributors](https://github.com/creativecommons/cccatalog/contributors) who
participated in this project.

## License
This project is licensed under the MIT license - see the [LICENSE](LICENSE) file
for details.
