from rest_framework.exceptions import (
    AuthenticationFailed,
    PermissionDenied,
)

from drf_spectacular.authentication import TokenScheme
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication as BaseOAuth2Authentication,
)


class OAuth2Authentication(BaseOAuth2Authentication):
    # Required by schema extension
    keyword = "Bearer"

    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)
        if getattr(request, "oauth2_error", None):
            # oauth2_error is only defined on requests that had errors
            # it will be undefined or empty for anonymous requests and
            # requests with valid credentials
            # `request` is mutated by `super().authenticate`
            raise AuthenticationFailed()

        # if this is an authed request, check and
        # deny access if client's access has been
        # revoked.
        if user_auth_tuple is not None:
            user, auth = user_auth_tuple
            if application := getattr(auth, "application", None):
                if application.revoked:
                    raise PermissionDenied()

        return user_auth_tuple


class OAuth2OpenApiAuthenticationExtension(TokenScheme):
    target_class = "conf.oauth2_extensions.OAuth2Authentication"
    name = "Openverse API Token"
