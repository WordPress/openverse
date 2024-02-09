# ProviderDataIngester FAQ

The most straightforward implementation of a `ProviderDataIngester` repeats the
following process:

- Builds a set of query params for the next request, based upon the previous
  params (for example, by updating offsets or page numbers)
- Makes a single GET request to the configured static `endpoint` using the built
  params
- Extracts a "batch" of records from the response, as a list of record JSON
  representations
- Iterates over the records in the batch, extracting desired data, and commits
  them to local storage

Some provider APIs may not fit neatly into this workflow. This document
addresses some common use cases.

## How do I process a provider "record" that contains data about multiple records?

**Example**: You're pulling data from a Museum database, and each "record" in a
batch contains multiple photos of a single physical object.

**Solution**: The `get_record_data` method takes a `data` object representing a
single record from the provider API. Typically, it extracts required data and
returns it as a single dict. However, it can also return a **list of
dictionaries** for cases like the one described, where multiple Openverse
records can be extracted.

```python
def get_record_data(self, data: dict) -> dict | list[dict] | None:
    records = []

    for record in data.get("associatedImages", []):
        # Perform data processing for each record and add it to a list
        records.append({
            "foreign_landing_url": record.get("foreign_landing_url")
            ...
        })

    return records
```

## What if I can't get all the necessary information for a record from a single API request?

**Example**: A provider's `search` endpoint returns a list of image records
containing _most_ of the information we need for each record, but not image
dimensions. This information _is_ available via the API by hitting a `details`
endpoint for a given image, though.

**Solution**: In this case, you can reuse the `get_response_json` method by
passing in the endpoint you need:

```python
def get_record_data(self, data: dict) -> dict | list[dict] | None:
    ...

    # Get data from the details endpoint
    response_json = self.get_response_json(
        query_params={"my_params": "foo"},
        endpoint=f"https://foobar.museum.org/api/v1/images/{data.get("uuid")}"
    )

    ...
```

> **Note**
>
> When doing this, keep in mind that adding too many requests may slow down
> ingestion. Be aware of rate limits from your provider API as well.

## What if my API endpoint isn't static and needs to change from one request to another?

**Example**: Rather than passing a `page` number in query parameters, a provider
expects the `page` as part of the endpoint path itself.

**Solution**: If your `endpoint` needs to change, you can implement it as a
`property`:

```python
@property
def endpoint(self) -> str:
    # Compute the endpoint using some instance variable
    return f"https://foobar.museum.org/images/page/{self.page_number}"
```

In this example, `self.page_number` is an instance variable that gets updated
after each request. To set up the instance variable you can override `__init__`,
**being careful to remember to call `super` and pass through kwargs**, and then
update it in `get_next_query_params`:

```python
def __init__(self, *args, **kwargs):
    # REQUIRED!
    super().__init__(*args, **kwargs)

    # Set up our instance variable
    self.page_number = None

def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
    # Remember that `get_next_query_params` is called before every request, even
    # the first one.

    if self.page_number is None:
        # Set initial value
        self.page_number = 0
    else:
        # Increment value on subsequent requests
        self.page_number += 1

    # Return your actual query params
    return {}
```

Now each time `get_batch` is called, the `endpoint` is correctly updated.

## How do I run ingestion for a set of discrete categories?

**Example**: My provider has some set of categories that I'd like to iterate
over and ingest data for. E.g., a particular audio provider's search endpoint
requires you specify whether you're searching for "podcasts", "music", etc. I'd
like to iterate over all the available categories and run ingestion for each.

**Solution**: You can do this by overriding the `ingest_records` method, which
accepts optional `kwargs` that it passes through on each call to
`get_next_query_params`. This is best demonstrated with code:

```python
CATEGORIES = ["music", "audio_book", "podcast"]

def ingest_records(self, **kwargs):
    # Iterate over categories and call the main ingestion function, passing in
    # our category as a kwarg
    for category in CATEGORIES:
        super().ingest_records(category=category)

def get_next_query_params(self, prev_query_params, **kwargs):
    # Our category param will be available here
    category = kwargs.get("category")

    # Add it to your query params
    return {
        "category": category,
        ...
    }
```

This will result in the ingestion function running once for each category.

## What if I need to do more complex processing to get a batch?

**Example**: A single GET request is insufficient to get a batch from a
provider. Instead, several requests need to be made in sequence until a
"batchcomplete" token is encountered.

**Solution**: You can override `get_response_json` in order to implement more
complex behavior.

```python
# Pseudo code serves as an example
def get_response_json(
    self, query_params: dict, endpoint: str | None = None, **kwargs
):
    batch_json = None

    while True:
        partial_response = super().get_response_json(query_params)
        batch_json = self.merge_data(batch_json, partial_response)

        if "batchcomplete" in response_json:
            break

    return batch_json
```
