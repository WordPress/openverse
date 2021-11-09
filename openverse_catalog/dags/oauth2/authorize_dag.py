"""
# OAuth Provider Authorization

**Author**: Madison Swain-Bowden

**Created**: 2021-10-13

"""
from datetime import datetime

import oauth2
from airflow.models import DAG
from airflow.operators.python import PythonOperator


dag = DAG(
    dag_id="oauth2_authorization",
    schedule_interval=None,
    description="Authorization workflow for all Oauth2 providers.",
    max_active_runs=1,
    catchup=False,
    default_args={
        "owner": "data-eng-admin",
        "depends_on_past": False,
        "start_date": datetime(2021, 1, 1),
        "email_on_retry": False,
        "retries": 0,
    },
    tags=["oauth"],
)

_current_providers = [
    f"- {provider.name.title()}\n" for provider in oauth2.OAUTH_PROVIDERS
]

dag.doc_md = (
    __doc__
    + f"""

Iterates through all the OAuth2 providers and attempts to authorize them using tokens
found in the in the `{oauth2.OAUTH2_AUTH_KEY}` Variable. Once authorization has been
completed successfully, the auth token is removed from that Variable. The authorization
will create an access/refresh token pair in the `{oauth2.OAUTH2_TOKEN_KEY}` Variable.

**Current Providers**:

{"".join(_current_providers)}
"""
)


with dag:
    PythonOperator(
        task_id="authorize_providers",
        python_callable=oauth2.authorize_providers,
        op_kwargs={"providers": oauth2.OAUTH_PROVIDERS},
    )
