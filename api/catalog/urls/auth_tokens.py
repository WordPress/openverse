from django.urls import include, path

from catalog.api.views.oauth2_views import Register, TokenView, VerifyEmail


urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("verify/<str:code>/", VerifyEmail.as_view(), name="verify-email"),
    path("token/", TokenView.as_view(), name="token"),
    path("", include("oauth2_provider.urls", namespace="oauth2_provider")),
]
