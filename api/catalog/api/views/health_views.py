from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheck(APIView):
    """
    Returns a "200 OK" response if the server is running normally.

    This endpoint is used in production to ensure that the server should receive
    traffic. If no response is provided, the server is deregistered from the
    load balancer and destroyed.
    """

    swagger_schema = None

    def get(self, request, format=None):
        return Response({"status": "200 OK"}, status=200)
