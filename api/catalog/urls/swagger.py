from django.conf import settings
from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny


description_path = settings.BASE_DIR.joinpath(
    "catalog",
    "api",
    "docs",
    "README.md",
)
with open(description_path, "r") as description_file:
    description = description_file.read()

tos_url = "https://api.openverse.engineering/terms_of_service.html"
license_url = "https://github.com/WordPress/openverse-api/blob/HEAD/LICENSE"
logo_url = "https://raw.githubusercontent.com/WordPress/openverse/HEAD/brand/logo.svg"
schema_view = get_schema_view(
    openapi.Info(
        title="Openverse API consumer docs",
        default_version=settings.API_VERSION,
        description=description,
        contact=openapi.Contact(email=settings.CONTACT_EMAIL),
        license=openapi.License(name="MIT License", url=license_url),
        terms_of_service=tos_url,
        x_logo={"url": logo_url, "backgroundColor": "#fafafa"},
    ),
    public=True,
    permission_classes=(AllowAny,),
)

cache_timeout = 0 if settings.DEBUG else 15

urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=None),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=cache_timeout),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=cache_timeout),
        name="schema-redoc",
    ),
    re_path(
        r"^v1/$", schema_view.with_ui("redoc", cache_timeout=cache_timeout), name="root"
    ),
]
