# Creative Commons Catalog API
[![Build Status](https://travis-ci.org/creativecommons/cccatalog-api.svg?branch=master)](https://travis-ci.org/creativecommons/cccatalog-api)
![License](https://img.shields.io/github/license/creativecommons/cccatalog-api.svg?style=flat)
## Purpose

The Creative Commons Catalog API ('cccatalog-api') is a system that allows programmatic access to public domain digital media. It is our ambition to index and catalog [billions of Creative Commons works](https://stateof.creativecommons.org/), including articles, songs, videos, photographs, paintings, and more. Using this API, developers will be able to access the digital commons in their own applications.

This repository is primarily concerned with back end infrastructure like datastores, servers, and APIs. The pipeline that feeds data into this system can be found in the [cccatalog repository](https://github.com/creativecommons/cccatalog). A front end web application that interfaces with the API can be found at the [cccatalog-frontend repository](https://github.com/creativecommons/cccatalog-frontend).

## API Documentation

Browsable API documentation can be found [here](https://api.creativecommons.engineering).

## Running the server locally

Ensure that you have installed [Docker](https://docs.docker.com/install/) (with [Docker Compose](https://docs.docker.com/compose/install/)) and that the [Docker daemon is running](https://docs.docker.com/config/daemon/).
```
git clone https://github.com/creativecommons/cccatalog-api.git
cd cccatalog-api
docker-compose up
```

After executing `docker-compose up`, you will be running:
* A Django API server
* Two PostgreSQL instances (one simulates the upstream data source, the other serves as the application database)
* Elasticsearch
* Redis
* A thumbnail-generating image proxy
* `ingestion-server`, a service for bulk ingesting and indexing search data.
* `analytics`, a REST API server for collecting search usage data

Once everything has initialized, with `docker-compose` still running in the background, load the sample data. You will need to install PostgreSQL client tools to perform this step. On Debian, the package is called `postgresql-client-common`.

```
./load_sample_data.sh
```

You are now ready to start sending the API server requests. Hit the API with a request to make sure it is working:
`curl localhost:8000/v1/images?q=honey`

### Diagnosing local Elasticsearch issues
If the API server container failed to start, there's a good chance that Elasticsearch failed to start on your machine. Ensure that you have allocated enough memory to Docker applications, otherwise the container will instantly exit with an error. Also, if the logs mention "insufficient max map count", increase the number of open files allowed on your system. For most Linux machines, you can fix this by adding the following line to `/etc/sysctl.conf`:
```
vm.max_map_count=262144
```
To make this setting take effect, run:
```
sudo sysctl -p
```

## System Architecture
![System Architecture](https://raw.githubusercontent.com/creativecommons/cccatalog-api/master/system_architecture.png)

### Basic flow of data
Search data is ingested from upstream sources provided by the [data pipeline](https://github.com/creativecommons/cccatalog). As of the time of writing, this includes data from Common Crawl and multiple 3rd party APIs. Once the data has been scraped and cleaned, it is transferred to the upstream database, indicating that it is ready for production use.

Every week, the latest version of the data is automatically bulk copied ("ingested") from the upstream database to the production database by the Ingestion Server. Once the data has been downloaded and indexed inside of the database, the data is indexed in Elasticsearch, at which point the new data can be served up from the CC Catalog API servers.

### Description of subprojects
- *cccatalog-api* is a Django Rest Framework API server. For a full description of its capabilities, please see the [browsable documentation](https://api.creativecommons.engineering).
- *ingestion-server* is a service for downloading and indexing search data once it has been prepared by the CC Catalog.
- *analytics* is a Falcon REST API for collecting usage data.

## Running the tests

### Running API live integration tests
You can check the health of a live deployment of the API by running the live integration tests.
```
cd cccatalog-api
pipenv install
pipenv shell
./test/run_test.sh
```

### Running Ingestion Server test
This end-to-end test ingests and indexes some dummy data using the Ingestion Server API.

```
cd ingestion_server
pipenv install
pipenv shell
python3 test/integration_tests.py
```

## Deploying and monitoring the API
The API infrastructure is orchestrated using Terraform hosted in creativecommons/ccsearch-infrastructure. More details can be found on the [this wiki page](https://wikijs.creativecommons.org/tech/cc-search/operations).

## Django Admin

Custom administration views can be viewed at the /admin/ endpoint.

## Contributing
Pull requests are welcome! Feel free to [join us on Slack](https://slack-signup.creativecommons.org/) and discuss the project with the engineers on #cc-search. You are welcome to take any open issue in the tracker labeled 'help wanted' or 'good first issue'; **there's no need to ask for permission in advance**. See the [CONTRIBUTORS](https://github.com/creativecommons/cccatalog-api/blob/master/CONTRIBUTING.md) file for details. Other issues are open for contribution as well, but may be less accessible or well defined in comparison to those that are explicitly labeled.
