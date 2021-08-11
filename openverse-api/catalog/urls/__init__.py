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
import rest_framework.permissions
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from catalog.api.views.image_views import Watermark, OembedView
from catalog.api.views.site_views import HealthCheck, CheckRates
from catalog.api.utils.status_code_view import get_status_code_view

from catalog.urls.auth_tokens import urlpatterns as auth_tokens_patterns
from catalog.urls.audio import urlpatterns as audio_patterns
from catalog.urls.images import urlpatterns as images_patterns

description = """
# Introduction
The Openverse API ('openverse-api') is a system
that allows programmatic access to public domain digital media. It is our
ambition to index and catalog billions of Creative Commons works, including
articles, songs, videos, photographs, paintings, and more. Using this API,
developers will be able to access the digital commons in their own
applications.

Please note that there is a rate limit of 5000 requests per day and
60 requests per minute rate limit in place for anonymous users. This is fine
for introducing yourself to the API, but we strongly recommend that you obtain
an API key as soon as possible. Authorized clients have a higher rate limit
of 10000 requests per day and 100 requests per minute. Additionally, Creative
Commons can give your key an even higher limit that fits your application's
needs. See the Register and Authenticate section for instructions on obtaining
an API key.

# Register and Authenticate

## Register for a key
Before using the Openverse API, you need to register access via OAuth2.
This can be done using the `/v1/auth_tokens/register` endpoint.

<br>
Example on how to register for a key

```
$ curl -X POST -H "Content-Type: application/json" -d '{"name": "My amazing project", "description": "To access Openverse API", "email": "zack.krida@automattic.com"}' https://api.openverse.engineering/v1/auth_tokens/register
```

<br>
If your request is succesful, you will get a `client_id` and `client_secret`.

Example of successful request

```
{
    "client_secret" : "YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e",
    "client_id" : "pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda",
    "name" : "My amazing project"
}
```

## Authenticate
In order to use the Openverse API endpoints, you need to include access token \
in the header.
This can be done by exchanging your client credentials for a token using the \
`v1/auth_tokens/token/` endpoint.

<br>
Example on how to authenticate using OAuth2

```
$ curl -X POST -d "client_id=pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda&client_secret=YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e&grant_type=client_credentials" https://api.openverse.engineering/v1/auth_tokens/token/
```

<br>
If your request is successful, you will get an access token.

Example of successful request

```
 {
    "access_token" : "DLBYIcfnKfolaXKcmMC8RIDCavc2hW",
    "scope" : "read write groups",
    "expires_in" : 36000,
    "token_type" : "Bearer"
 }
```

Check your email for a verification link. After you have followed the link, \
your API key will be activated.

## Using Access Token
Include the `access_token` in the authorization header to use your key in \
your future API requests.

<br>
Example

```
$ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.openverse.engineering/v1/images?q=test
```
<br>
<blockquote>
   <b>NOTE :</b> Your token will be throttled like an anonymous user \
   until the email address has been verified.
</blockquote>

# Glossary

#### Access Token
A private string that authorizes an application to make API requests

#### API
An abbreviation for Application Programming Interface.

#### CC
An abbreviation for Creative Commons.

#### Client ID
A publicly exposed string used by Openverse API to identify the application.

#### Client Secret
A private string that authenticates the identity of the application to the Openverse API.

#### Copyright
A type of intellectual property that gives the owner an exclusive right to reproduce, publish, sell or distribute content.

#### Mature content
Any content that requires the audience to be 18 and older.

#### OAuth2
An authorization framework that enables a third party application to get access to an HTTP service.

#### Sensitive content
Any content that depicts graphic violence, adult content, and hostility or malice against others based on their race, religion, disability, sexual orientation, ethnicity and national origin.

# Contribute

We love pull requests! If you’re interested in [contributing on Github](https://github.com/wordpress/openverse-api), here’s a todo list to get started.

- Read up about [Django REST Framework](https://www.django-rest-framework.org/), which is the framework used to build Openverse API
- Read up about [drf-yasg](https://drf-yasg.readthedocs.io/en/stable/), which is a tool used to generate real Swagger/OpenAPI 2.0 specifications
- Read up about Documentation Guidelines, which provides guidelines on how to contribute to documentation, documentation styles and cheat sheet for drf-yasg
- Run the server locally by following this [link](https://github.com/wordpress/openverse-api#running-the-server-locally)
- Update documentation or codebase
- Make sure the updates passed the automated tests in this [file](https://github.com/wordpress/openverse-api/blob/master/.github/workflows/integration-tests.yml)
- Commit and push
- Create pull request
"""  # noqa

# @todo: Reimplement logo once Openverse logomark is finalized
# logo_url = "https://mirrors.creativecommons.org/presskit/logos/cc.logo.svg"
tos_url = "https://api.openverse.engineering/terms_of_service.html"
license_url = \
    "https://github.com/wordpress/openverse-api/blob/master/LICENSE"
schema_view = get_schema_view(
    openapi.Info(
        title="Openverse API",
        default_version=settings.API_VERSION,
        description=description,
        contact=openapi.Contact(email="zack.krida@automattic.com"),
        license=openapi.License(name="MIT License", url=license_url),
        terms_of_service=tos_url,
        # x_logo={
        #     "url": logo_url,
        #     "backgroundColor": "#FFFFFF"
        # }
    ),
    public=True,
    permission_classes=(rest_framework.permissions.AllowAny,),
)

cache_timeout = 0 if settings.DEBUG else 15

discontinuation_message = {
    'error': 'Gone',
    'reason': 'This API endpoint has been discontinued.'
}

versioned_paths = [
    path('rate_limit', CheckRates.as_view(), name='key_info'),
    path('auth_tokens/', include(auth_tokens_patterns)),

    # Audio
    path('audio/', include(audio_patterns)),

    # Images
    path('images/', include(images_patterns)),
    path('oembed', OembedView.as_view(), name='oembed'),

    # Deprecated
    path(
        'sources',
        RedirectView.as_view(pattern_name='image-stats', permanent=True),
        name='about-image'
    ),
    path(
        'recommendations/images/<str:identifier>',
        RedirectView.as_view(pattern_name='image-related', permanent=True),
        name='related-images',
    ),
    path(
        'thumbs/<str:identifier>',
        RedirectView.as_view(pattern_name='image-thumb', permanent=True),
        name='thumbs'
    ),

    # Discontinued
    re_path(
        r'^link/',
        get_status_code_view(discontinuation_message, 410).as_view(),
        name='make-link'
    ),
]
if settings.WATERMARK_ENABLED:
    versioned_paths.append(
        path('watermark/<str:identifier>', Watermark.as_view())
    )

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='root')),
    path('admin/', admin.site.urls),
    path('healthcheck', HealthCheck.as_view()),

    # Swagger documentation
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None),
        name='schema-json'
    ),
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=cache_timeout),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=cache_timeout),
        name='schema-redoc'
    ),
    re_path(
        r'^v1/$',
        schema_view.with_ui('redoc', cache_timeout=cache_timeout),
        name='root'
    ),

    # API
    path('v1/', include(versioned_paths)),
]
