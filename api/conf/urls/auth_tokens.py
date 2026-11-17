from django.urls import include, path

from oauth2_provider import urls as oauth2_urls

from api.views.oauth2_views import CheckRates, Register, TokenView, VerifyEmail


# Mount only the route groups the toolkit had before 3.4. Its default
# ``urlpatterns`` also publish RFC 8414/9728 metadata documents that advertise
# grant types this API does not support, and Dynamic Client Registration routes.
oauth2_provider_urlpatterns = (
    oauth2_urls.base_urlpatterns
    + oauth2_urls.management_urlpatterns
    + oauth2_urls.oidc_urlpatterns
)

auth_tokens_urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("verify/<str:code>/", VerifyEmail.as_view(), name="verify-email"),
    path("token/", TokenView.as_view(), name="token"),
    path(
        "",
        include(
            (oauth2_provider_urlpatterns, oauth2_urls.app_name),
            namespace="oauth2_provider",
        ),
    ),
]

urlpatterns = [
    path("auth_tokens/", include(auth_tokens_urlpatterns)),
    path("rate_limit/", CheckRates.as_view(), name="key_info"),
]
