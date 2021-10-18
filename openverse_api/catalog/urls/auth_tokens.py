from catalog.api.views.oauth2_views import Register, VerifyEmail
from django.urls import include, path


urlpatterns = [
    path("register", Register.as_view(), name="register"),
    path("verify/<str:code>", VerifyEmail.as_view(), name="verify-email"),
    path("", include("oauth2_provider.urls", namespace="oauth2_provider")),
]
