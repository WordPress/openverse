# CC Search Analytics

## Purpose

The `analytics` server collects information about anonymous usage of CC Search.
We intend to use this information to generate statistics about the quality of
search results; the API may be extended in the future to produce usage data
reports.

To minimize risks to privacy, data is only connected to an anonymous session
UUID, which changes every time that a user visits CC Search. No other
identifying information is collected for analytical purposes. We intend to
consume this raw data to produce aggregated reports, after which the raw
data (along with session UUIDs) will be promptly deleted.

## Running the server

The analytics server is automatically started by `docker-compose` in the parent
directory. Before analytics endpoints can be called, the database needs to
be set up with `../load_sample_data.sh`.

To run the `analytics` container by itself:

```
cd ../
docker-compose up db analytics
# Set up the database.
cd analytics
alembic upgrade head
```

## Generating new database migrations

After updating `models.py`, you will need to produce new database migrations.

`alembic revision --autogenerate -m "A message concisely explaining the purpose of your new migration`

## Running the tests

```
pipenv install
pipenv run pytest tests.py
```

## Documentation

After starting the server, you can view the documentation by visiting the
root path (e.g. localhost:8090/). You may have to tweak `docs/redoc.html` for
this to work on your local machine.

Alternatively, you can view the production version of the documentation at
`https://api.openverse.engineering/analytics`.

## Contributing / Code Structure

Pull requests are welcome. Please make sure to update the unit tests and
OpenAPI documentation (`docs/swagger.yaml`) where appropriate.

`analytics` uses a model-view-controller pattern. It is intended to be simple
and idiomatic Python. You shouldn't need to know much else besides that to get
started.

Key technologies to familiarize yourself with include:

- [Falcon](https://falcon.readthedocs.io/en/stable/), a backend API web framework.
- [SQLAlchemy](https://www.sqlalchemy.org/), a database ORM.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/), a lightweight database migration tool for SQLAlchemy.
- [pipenv](https://docs.pipenv.org/en/latest/) for packaging.
- [Docker](https://www.docker.com/) for containerization.
- [OpenAPI](https://www.openapis.org/) (AKA Swagger) for human and machine readable documentation.
