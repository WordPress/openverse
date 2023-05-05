from django.urls import path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("", SpectacularRedocView.as_view(url_name="schema"), name="root"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
]
