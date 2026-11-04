from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils.throttle import ExemptOAuth2IdRateThrottle, HealthcheckAnonRateThrottle


class HealthCheckException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class HealthCheck(APIView):
    """
    Return a "200 OK" response if the server is running normally, 503 otherwise.

    This endpoint is used in production to ensure that the server should receive
    traffic. If no response is provided, the server is deregistered from the
    load balancer and destroyed.

    The database and Elasticsearch checks are opt-in (``check_db`` and
    ``check_es`` query parameters). The load balancer calls this endpoint
    without them: the DB check needs a pooled connection, so whenever slow
    requests exhausted the pool the check timed out too and the task was
    killed, which only moved the load onto the remaining tasks. A task that
    cannot reach the database never finishes booting anyway, because
    migrations run on startup.
    """

    throttle_classes = [HealthcheckAnonRateThrottle, ExemptOAuth2IdRateThrottle]
    schema = None  # Hide this view from the OpenAPI schema.

    @staticmethod
    def _check_db() -> None:
        """
        Check that the database is available.

        Returns nothing if everything is OK, throws error otherwise.
        """
        try:
            connection.ensure_connection()
        except OperationalError as err:
            raise HealthCheckException(f"postgres: {err}")

    @staticmethod
    def _check_es() -> None:
        """
        Check Elasticsearch cluster health.

        Raises an exception if ES is not healthy.
        """
        es_health = settings.ES.cluster.health(timeout="5s")

        if es_health["timed_out"]:
            raise HealthCheckException("elasticsearch: es_timed_out")

        if (es_status := es_health["status"]) != "green":
            raise HealthCheckException(f"elasticsearch: es_status_{es_status}")

    def get(self, request: Request):
        if "check_es" in request.query_params:
            self._check_es()
        if "check_db" in request.query_params:
            self._check_db()

        return Response({"status": "200 OK"}, status=200)
