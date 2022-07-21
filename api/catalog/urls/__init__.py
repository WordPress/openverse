"""catalog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from rest_framework.routers import SimpleRouter

from catalog.api.utils.status_code_view import get_status_code_view
from catalog.api.views.audio_views import AudioViewSet
from catalog.api.views.health_views import HealthCheck
from catalog.api.views.image_views import ImageViewSet
from catalog.api.views.oauth2_views import CheckRates
from catalog.urls.auth_tokens import urlpatterns as auth_tokens_patterns
from catalog.urls.swagger import urlpatterns as swagger_patterns


discontinuation_message = {
    "error": "Gone",
    "reason": "This API endpoint has been discontinued.",
}

versioned_paths = [
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
    path("healthcheck", HealthCheck.as_view()),
    # Swagger documentation
    path("", include(swagger_patterns)),
    # API
    path("v1/", include(versioned_paths)),
]
