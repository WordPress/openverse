"""# OAuth Provider Authorization"""

from datetime import datetime

from airflow.models import DAG
from airflow.operators.python import PythonOperator

import oauth2
from common.constants import DAG_DEFAULT_ARGS


dag = DAG(
    dag_id="oauth2_authorization",
    schedule=None,
    start_date=datetime(2021, 1, 1),
    description="Authorization workflow for all Oauth2 providers.",
    max_active_runs=1,
    catchup=False,
    default_args={
        **DAG_DEFAULT_ARGS,
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
