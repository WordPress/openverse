# Creative Commons Catalog
*Mapping the commons towards an open ledger and cc search.*

## Description
This repository contains the methods used to identify over 1.4 billion Creative Commons licensed works. The challenge is that these works are dispersed throughout the web and identifying them requires a combination of techniques. Two approaches are currently explored:
1. [Web crawl data](#web-crawl-data)
2. [Application Programming Interfaces (APIs)](#application-programming-interfaces-apis)

### Web Crawl Data
The Common Crawl Foundation provides an open repository of petabyte-scale web crawl data. A new dataset is published at the end of each month comprising over 200 TiB of uncompressed data. 

The data is available in three formats:
- WARC: the entire raw data, including HTTP response metadata, WARC metadata, etc.
- WET: extracted plaintext from each webpage.
- WAT: extracted html metadata, e.g. HTTP headers and hyperlinks, etc.

CC Catalog uses AWS Data Pipeline service to automatically create an EMR cluster of 100 c4.8xlarge instances that will parse the WAT archives to identify all domains that link to creativecommons.org. Due to the volume of data, Apache Spark is used to streamline the processing. The output of this methodology is a series of parquet files that contain:
- the domains and its respective content path and query string (i.e. the exact webpage that links to creativecommons.org)
- the CC referenced hyperlink (which may indicate a license), 
- HTML meta data in JSON format which indicates the number of images on each webpage and other domains that they reference, 
- the location of the webpage in the WARC file so that the page contents can be found.

The steps above are performed in [ExtractCCLinks.py](https://github.com/creativecommons/cccatalog/blob/master/src/ExtractCCLinks.py)

### Application Programming Interfaces (APIs)
[Apache Airflow](https://airflow.apache.org/) is used to manage the workflow for the various API ETL jobs. There are three workflows: 1) [Daily_ETL_Workflow](https://github.com/creativecommons/cccatalog/blob/master/src/airflow_dag/dailyWorkflow.py), 2) [Monthly_Workflow](https://github.com/creativecommons/cccatalog/blob/master/src/airflow_dag/monthlyWorkflow.py) and 3) [DB_Loader](https://github.com/creativecommons/cccatalog/blob/master/src/airflow_dag/loaderWorkflow.py).

#### Daily_ETL_Workflow
This manages the daily ETL jobs for the following platforms:
- [Flickr](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/Flickr.py)
- [Wikimedia Commons](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/WikimediaCommons.py)
- [Thingiverse](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/Thingiverse.py)
- [Met Museum](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/MetMuseum.py)
- [PhyloPic](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/PhyloPic.py)

#### Monthly_Workflow
Manages the monthly jobs that are scheduled to run on the 15th day of each month at 16:00 UTC. This workflow is reserved for long-running jobs or APIs that do not have date filtering capabilities so the data is reprocessed monthly to keep the catalog updated. The following tasks are performed:
- [Cleveland Museum of Art](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/ClevelandMuseum.py)
- [RawPixel](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/RawPixel.py)
- [Flickr](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/Flickr.py)
- [Common Crawl Syncer](https://github.com/creativecommons/cccatalog/blob/master/src/airflow_dag/commoncrawl_s3_syncer/SyncImageProviders.py)

#### DB_Loader
Scheduled to load data into the upstream database every four hours. It includes data preprocessing steps.

#### Other API Jobs (not in the workflow)
- [Brooklyn Museum](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/BrooklynMuseum.py)
- [NYPL](https://github.com/creativecommons/cccatalog/blob/master/src/providers/api/NYPL.py)
- Cleveland Public Library 

## Getting Started

## PySpark development
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
## Provider API puller module development
There are a number of scripts in the directory `src/providers/api` which pull image data from various restful apis, and format it into files which are eventually loaded into a database to be indexed for searching on CC Search.  These run in a different environment than the PySpark portion of the project, and so have their own dependency requirements.

### Setup the easy way
There is a Dockerfile provided in the `src/providers/api` directory.  With docker installed, navigate to that directory and run
```
docker build -t cccdev -f Dockerfile.localdev .
```
This results in a docker image named `cccdev` with some helpful pieces installed (the right version of python, all dependencies, vim, ipython, and tmux).  To run that image, and sync the directory containing the source files, run
```
docker run -it -v $(pwd):/cccatalog_api_scripts cccdev
```
from the `src/providers/api` directory.  The source files are then available at `/cccatalog_api_scripts` in the running container.  Edits to the source files can be made on your local machine, then tests can be run in the container to see the effects.

### Setup the other way
The advantage of this method is that you don't have to install docker.  You will, however need to install a number of other dependencies, including a specific version of Python.  Furthermore, the tests are unlikely to pass on a windows machine (unless you're using WSL).

1. To begin, install Python 3.7.4, and `pip`.  Use of `virtualenv` is recommended.
1. Navigate to `src/providers/api` and run `pip install -r requirements.txt`.
1. If that succeeds, set the `OUTPUT_DIR` and `FLICKR_API_KEY` variables to whatever you like (they won't be used by the tests), start `python` (3.7.4), and try to import `Flickr`.  

If you make it that far, the tests (for the api provider modules) should pass on your local setup.

### Running the tests

From the `/cccatalog_api_scripts` directory in the docker container, or the `src/providers/api` directory on your local machine, run `pytest`.  (on your local machine, don't forget to set the environment variables mentioned above).

### Running the tests

## Authors
See the list of [contributors](https://github.com/creativecommons/cccatalog/contributors) who participated in this project.

## License
This project is licensed under the MIT license - see the [LICENSE](LICENSE) file for details.
