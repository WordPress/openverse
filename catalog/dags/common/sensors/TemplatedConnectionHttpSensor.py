from airflow.providers.http.sensors.http import HttpSensor


class TemplatedConnectionHttpSensor(HttpSensor):
    """
    Wrapper around the HTTPSensor which allows templating of the conn_id,
    in order to support using a conn_id passed through XCOMs.
    """

    # Extended to allow templating of conn_id
    template_fields = HttpSensor.template_fields + ("http_conn_id",)
