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
from django.conf.urls import include
from cccatalog.api import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import rest_framework.permissions


schema_view = get_schema_view(
   openapi.Info(
      title="Creative Commons Catalog API",
      default_version='v1',
      description="Test description",
      contact=openapi.Contact(email="alden@creativecommons.org"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(rest_framework.permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    re_path(r'^social/', include('rest_framework_social_oauth2.urls')),
    re_path('secret/', views.ProtectedView.as_view()),
    re_path('public/', views.PublicView.as_view()),
    re_path('healthcheck', views.HealthCheck.as_view()),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None),
        name='schema-redoc'),
]