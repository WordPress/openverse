"""cccatalog URL Configuration

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
from django.contrib import admin
from django.urls import path, re_path
# from django.conf.urls import include
from cccatalog.api.views.image_views import SearchImages, ImageDetail
from cccatalog.api.views.site_views import HealthCheck, ImageStats
from cccatalog.api.views.list_views import CreateList, ListDetail
from cccatalog.api.views.link_views import CreateShortenedLink, \
    ResolveShortenedLink
from cccatalog.settings import API_VERSION
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import rest_framework.permissions

description = """
The Creative Commons Catalog API ('cccatalog-api') is a system
that allows programmatic access to public domain digital media. It is our 
ambition to index and catalog billions of Creative Commons works, including
articles, songs, videos, photographs, paintings, and more. Using this API,
developers will be able to access the digital commons in their own
applications.
"""


schema_view = get_schema_view(
    openapi.Info(
        title="Creative Commons Catalog API",
        default_version=API_VERSION,
        description=description,
        contact=openapi.Contact(email="alden@creativecommons.org"),
        license=openapi.License(name="MIT License"),
        x_logo={
            "url": "https://mirrors.creativecommons.org/presskit/logos/cc.logo.svg",
            "backgroundColor": "#FFFFFF"
        }
    ),
    public=True,
    permission_classes=(rest_framework.permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('redoc', cache_timeout=None),
        name='root'),
    path('admin/', admin.site.urls),
    path('list', CreateList.as_view()),
    path('list/<str:slug>', ListDetail.as_view(), name='list-detail'),
    # re_path(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # re_path(r'^social/', include('rest_framework_social_oauth2.urls')),
    re_path('image/search', SearchImages.as_view()),
    path('image/<str:identifier>', ImageDetail.as_view(), name='image-detail'),
    path('statistics/image', ImageStats.as_view(), name='about-image'),
    path('link', CreateShortenedLink.as_view(), name='make-link'),
    path('link/<str:path>', ResolveShortenedLink.as_view(), name='resolve'),
    re_path('healthcheck', HealthCheck.as_view()),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=15),
        name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=15),
        name='schema-redoc'),
    ]
