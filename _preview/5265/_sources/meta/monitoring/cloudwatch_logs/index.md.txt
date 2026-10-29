# Log querying

Openverse uses
[AWS CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SearchDataFilterPattern.html)
for log storage, log querying, and service monitoring. This document aims to
give readers a baseline knowledge of our logging setup in particular, with the
following explicit questions answered:

- Where do I find logs for a given application?
- How do I query all the logs for a given application for a given period of
  time?
- How do I use CloudWatch Logs Insights to query structured and unstructured
  logs for statistical data?

The primary use case for the information in this document is incident
investigation. The audience of this document is Openverse core maintainers and
as such necessarily assumes access to the Openverse AWS Console and other core
infrastructure. As of writing, **Openverse does not rely on Logs Insights for
metric generation**. Work is planned to leverage Prometheus, Grafana, and other
tools for long term metrics monitoring[^monitoring-ip].

[^monitoring-ip]:
    An
    [old implementation plan exists for this](/projects/proposals/monitoring/20220307-project_proposal.md)
    but was only half implemented. For now, we will continue to leverage
    CloudWatch to the best of our ability.

```{note}
This documentation only applies to the Openverse Django API, the ingestion server,
and the Nuxt frontend. Openverse's catalog (Airflow) does not send logs to CloudWatch.
To find logs for Airflow DAG runs, you need to look in Airflow itself, which manages
logs all on its own.
```

## Terms

