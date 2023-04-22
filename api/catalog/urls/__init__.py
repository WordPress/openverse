"""
This is the Openverse API URL configuration.

The `urlpatterns` list routes URLs to views. For more information please refer
to the [documentation](https://docs.djangoproject.com/en/2.0/topics/http/urls/).
"""

from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from rest_framework.routers import SimpleRouter

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from catalog.api.utils.status_code_view import get_status_code_view
from catalog.api.views.audio_views import AudioViewSet
from catalog.api.views.health_views import HealthCheck
from catalog.api.views.image_views import ImageViewSet
from catalog.api.views.oauth2_views import CheckRates
from catalog.urls.auth_tokens import urlpatterns as auth_tokens_patterns


discontinuation_message = {
    "error": "Gone",
    "reason": "This API endpoint has been discontinued.",
}

versioned_paths = [
    path("", SpectacularRedocView.as_view(url_name="schema"), name="root"),
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path("rate_limit/", CheckRates.as_view(), name="key_info"),
    path("auth_tokens/", include(auth_tokens_patterns)),
    # Deprecated, redirects to new URL
    path(
        "sources",
        RedirectView.as_view(pattern_name="image-stats", permanent=True),
        name="about-image",
    ),
    path(
        "recommendations/images/<str:identifier>",
        RedirectView.as_view(pattern_name="image-related", permanent=True),
        name="related-images",
    ),
    path(
        "oembed",
        RedirectView.as_view(
            pattern_name="image-oembed", query_string=True, permanent=True
        ),
        name="oembed",
    ),
    path(
        "thumbs/<str:identifier>",
        RedirectView.as_view(pattern_name="image-thumb", permanent=True),
        name="thumbs",
    ),
    # Discontinued, return 410 Gone
    re_path(
        r"^link/",
        get_status_code_view(discontinuation_message, 410).as_view(),
        name="make-link",
    ),
]

router = SimpleRouter()
router.register("audio", AudioViewSet, basename="audio")
router.register("images", ImageViewSet, basename="image")
versioned_paths += router.urls

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="root")),
    path("admin/", admin.site.urls),
    path("healthcheck/", HealthCheck.as_view()),
    # API
    path("v1/", include(versioned_paths)),
]
