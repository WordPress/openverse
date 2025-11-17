# Openverse Providers

## Overview

The Openverse Catalog collects data from the APIs of sites that share
openly-licensed media, and saves them in our Catalog database. This process is
automated by
[Airflow DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html)
generated for each provider. A simple provider DAG looks like this:

![Example DAG](/_static/simple_dag.png)

At a high level the steps are:

1. `generate_filename`: Generates the named of a TSV (tab-separated values) text
   file that will be used for saving the data to the disk in later steps
2. `pull_data`: Pulls records from the provider API, collects just the data we
   need, and commits it to local storage in TSVs.
3. `load_data`: Loads the data from TSVs into the Catalog database, updating old
   records and discarding duplicates.
4. `report_load_completion`: Reports a summary of added and updated records.

When a provider supports multiple media types (for example, `audio` _and_
`images`), the `pull` step consumes data of all types, but separate `load` steps
are generated:

![Example Multi-Media DAG](/_static/multi_media_dag.png)

## Adding a New Provider

Adding a new provider to Openverse means adding a new provider DAG. Fortunately,
our DAG factories automate most of this process. To generate a fully functioning
provider DAG, you need to:

1. Implement a `ProviderDataIngester`
2. Add a `ProviderWorkflow` configuration class

### Implementing a `ProviderDataIngester` class

We call the code that pulls data from our provider APIs "Provider API scripts".
You can find examples in
[`provider_api_scripts` folder](https://github.com/WordPress/openverse/tree/main/catalog/dags/providers/provider_api_scripts).
This code will be run during the `pull` steps of the provider DAG.

At a high level, a provider script should iteratively request batches of records
from the provider API, extract data in the format required by Openverse, and
commit it to local storage. Much of this logic is implemented in a
[`ProviderDataIngester` base class](https://github.com/WordPress/openverse/blob/main/catalog/dags/providers/provider_api_scripts/provider_data_ingester.py)
(which also provides additional testing features).

<!-- TODO: link to documentation for testing features like ingestion_limit, skip_ingestion_errors etc-->

To add a new provider, extend this class and implement its abstract methods.

We provide a
[script](https://github.com/WordPress/openverse/blob/main/catalog/templates/create_provider_ingester.py)
that can be used to generate the files you'll need and get you started:

```
# PROVIDER_NAME: The name of the provider
# ENDPOINT: The API endpoint from which to fetch data
# MEDIA: Optionally, a space-delineated list of media types ingested by this provider
#        (and supported by Openverse). If not provided, defaults to "image".

> just catalog/add-provider <PROVIDER_NAME> <ENDPOINT> <MEDIA>

# Example usages:

# Creates a provider that supports just audio
> just catalog/add-provider TestProvider https://test.test/search audio

# Creates a provider that supports images and audio
> just catalog/add-provider "Foobar Museum" https://foobar.museum.org/api/v1 image audio

# Creates a provider that supports the default, just image
> just catalog/add-provider TestProvider https://test.test/search
```

You should see output similar to this:

<!-- Ignore "NOTE" in the codeblock below. It is verbatim output from a script so should not be changed. -->
<!-- vale proselint.Annotations = NO -->

```
Creating files in /Users/staci/projects/openverse-projects/openverse
API script:        openverse/catalog/dags/providers/provider_api_scripts/foobar_museum.py
API script test:   openverse/catalog/tests/dags/providers/provider_api_scripts/test_foobar_museum.py

NOTE: You will also need to add a new ProviderWorkflow dataclass configuration to the PROVIDER_WORKFLOWS list in `openverse-catalog/dags/providers/provider_workflows.py`.
```

<!-- vale proselint.Annotations = YES -->

This generates a provider script with a templated `ProviderDataIngester` for you
in the
[`provider_api_scripts` folder](https://github.com/WordPress/openverse/tree/main/catalog/dags/providers/provider_api_scripts),
as well as a corresponding test file. Complete the TODOs detailed in the
generated files to implement behavior specific to your API.

Some APIs may not fit perfectly into the established `ProviderDataIngester`
pattern. For advanced use cases and examples of how to modify the ingestion
flow, see the
[`ProviderDataIngester` FAQ](https://github.com/WordPress/openverse/blob/main/catalog/docs/provider_data_ingester_faq.md).

### Add a `ProviderWorkflow` configuration class

Now that you have an ingester class, you're ready to wire up a provider DAG in
Airflow to automatically pull data and load it into our Catalog database. This
is done by defining a `ProviderWorkflow` configuration dataclass and adding it
to the `PROVIDER_WORKFLOWS` list in
[`provider_workflows.py`](https://github.com/WordPress/openverse/blob/main/catalog/dags/providers/provider_workflows.py).
Our DAG factories will pick up the configuration and generate a complete new DAG
in Airflow!

At minimum, you'll need to provide the following in your configuration:

- `ingester_class`: the `ProviderDataIngester` class itself

Example:

```python
# In catalog/dags/providers/provider_workflows.py
from providers.provider_api_scripts.foobar_museum import FoobarMuseumDataIngester

...

PROVIDER_WORKFLOWS = [
    ...
    ProviderWorkflow(
        ingester_class=FooBarMuseumDataIngester,
    )
]
```

There are many other options that allow you to tweak the `schedule` (when and
how often your DAG is run), timeouts for individual steps of the DAG, and more.
These are documented in the definition of the `ProviderWorkflow` dataclass.

<!--TODO: add docs for other options.-->

After adding your configuration, run `just up` and you should now have a fully
functioning provider DAG!

<!--TODO: add and link to docs for how to run provider DAGs locally, preferably with images.-->

```{note}
When your code is merged, the DAG will become available in production
but will be disabled by default. A contributor with Airflow access will need to
manually turn the DAG on in production.
```

## Testing guide

### Steps

1. Ensure you've gone through the [quickstart](/catalog/guides/quickstart.md).
   Ensure that the Docker daemon is running.

2. Run individual test by creating a testing session within Docker, then
   selecting only the tests associated with the provider.

   ```console
   $ just catalog/test-session
   $ pytest -k <provider_name>
   ```

   Alternatively, the test selection can be run in Docker directly with:

   ```console
   $ just catalog/test -k <provider_name>
   ```

```{note}
Using `just catalog/test-session` opens Docker to access a shell which is set up to run
tests. This allows one to run tests repeatedly while potentially modifying the code,
without having to start the Docker container up each time the tests need to be run.
Running the tests on Docker directly (e.g. using `just catalog/test`) will spin up the
container, run the selected tests if any are provided (or all by default) and then stop
and remove the container. That can be useful for ensuring that all tests pass if one
does not need to iterate and check the test failures repeatedly.
```
