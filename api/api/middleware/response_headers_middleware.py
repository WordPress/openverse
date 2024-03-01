from rest_framework.request import Request

from api.models.oauth import ThrottledApplication


def response_headers_middleware(get_response):
    """
    Add standard response headers used by Nginx logging.

    These headers help Openverse more easily and directly connect
    individual requests to each other. This is particularly useful
    when evaluating traffic patterns from individual source IPs
    to identify malicious requesters or request patterns.
    """

    def middleware(request: Request):
        response = get_response(request)

        if not (hasattr(request, "auth") and hasattr(request.auth, "application")):
            return response

        application: ThrottledApplication = request.auth.application
        response["x-ov-client-application-name"] = application.name
        response["x-ov-client-application-verified"] = application.verified

        return response

    return middleware
