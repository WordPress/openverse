from airflow.providers.http.operators.http import HttpOperator


class TemplatedConnectionHttpOperator(HttpOperator):
    """
    Wrapper around the HTTPOperator which allows templating of the conn_id,
    in order to support using a conn_id passed through XCOMs.
    """

    # Extended to allow templating of conn_id
    template_fields = HttpOperator.template_fields + ("http_conn_id",)
