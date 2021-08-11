from django.urls import path, include

from catalog.api.views.site_views import (
    Register,
    VerifyEmail,
)

urlpatterns = [
    path(
        'register',
        Register.as_view(),
        name='register'
    ),
    path(
        'verify/<str:code>',
        VerifyEmail.as_view(),
        name='verify-email'
    ),
    path(
        '',
        include('oauth2_provider.urls', namespace='oauth2_provider')
    ),
]