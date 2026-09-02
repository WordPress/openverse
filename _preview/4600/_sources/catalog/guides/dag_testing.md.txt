# Running DAGs locally

[Apache Airflow](https://airflow.apache.org/) is used to manage our workflows
(DAGs) in the catalog. For more information see
[our quickstart guide](/catalog/guides/quickstart.md#api-data). This document
describes how to run or test out these DAGs locally during development.

Additionally, it is worth noting that not all DAGs can be run locally in
development right away as some of them require API keys from the provider.
However, some other DAGs like the ones for SMK or Finnish Museums can be run
locally without any additional keys. In order to run some DAGs locally, you
might need to get the API keys from the provider and add them to the
`catalog/.env` file.

## Getting started

1. Refer to and follow the instructions at [Quickstart](./quickstart.md) to
   setup and make sure the catalog service is up and running. If you have
   successfully completed the general setup then this can be started by running
   `./ov just catalog/up`.

2. Navigate to http://localhost:9090

![Airflow Login Page](/_static/airflow_login.png)

3. You should be met with an authentication page, use `airflow` as both the
   username and password to log in.

![Airflow Home Page](/_static/airflow_home.png)

4. Search for or scroll down to any DAG of choice that does not require an API
   key and click on it. We are using the `finnish_museums_workflow` for this
   example.

![Airflow DAG Index](/_static/dag_index.png)

5. Click the toggle button labelled "DAG" at the top left, an alert box pops up
   for you to confirm the action, click "OK" to continue. A run will get kicked
   off.

   DAGs which are run on a schedule (like this one) will usually kick off
   immediately, though the page may need to be refreshed in order to view the
   run. If you wish to kick off a new DAG run, you should click on the "Trigger
   DAG" button represented by a "play" icon at the top right of the page.

![Airflow DAG Unpaused](/_static/dag_unpaused.png)

6. To get a summary of the DAG, click on the "DAG Docs" accordion and you should
   see an overview of the DAG displayed.

```{note}
For more info about how Airflow works in general, check out their
[documentation on the UI](https://airflow.apache.org/docs/apache-airflow/stable/ui.html).
```
