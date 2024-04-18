from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
    ValidationError,
)

from api.docs.base_docs import custom_extend_schema
from api.examples import (
    auth_key_info_200_example,
    auth_key_info_curl,
    auth_register_201_example,
    auth_register_curl,
    auth_token_200_example,
    auth_token_curl,
)
from api.serializers.oauth2_serializers import (
    OAuth2ApplicationSerializer,
    OAuth2KeyInfoSerializer,
    OAuth2RegistrationSerializer,
    OAuth2TokenRequestSerializer,
    OAuth2TokenSerializer,
)


register = custom_extend_schema(
    operation_id="register",
    request=OAuth2RegistrationSerializer,
    res={
        201: (OAuth2ApplicationSerializer, auth_register_201_example),
        400: (ValidationError, None),
        401: ({"type": "object", "properties": {"error": {"type": "string"}}}, None),
        429: (
            APIException("Request was throttled. Expected available in 1 second.", 429),
            None,
        ),
    },
    eg=[auth_register_curl],
)

key_info = custom_extend_schema(
    operation_id="key_info",
    res={
        200: (OAuth2KeyInfoSerializer, auth_key_info_200_example),
        401: (NotAuthenticated, None),
        429: (
            APIException("Request was throttled. Expected available in 1 second.", 429),
            None,
        ),
        500: (APIException, None),
    },
    eg=[auth_key_info_curl],
)

token = custom_extend_schema(
    operation_id="token",
    request={"application/x-www-form-urlencoded": OAuth2TokenRequestSerializer},
    res={
        200: (OAuth2TokenSerializer, auth_token_200_example),
        400: (APIException("Invalid credentials", 400), None),
    },
    eg=[auth_token_curl],
)
