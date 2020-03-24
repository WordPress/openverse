## What is this?

A distributed solution for retrieving images from a list of URLs fed to a 
message queue. Async workers consume messages from this queue and 
store the images at the configured resolution.

Performance is horizontally scalable; workers can be run in any number of 
processes on any number of machines. Be sure to adjust the Kafka topic partition
count to at least the total number of worker processes across all machines.

## How do I start it?
`docker-compose up --build`

## How do I run the tests?
```
pipenv install
pipenv shell
pytest
```
Use `pytest -s` to include logs.

## How do I feed images to it?
See `dummy_producer.py` for an example.

If you are running `docker-compose`, you must run the producer from within 
the docker-compose network. Enter the worker container and run it from
there.
```
sudo docker exec -it image_get_worker_1 /bin/bash
pipenv run python dummy_producer.py
```
