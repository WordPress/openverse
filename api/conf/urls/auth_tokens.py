from django.urls import include, path

from api.views.oauth2_views import CheckRates, Register, TokenView, VerifyEmail


auth_tokens_urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("verify/<str:code>/", VerifyEmail.as_view(), name="verify-email"),
    path("token/", TokenView.as_view(), name="token"),
    path("", include("oauth2_provider.urls", namespace="oauth2_provider")),
]

urlpatterns = [
    path("auth_tokens/", include(auth_tokens_urlpatterns)),
    path("rate_limit/", CheckRates.as_view(), name="key_info"),
]