[Please see CloudWatch's own glossary first as it contains critical terms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogsConcepts.html)
that are referenced in this document but not listed in this section to avoid
duplication.

- "CloudWatch": AWS's name for a group of services used to monitor applications.
  This includes logging as well as other tools that are not covered in this
  document.
- "Logs Insights": A tool for querying logs using a SQL-like syntax that is
  capable of building charts and graphs and parsing unstructured log data
  on-the-fly
- "Structured logs": Logs in a structured, machine-readable format, like JSON;
  cf "unstructured logs"
- "Unstructured logs": Logs in an unstructured format, like raw stack traces; cf
  "structured logs"

## External documentation links

This document aims to give an overview of how to access and get started with
Openverse's CloudWatch configuration. It does not and should not document
CloudWatch itself. The following links have been helpful for folks who've
learned about CloudWatch in the past. Once you are familiar with finding logs
for specific applications and the basic Openverse-specific features of our
integration, AWS's own documentation will be the best place to look for help
actually using CloudWatch.

- [CloudWatch logs documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
- [CloudWatch Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html),
  used for Logs Insights queries
- [Searching log streams](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SearchDataFilterPattern.html)

CloudWatch's documentation is "decent", but you will likely still need to fiddle
and experiment until you find an approach that works for you. There is plenty of
advice online as well if you get stuck trying to query in a specific way.

## Where to find logs

There are two entry points for CloudWatch logs:

- [Log groups](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)
- [Logs Insights](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights)

### Log groups

Each Openverse application has its own log group that includes the application
name and the environment. For example, the `/ecs/production/api` log group
houses all the log streams for every Django API task's logs. Within the group,
each application instance has its own log streams. For ECS these correspond to
the tasks running in the service. For EC2, these correspond to the EC2 instance.
In both cases, the log streams include the identifier for the task or instance.
For ECS, the streams have the following pattern:

```
ecs/<container name>/<task id>
```

For EC2, the log stream name is simply the instance identifier. Notably, the
ingestion server has separate log groups for the workers and the coordinator.

To query logs for a specific ECS task or EC2 instance, query its corresponding
log stream.

To query the logs for an entire application over a given time period, ignore the
task IDs entirely, and simply query the full log group. This is especially
useful if you know that an event happened within a particular period of time but
do not know the task or EC2 instance identifier and therefore which specific log
stream to query. Because the ingestion server splits its logs in two separate
groups, **it is not possible to query all logs for the ingestion server in a
single query.** You will need to separately query both the ingestion server and
work log groups for the environment.

To query all logs for a log group, go to the log group page and click the orange
"Search log group" button in the upper right-hand corner.

![Search log group button in CloudWatch](/meta/monitoring/cloudwatch_logs/search_log_group.png)

It is not possible to query specific ECS container log streams via the log
groups UI. For example, if you want to query only the Django container logs for
the API log group, you will not be able to narrow your query to exclude the
nginx log streams explicitly. Instead, structure your query such that it will
only match log events from the Django application (or vice-versa).

### Logs Insights

Logs Insights is a powerful tool for querying our logs. It is particular useful
for deriving numerical and statistical data from both structured and
unstructured logs, though the latter require additional parsing. Logs Insights
has its own SQL-like query syntax,
[the documentation for which](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
should be the read before attempting to use Logs Insights for anything serious.

The Logs Insights tutorials present sufficient examples for different types of
queries that you may need to do. A good tip is to think of the Logs Insights
query as a multi-step extract, transform, and load/aggregate tool. First,
extract the specific log events that concern you. If you're querying to find the
average ES query time logged in a particular format, first narrow the log
streams down to just the service sending those logs. Next, use `parse` to
extract the relevant information from the unstructured logs. Finally, use
`stats` to aggregate the data and find the statistical information relevant to
you. The following are two simple examples that can serve as starting points for
querying structured and unstructured log data in Logs Insights for our
application.

```{caution}
Please note that logs insights queries are **not free**.
[See the advice below on how to minimise costs](#logs-insights-queries-are-not-free).
```

**Query for number of failed thumbnail requests per media type in the query
period (parse unstructured logs)**:

```
# Filter down to only the django log streams (excluding nginx)
# Filter to events that include "Failed Dependency"
filter @logStream like 'ecs/django' and @message like 'Failed Dependency'

# Extract the media type and UUID from the message
| parse "/v1/*/*/thumb/" as mediaType, uuid

# Aggregate the data to count
| stats count_distinct(uuid) by mediaType as mediaTypeCount
```

**Query for the average timing of an API endpoint (leverage structured logs)**:

```
# Filter down to only the nginx log streams (excluding django)
# Filter down to requests with "search" in the URL (stored in `request` field)
filter @logStream like 'ecs/nginx' and request like "search"

# Calculate the average request time for every 10 minute period within the query period
| stats avg(request_time) by bin(10m) as averageSearchTime
```

In this example, `request` and `request_time` come directly from the structured
JSON logs that our API Nginx container outputs. You can find the list of
available fields in the
[Nginx configuration](https://github.com//WordPress/openverse/blob/HEAD/api/nginx.conf.template#L10-L24).

You will also find additional real-world queries in Openverse's incident
investigation reports to use as examples for building your own queries.

## Things to keep in mind

### Line-by-line splitting

Unstructured logs are split line-by-line. Because of the way the API currently
outputs stack traces, for example, this means that stack traces will be split
across multiple lines. Take the following, real stack trace:

```
2023-06-04T00:32:12.485Z	2023-06-04 00:32:12,485 ERROR tasks.py:220 - Error processing task `CREATE_AND_POPULATE_FILTERED_INDEX` for `audio`: BadRequestError(400, 'search_phase_execution_exception', 'too_many_clauses: maxClauseCount is set to 1024')
2023-06-04T00:32:12.539Z	Process Process-5:
2023-06-04T00:32:12.541Z	Traceback (most recent call last):
2023-06-04T00:32:12.541Z	File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
2023-06-04T00:32:12.541Z	self.run()
2023-06-04T00:32:12.541Z	File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
2023-06-04T00:32:12.541Z	self._target(*self._args, **self._kwargs)
2023-06-04T00:32:12.541Z	File "/ingestion_server/ingestion_server/tasks.py", line 217, in perform_task
2023-06-04T00:32:12.541Z	func(model, **kwargs) # Directly invoke indexer methods if no task function
2023-06-04T00:32:12.541Z	^^^^^^^^^^^^^^^^^^^^^
2023-06-04T00:32:12.541Z	File "/ingestion_server/ingestion_server/indexer.py", line 525, in create_and_populate_filtered_index
2023-06-04T00:32:12.541Z	self.es.reindex(
2023-06-04T00:32:12.541Z	File "/venv/lib/python3.11/site-packages/elasticsearch/client/utils.py", line 347, in _wrapped
2023-06-04T00:32:12.541Z	return func(*args, params=params, headers=headers, **kwargs)
2023-06-04T00:32:12.541Z	^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2023-06-04T00:32:12.541Z	File "/venv/lib/python3.11/site-packages/elasticsearch/client/__init__.py", line 1467, in reindex
2023-06-04T00:32:12.541Z	return self.transport.perform_request(
2023-06-04T00:32:12.541Z	^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2023-06-04T00:32:12.541Z	File "/venv/lib/python3.11/site-packages/elasticsearch/transport.py", line 466, in perform_request
2023-06-04T00:32:12.541Z	raise e
2023-06-04T00:32:12.541Z	File "/venv/lib/python3.11/site-packages/elasticsearch/transport.py", line 427, in perform_request
2023-06-04T00:32:12.541Z	status, headers_response, data = connection.perform_request(
2023-06-04T00:32:12.541Z	^^^^^^^^^^^^^^^^^^^^^^^^^^^
2023-06-04T00:32:12.541Z	File "/venv/lib/python3.11/site-packages/elasticsearch/connection/http_requests.py", line 216, in perform_request
2023-06-04T00:32:12.541Z	self._raise_error(response.status_code, raw_data)
2023-06-04T00:32:12.541Z	File "/venv/lib/python3.11/site-packages/elasticsearch/connection/base.py", line 328, in _raise_error
2023-06-04T00:32:12.541Z	raise HTTP_EXCEPTIONS.get(status_code, TransportError)(
2023-06-04T00:32:12.541Z	elasticsearch.exceptions.BadRequestError: BadRequestError(400, 'search_phase_execution_exception', 'too_many_clauses: maxClauseCount is set to 1024')
```

Each line (prepended with a timestamp), is a separate log event. The implication
of this is that if you're querying for a particular phrase that appears in a
stack trace, you will only get the exact line of the stack trace with the phrase
you queried for.

This will be fixed generally for our Python applications, but still keep this in
mind if you find logs that appear to be incomplete. It may be that the event
parsing configuration needs tweaking to account for certain edge cases. Please
open an issue if you notice this.

### Logs Insights queries are not free

Logs Insights queries parse logs on-the-fly (more or less) and cost money each
time they are executed. You can minimise costs in the following ways:

- Scope queries to as specific a period of time as possible. If you are
  investigating an incident with a known beginning and end, narrow the query to
  that time period via the date range selector at the top. If there are multiple
  periods with lulls in between, consider performing multiple queries and
  aggregating them manually outside Logs Insights.
- Develop queries against the minimum required number. While you're still
  building a query to find specific data, narrow the time range or use `limit`
  to reduce the number of log lines processed during each iteration. Avoid
  searching the full relevant data set until you're confident that the query
  works and extracts the data you expect.
- When trying to find examples of specific logs, use `limit` with a low number.
  If you just need one example, use `limit 1`. If you need multiple, try to keep
  the number low, for example, less than 25. This is especially useful when
  developing `parse` statements.

### Logs are not retained forever

Each log group has a retention policy and none of them are forever. You can see
the retention period for each log group
[on the log groups listing page under the "retention" heading of the table](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups).
