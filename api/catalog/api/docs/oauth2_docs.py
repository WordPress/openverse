from catalog.api.docs.base_docs import custom_extend_schema
from catalog.api.examples import (
    auth_key_info_200_example,
    auth_key_info_403_example,
    auth_key_info_curl,
    auth_register_201_example,
    auth_register_curl,
)
from catalog.api.serializers.error_serializers import (
    ForbiddenErrorSerializer,
    InputErrorSerializer,
    InternalServerErrorSerializer,
)
from catalog.api.serializers.oauth2_serializers import (
    OAuth2ApplicationSerializer,
    OAuth2KeyInfoSerializer,
    OAuth2RegistrationSerializer,
)


register = custom_extend_schema(
    operation_id="register",
    params=OAuth2RegistrationSerializer,
    res={
        201: (OAuth2ApplicationSerializer, auth_register_201_example),
        400: (InputErrorSerializer, None),
    },
    eg=[auth_register_curl],
)

key_info = custom_extend_schema(
    operation_id="key_info",
    res={
        200: (OAuth2KeyInfoSerializer, auth_key_info_200_example),
        403: (ForbiddenErrorSerializer, auth_key_info_403_example),
        500: (InternalServerErrorSerializer, None),
    },
    eg=[auth_key_info_curl],
)
