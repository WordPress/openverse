from api.utils.oauth2_helper import get_token_info


def response_headers_middleware(get_response):
    """
    Add standard response headers used by Nginx logging.
    These headers help Openverse more easily and directly connect
    individual requests to each other. This is particularly useful
    when evaluating traffic patterns from individual source IPs
    to identify malicious requesters or request patterns.
    """

    def middleware(request):
        response = get_response(request)

        if hasattr(request, "auth") and request.auth:
            token_info = get_token_info(str(request.auth))
            if token_info:
                response["x-ov-client-application-name"] = token_info.application_name
                response["x-ov-client-application-verified"] = token_info.verified

        return response

    return middleware
