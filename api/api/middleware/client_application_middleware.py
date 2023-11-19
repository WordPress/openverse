from api.utils.oauth2_helper import get_token_info


def client_application_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        if hasattr(request, "auth") and request.auth:
            token_info = get_token_info(str(request.auth))
            if token_info:
                response["x-ov-client-application-name"] = token_info.application_name
                response["x-ov-client-application-verified"] = token_info.verified

        return response

    return middleware
