"""
URL configuration for the Openverse API.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.decorators import api_view
from rest_framework.routers import SimpleRouter

from api.views.audio_views import AudioViewSet
from api.views.health_views import HealthCheck
from api.views.image_views import ImageViewSet
from conf.urls.auth_tokens import urlpatterns as auth_tokens_urlpatterns
from conf.urls.deprecations import urlpatterns as deprecations_urlpatterns
from conf.urls.openapi import urlpatterns as openapi_urlpatterns
from conf.wsgi import TRACING


if TRACING:
    prev_snapshot = None

    @api_view(["GET"])
    def _trace_view(request):
        global prev_snapshot
        import pprint
        import time
        import tracemalloc

        from django.http.response import HttpResponse

        snapshot = tracemalloc.take_snapshot()
        if prev_snapshot:
            top_stats = snapshot.compare_to(prev_snapshot, "lineno", cumulative=True)[
                :10
            ]
        else:
            top_stats = snapshot.statistics("lineno", cumulative=True)[:10]

        prev_snapshot = snapshot

        content = f"{time.time()}\n" f"{pprint.pformat(top_stats, indent=4)}"

        return HttpResponse(content=content, status=200, content_type="text/plain")


versioned_paths = [
    path("", include(openapi_urlpatterns)),  # OpenAPI
    path("", include(auth_tokens_urlpatterns)),  # Authentication endpoints
    path("", include(deprecations_urlpatterns)),  # Deprecated, redirects to new URL
]

router = SimpleRouter()
router.register("audio", AudioViewSet, basename="audio")
router.register("images", ImageViewSet, basename="image")
versioned_paths += router.urls

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="root")),
    path("admin/", admin.site.urls),
    path("healthcheck/", HealthCheck.as_view(), name="health"),
    path("v1/", include(versioned_paths)),
]

if TRACING:
    urlpatterns.append(path("_trace/", _trace_view))

if settings.ENVIRONMENT == "local":
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
