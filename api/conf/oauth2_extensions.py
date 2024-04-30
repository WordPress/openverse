from rest_framework.exceptions import AuthenticationFailed

from drf_spectacular.authentication import TokenScheme
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication as BaseOAuth2Authentication,
)


class OAuth2Authentication(BaseOAuth2Authentication):
    # Required by schema extension
    keyword = "Bearer"

    def authenticate(self, request):
        result = super().authenticate(request)
        if getattr(request, "oauth2_error", None):
            # oauth2_error is only defined on requests that had errors
            # it will be undefined or empty for anonymous requests and
            # requests with valid credentials
            # `request` is mutated by `super().authenticate`
            raise AuthenticationFailed()

        return result


class OAuth2OpenApiAuthenticationExtension(TokenScheme):
    target_class = "conf.oauth2_extensions.OAuth2Authentication"
    name = "Openverse API Token"
