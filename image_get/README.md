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
cd worker
pipenv install
pipenv shell
PYTHONPATH=. pytest
```
Use `pytest -s` to include debug logs.

## How do I feed images to it?
See `dummy_producer.py` for an example.

If you are running `docker-compose`, you must run the producer from within 
the docker-compose network. Enter the worker container and run it from
there.
```
docker exec -it image_get_worker_1 /bin/bash
pipenv run python dummy_producer.py
```

### Current message format
The consumer expects a JSON message with the following structure:
```
{
    'url': 'https://example.gov/example.jpg',
    'uuid': '7563efd4-58d0-41eb-9a4f-3903d36a5225'
}
```

*url*: The URL of the image
*uuid*: Our unique identifier for an image.
