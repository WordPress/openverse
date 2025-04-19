"""
URL configuration for the Openverse API.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from api.views.health_views import HealthCheck
from conf.urls.auth_tokens import urlpatterns as auth_tokens_urlpatterns
from conf.urls.deprecations import urlpatterns as deprecations_urlpatterns


versioned_paths = [
    path("", include("open_api.urls")),  # OpenAPI
    path("", include(auth_tokens_urlpatterns)),  # Authentication endpoints
    path("", include(deprecations_urlpatterns)),  # Deprecated, redirects to new URL
    path("", include("api.urls")),  # API endpoints
]

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="root")),
    path("admin/", admin.site.urls),
    path("healthcheck/", HealthCheck.as_view(), name="health"),
    path("v1/", include(versioned_paths)),
] + [
    path(
        f"{file}",
        TemplateView.as_view(
            template_name=file,
            content_type="text/plain",
        ),
    )
    for file in ["robots.txt", "ai.txt"]
]
