"""# OAuth Provider Token Refresh"""

from datetime import datetime

from airflow.models import DAG
from airflow.operators.python import PythonOperator

import oauth2
from common.constants import DAG_DEFAULT_ARGS


dag = DAG(
    dag_id="oauth2_token_refresh",
    schedule="0 */12 * * *",
    start_date=datetime(2021, 1, 1),
    description="Refresh tokens for all Oauth2 providers",
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

Iterates through all OAuth2 providers and attempts to refresh the access token using
the refresh token stored in the `{oauth2.OAUTH2_TOKEN_KEY}` Variable. This DAG will
update the tokens stored in the Variable upon successful refresh.

**Current Providers**:

{"".join(_current_providers)}
"""
)


with dag:
    for provider in oauth2.OAUTH_PROVIDERS:
        PythonOperator(
            task_id=f"refresh__{provider.name}",
            python_callable=oauth2.refresh,
            op_kwargs={"provider": provider},
        )
