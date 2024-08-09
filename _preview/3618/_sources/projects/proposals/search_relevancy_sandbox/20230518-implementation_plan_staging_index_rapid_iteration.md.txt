# 2023-05-18 Implementation Plan: Rapid iteration of ingestion server index configuration

**Author**: @aetherunbound

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @sarayourfriend
- [x] @stacimc
- [x] @krysal

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/392)
- [Project Proposal](https://github.com/WordPress/openverse/issues/392)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This document describes a DAG (and associated dependencies) which can be used to
generate a new index in Elasticsearch without requiring a data refresh,
ingestion server deployment, or any interaction with the ingestion server.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

Once the implementation is complete, a maintainer should be able to run this DAG
to create a new index on either elasticsearch environment with an altered
configuration. The maintainer should only need to specify the pieces of the
configuration that are different from the default configuration, although they
can supply a full configuration if they wish. The DAG will report when it is
complete and what the name of the new index is.

## Dependencies

The following are prerequisites for the DAG:

- Installation of the
  [`elasticsearch` Airflow provider package](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/)
- Airflow Connections for each Elasticsearch cluster

### Elasticsearch provider

The
[`elasticsearch` provider](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/)
will need to be added to the list of dependencies for our catalog Docker image.
This will be done first and deployed on its own, as the connections will be
needed for the rest of the work.

In order to add this provider, the
[production requirements](https://github.com/WordPress/openverse/blob/3fcce5ade2165955db5bbcb4f679257b3260547b/catalog/requirements_prod.txt#L5)
will need to be changed from `apache-airflow[amazon,postgres,http]` to
`apache-airflow[amazon,postgres,http,elasticsearch]`.

### Airflow connections

Once the provider is installed,
[Airflow Connections](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/connections/elasticsearch.html)
will need to be created for each Elasticsearch cluster. The connections will be
named `elasticsearch_production` and `elasticsearch_staging` and reference each
respective environment. These will be created by hand in the Airflow UI. For
local development, defaults will be added to the
[`env.template` file](https://github.com/WordPress/openverse/blob/3fcce5ade2165955db5bbcb4f679257b3260547b/catalog/env.template).

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

No infrastructure changes should be necessary for this implementation, beyond
the addition of the `elasticsearch` provider package and the Airflow connections
described above.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

This work does not depend on any other projects and can be implemented at any
time. In order to be utilized however, a query parameter on the API will need to
be used for determining which index to query. This has been implemented in
#2073.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

Once the prerequisites above have been filled, the DAGs can be created. The DAGs
will be named `create_new_es_index_{environment}`, and will have the parameters
and steps described below. A dynamic DAG generation function will be used to
create one DAG per environment (`staging` and `production`). It will have a
schedule of `None` so that it is only run when triggered. It should also have
`max_active_runs` set to `1` so that only one instance of the DAG can be running
at a time.

### Parameters

1. `media_type`: The media type for which the index is being created. Presently
   this would only be `image` or `audio`.
2. `index_config`: A JSON object containing the configuration for the new index.
   The values in this object will be merged with the existing configuration,
   where the value specified at a leaf key in the object will override the
   existing value (see [Merging policy](#merging-policy) below). This can also
   be the entire index configuration, in which case the existing configuration
   will be replaced entirely (see `override_config` parameter below).
3. `index_suffix`: (Optional) The name suffix of the new index to create. This
   will be a string, and will be used to name the index in Elasticsearch of the
   form `{media_type}-{index_suffix}`. If not provided, the suffix will be a
   timestamp of the form `YYYYMMDDHHMMSS`.
4. `source_index`: (Optional) The existing index on Elasticsearch to use as the
   basis for the new index. If not provided, the index aliased to `media_type`
   will be used (e.g. `image` for the `image` media type). In production, the
   data refresh process creates the index and aliases it to the media type. In
   staging, the process for creating the indices which can be iterated on here
   will be defined in a follow-up IP, #1987.
5. `override_config`: (Optional) A boolean value which can be toggled to replace
   the existing index configuration entirely with the new configuration. If
   `True`, the `index_config` parameter will be used as the entire
   configuration. If `False`, the `index_config` parameter will be merged with
   the existing configuration. Defaults to `False`.
6. `query`: (Optional) An
   [Elasticsearch query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
   to use to filter the documents to be copied to the new index. If not
   provided, all documents will be copied. See
   [the reindex API endpoint for the request body](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/docs-reindex.html#docs-reindex-api-request-body)
   and
   [`create_and_populate_filtered_index` on the ingestion server](https://github.com/WordPress/openverse/blob/3fcce5ade2165955db5bbcb4f679257b3260547b/ingestion_server/ingestion_server/indexer.py#L529)
   for an example of how this is used.

### DAG

Once the parameters are provided, the DAG will execute the following steps:

1. (For `production` only) Check that there are no other reindexing jobs
   currently underway. This can be done by checking whether the
   `{media_type}_data_refresh` and `create_filtered_{media_type}_index` DAGs are
   currently running. If either of them are, this DAG should fail immediately
   with an appropriate error message. **Note**: We will also need to add the
   `create_new_es_index_production` DAG to the checks prior to running the data
   refresh (where `create_filtered_{media_type}_index` is currently checked) in
   the `image_data_refresh` and `audio_data_refresh` DAGs. This will prevent the
   data refresh from running concurrently while the new index is being created.
2. Create the index configuration. If `override_config` is supplied, the
   `index_config` parameter will be used as the entire configuration. If not,
   the `index_config` parameter will be merged with the existing index settings.
   See [Merging policy](#merging-policy) for how this merge will be performed.
   Below are the steps for gathering the current index settings:
   1. Get the current index information. This will be done using the
      [`ElasticsearchPythonHook`](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/_api/airflow/providers/elasticsearch/hooks/elasticsearch/index.html#airflow.providers.elasticsearch.hooks.elasticsearch.ElasticsearchPythonHook),
      specifically the
      [`indices.get` function](https://elasticsearch-py.readthedocs.io/en/v8.8.0/api.html#elasticsearch.client.IndicesClient.get).
   2. Extract the relevant settings from the response. They come back in a form
      that differs from what is required by the
      [`indices.create`](https://elasticsearch-py.readthedocs.io/en/v8.8.0/api.html#elasticsearch.client.IndicesClient.create)
      function of the Elasticsearch Python API. The `indices.get` function
      returns data of the form:
      ```json
      {
        "<index-name>": {
          "settings": {
            "index": {
              "number_of_shards": "18",
              "number_of_replicas": 0,
              "refresh_interval": "-1",
              ...
              "analysis": {
                ...
              }
            }
          },
          "mappings": {...}
        }
      }
      ```
      However, the `indices.create` function expects data of the form:
      ```json
      {
        "settings": {
          "index": {
            "number_of_shards": 18,
            "number_of_replicas": 0,
            "refresh_interval": "-1"
          },
          "analysis": {...},
        },
        "mapping": {...}
      }
      ```
      Specifically note that the returned `settings.index.analysis`
      configuration section needs to be moved to `settings.analysis` instead,
      and that most of the other index settings (besides those denoted
      explicitly here, e.g. `number_of_shards`, `number_of_replicas`, and
      `refresh_interval`) can be discarded. The returned information will need
      to be extracted and converted into the form expected by `indices.create`
      before it is merged with the new configuration.
3. Create the new index with the configuration generated in step 1 using the
   `ElasticsearchPythonHook`'s
   [`indices.create`](https://elasticsearch-py.readthedocs.io/en/v8.8.0/api.html#elasticsearch.client.IndicesClient.create)
   function. The index name will either be a combination of the `media_type` and
   `index_suffix` parameters (`{media_type}-{index_suffix}`, e.g.
   `image-my-special-suffix`), or the `media_type` and a timestamp
   (`{media_type}-{timestamp}`, e.g. `image-20200102030405`).
   ([example from the existing ingestion server code](https://github.com/WordPress/openverse/blob/3fcce5ade2165955db5bbcb4f679257b3260547b/ingestion_server/ingestion_server/indexer.py#L518-L521)).
4. Initiate a reindex using the `source_index` as the source and the
   [`reindex`](https://elasticsearch-py.readthedocs.io/en/v8.8.0/api.html#elasticsearch.Elasticsearch.reindex)
   function of the Elasticsearch Python API
   ([example from the ingestion server](https://github.com/WordPress/openverse/blob/3fcce5ade2165955db5bbcb4f679257b3260547b/ingestion_server/ingestion_server/indexer.py#L525-L547)).
   Rather than setting `wait_for_completion=True` on the ES Python API reindex
   call and having this step halt until the reindex is complete, this step will
   set `wait_for_completion=False` and continue to the next step. The
   [task ID returned from Elasticsearch for the reindex operation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-reindex.html#docs-reindex-task-api)
   will be stored in an XCom variable. This step will have `refresh=True` on the
   function call to ensure the reindex will immediately refresh after completion
   to make the data available to searches. It will also need `slices='auto'` so
   the indexing is parallelized.
5. Use a sensor and the previously emitted task ID to wait for the reindex to
   complete. This will check the task using the
   [Task API](https://www.elastic.co/guide/en/elasticsearch/reference/current/tasks.html).
   This could be done either using a subsequent `wait_for_completion` call
   within a simple `PythonSensor` using the Elasticsearch hook with a low
   timeout which is polled repeatedly, or by using the `status` value of the
   response to determine if polling should continue. Elasticsearch documentation
   notes that
   [`status` may not always be available](https://www.elastic.co/guide/en/elasticsearch/reference/current/tasks.html#_get_more_information_about_tasks),
   so we'd need to determine if the reindex task returns a `status` field first.
6. Once the reindex & refresh are complete, report that the new index is ready
   via Slack. This message should include both the index name and the
   Elasticsearch environment.

#### Merging policy

The configuration should be merged such that the leaf key overwrites the entire
value present in the default configuration at that key. For example, if the
default configuration is:

```json
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 1
    }
  }
}
```

An override value of `{"settings": {"index": {"number_of_shards": 2}}}` will
overwrite the `number_of_shards` value, but leave the `number_of_replicas` value
unchanged. The resulting configuration will be:

```json
{
  "settings": {
    "index": {
      "number_of_shards": 2,
      "number_of_replicas": 1
    }
  }
}
```

This will be a naive merge, and list values will not be appended automatically.
For instance:

```json
{
  "analysis": {
    "filter": {
      "stem_overrides": {
        "type": "stemmer_override",
        "rules": [
          "animals => animal",
          "animal => animal",
          "anime => anime",
          "animate => animate",
          "animated => animate",
          "universe => universe"
        ]
      }
    }
  }
}
```

with an override of

```json
{
  "analysis": {
    "filter": {
      "stem_overrides": {
        "rules": ["crim => cribble"]
      }
    }
  }
}
```

will result in

```json
{
  "analysis": {
    "filter": {
      "stem_overrides": {
        "type": "stemmer_override",
        "rules": ["crim => cribble"]
      }
    }
  }
}
```

The [`jsonmerge` Python library](https://pypi.org/project/jsonmerge/) provides a
good example of the naive approach, although we will want to avoid adding an
extra dependency for this step is possible.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

### Using the ingestion server

The first idea for this approach was to use the ingestion server directly, and
alter the `es_mappings.py` file either dynamically or in a mechanism similar to
[the dag-sync script on the catalog](https://docs.openverse.org/projects/proposals/search_relevancy_sandbox/20230331-project_proposal_search_relevancy_sandbox.html#required-implementation-plans).
This might have been made easier by a move of this service from EC2 to ECS. This
approach was abandoned when @sarayourfriend suggested
[interacting with Elasticsearch directly](https://github.com/WordPress/openverse/pull/1107#discussion_r1155399508).

## Design

<!-- Note any design requirements for this plan. -->

No new design work is required for this plan.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

The addition of the Elasticsearch provider is a blocker for the rest of the work
described here; all work must be done serially.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

There are no external blockers to this project.

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

No API version changes should be necessary.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

No accessibility concerns are expected.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Rollback would likely involve deleting the DAG. The provider dependency and
Elasticsearch connections are likely to be useful in the future, so it may
behoove us to keep them even if the DAG is deleted.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

This approach does allow for maintainers to affect production resources, so the
same care should be taken when triggering this DAG as with triggering a
deployment. The described DAG will only ever create new indices, and so there is
no risk losing or affecting the production indices. The DAG will also fail if
any other DAGs which perform a reindex are running, which will prevent
saturating Elasticsearch resources in production.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [Discussion about the approach on the original project proposal](https://github.-com/WordPress/openverse/pull/1107#discussion_r1155399508)
- [`jsonmerge` Python package](https://pypi.org/project/jsonmerge/)
- [Elasticsearch reindex API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-reindex.html)
- [Airflow Elasticsearch Provider](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/)
- [`create_and_populate_filtered_index` Pull Request](https://github.com/WordPress/openverse/pull/1202)
