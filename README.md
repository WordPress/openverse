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

# Creative Commons Catalog API
[![Build Status](https://travis-ci.org/creativecommons/cccatalog-api.svg?branch=master)](https://travis-ci.org/creativecommons/cccatalog-api)
![License](https://img.shields.io/github/license/creativecommons/cccatalog-api.svg?style=flat)
## Purpose

The Creative Commons Catalog API ('cccatalog-api') is a system that allows programmatic access to public domain digital media. It is our ambition to index and catalog [billions of Creative Commons works](https://stateof.creativecommons.org/), including articles, songs, videos, photographs, paintings, and more. Using this API, developers will be able to access the digital commons in their own applications.

This repository is primarily concerned with back end infrastructure like datastores, servers, and APIs. The pipeline that feeds data into this system can be found in the [cccatalog repository](https://github.com/creativecommons/cccatalog). A front end web application that interfaces with the API can be found at the [cccatalog-frontend repository](https://github.com/creativecommons/cccatalog-frontend).

<br/>

## API Documentation

In the [API documentation](https://api.creativecommons.engineering), you can find more details about the endpoints with examples on how to use them.

<br/>

## How to Run the Server Locally

### Prerequisites

You need to install [Docker](https://docs.docker.com/install/) (with [Docker Compose](https://docs.docker.com/compose/install/)), [Git](https://git-scm.com/downloads), and [PostgreSQL client tools](https://www.postgresql.org/download/). On Debian, the package is called `postgresql-client-common`.

<br/>

### How to Do It

1. Run the [Docker daemon](https://docs.docker.com/config/daemon/)

2. Open your command prompt (CMD) or terminal

3. Clone CC Catalog API
```
git clone https://github.com/creativecommons/cccatalog-api.git
```
4. Change directory to CC Catalog API
```
cd cccatalog-api
```
5. Start CC Catalog API locally
```
docker-compose up
```
6. Wait until your CMD or terminal displays that it is starting development server at `http://0.0.0.0:8000/`
<br/>

![Initialization](initialization.PNG)

7. Open up your browser and type `localhost:8000` in the search tab

8. Make sure you see the local API documentation
<br/>

![Local API Documentation](local_api_documentation.PNG)

9. Open a new CMD or terminal and change directory to CC Catalog API

10. Still in the new CMD or terminal, load the sample data
```
./load_sample_data.sh
```

11. Still in the new CMD or terminal, hit the API with a request
```
curl localhost:8000/v1/images?q=honey
```

12. Make sure you see the following response from the API
<br/>

![Sample API_Request](localhost_request.PNG)

Congratulations! You just run the server locally.

<br/>

### What Happens In the Background

After executing `docker-compose up` (in Step 5), you will be running:
+ A Django API server
+ Two PostgreSQL instances (one simulates the upstream data source, the other serves as the application database)
+ Elasticsearch
+ Redis
+ A thumbnail-generating image proxy
+ ingestion-server, a service for bulk ingesting and indexing search data.
+ analytics, a REST API server for collecting search usage data

<br/>

### Diagnosing local Elasticsearch issues
If the API server container failed to start, there's a good chance that Elasticsearch failed to start on your machine. Ensure that you have allocated enough memory to Docker applications, otherwise the container will instantly exit with an error. Also, if the logs mention "insufficient max map count", increase the number of open files allowed on your system. For most Linux machines, you can fix this by adding the following line to `/etc/sysctl.conf`:
```
vm.max_map_count=262144
```
To make this setting take effect, run:
```
sudo sysctl -p
```

<br/>

## System Architecture
![System Architecture](https://raw.githubusercontent.com/creativecommons/cccatalog-api/master/system_architecture.png)

<br/>

### Basic flow of data
Search data is ingested from upstream sources provided by the [data pipeline](https://github.com/creativecommons/cccatalog). As of the time of writing, this includes data from Common Crawl and multiple 3rd party APIs. Once the data has been scraped and cleaned, it is transferred to the upstream database, indicating that it is ready for production use.

Every week, the latest version of the data is automatically bulk copied ("ingested") from the upstream database to the production database by the Ingestion Server. Once the data has been downloaded and indexed inside of the database, the data is indexed in Elasticsearch, at which point the new data can be served up from the CC Catalog API servers.

<br/>

### Description of subprojects
- *cccatalog-api* is a Django Rest Framework API server. For a full description of its capabilities, please see the [browsable documentation](https://api.creativecommons.engineering).
- *ingestion-server* is a service for downloading and indexing search data once it has been prepared by the CC Catalog.
- *analytics* is a Falcon REST API for collecting usage data.

<br/>

## Running the tests

### How to Run API live integration tests
You can check the health of a live deployment of the API by running the live integration tests.

1. Change directory to CC Catalog API
```
cd cccatalog-api
```

2. Install all dependencies for CC Catalog API
```
pipenv install
```

3. Launch a new shell session
```
pipenv shell
```

4. Run API live integration test
```
./test/run_test.sh
```

<br/>

### How to Run Ingestion Server tests
You can ingest and index some dummy data using the Ingestion Server API.

1. Change directory to ingestion server
```
cd ingestion_server
```

2. Install all dependencies for Ingestion Server API
```
pipenv install
```

3. Launch a new shell session
```
pipenv shell
```

4. Run the integration tests
```
python3 test/integration_tests.py
```

<br/>

## Deploying and monitoring the API
The API infrastructure is orchestrated using Terraform hosted in creativecommons/ccsearch-infrastructure. You can find more details on [this wiki page](https://wikijs.creativecommons.org/tech/cc-search/operations).

<br/>

## Django Admin

You can view the custom administration views at the /admin/ endpoint.

<br/>

## Contributing
Pull requests are welcome! Feel free to [join us on Slack](https://slack-signup.creativecommons.org/) and discuss the project with the engineers on #cc-search.

You are welcome to take any open issue in the tracker labeled [`help wanted`](https://github.com/creativecommons/cccatalog-api/labels/help%20wanted) or [`good first issue`](https://github.com/creativecommons/cccatalog-api/labels/good%20first%20issue); **there's no need to ask for permission in advance**. Other issues are open for contribution as well, but may be less accessible or well defined in comparison to those that are explicitly labeled.

See the [CONTRIBUTING](https://github.com/creativecommons/cccatalog-api/blob/master/CONTRIBUTING.md) file for details.
