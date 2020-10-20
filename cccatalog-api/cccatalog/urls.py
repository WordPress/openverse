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
from cccatalog.api.views.image_views import SearchImages, ImageDetail,\
    Watermark, RelatedImage, OembedView, ReportImageView
from cccatalog.api.views.site_views import HealthCheck, ImageStats, Register, \
    CheckRates, VerifyEmail, ProxiedImage
from cccatalog.api.views.link_views import CreateShortenedLink, \
    ResolveShortenedLink
from cccatalog.settings import API_VERSION, WATERMARK_ENABLED
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView
import rest_framework.permissions
from drf_yasg.utils import swagger_auto_schema
from cccatalog.api.serializers.image_serializers import\
    ReportImageSerializer
from cccatalog.example_responses import images_report_create_201_example

description = """
# Introduction
The Creative Commons Catalog API ('cccatalog-api') is a system
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
needs. See the `/v1/auth_tokens/register` endpoint for instructions on obtaining
an API key.

Pull requests are welcome!
[Contribute on GitHub](https://github.com/creativecommons/cccatalog-api)

# REST API

## Overview
The cccatalog REST API allows you to integrate and perform queries to digital \
media under Creative Commons.
The API is based on REST principles. It supports GET, POST, and DELETE requests.
GET request is used to retrieve information from a resource \
and a POST to update an entity. DELETE removes an entity.
After receiving your request, the API sends back an HTTP code as a response.

## Possible Response Status Codes
| Status Code   | Description           | Notes  |
| ------------- |-------------          | -----  |
| 200           | OK                    | The request was successful |
| 201           | OK                    | The request was successful |
| 204           | OK                    | No Content |
| 301           | Bad Request           | Moved Permanently |
| 400           | Bad Request           | The request could not be understood by the server. Incoming parameters might not be valid |
| 403           | Forbidden             | Access to requested content is forbidden for some reason |
| 404           | Not Found             | The requested content could not be found by the server |
| 500           | Internal Server Error | The request could not be processed by the server for an unknown reason |

# Register and Authenticate

## Register for a key
Before using the CC Catalog API, you need to register access via OAuth2. 
This can be done using the `/v1/auth_tokens/register` endpoint. 

<br>
Example on how to register for a key

```
$ curl -X POST -H "Content-Type: application/json" -d '{"name": "My amazing project", "description": "To access CC Catalog API", "email": "cccatalog-api@creativecommons.org"}' https://api.creativecommons.engineering/v1/auth_tokens/register
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
In order to use the CC Catalog API endpoints, you need to include access token \
in the header.
This can be done by exchanging your client credentials for a token using the \
`v1/auth_tokens/token/` endpoint.

<br>
Example on how to authenticate using OAuth2

```
$ curl -X POST -d "client_id=pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda&client_secret=YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e&grant_type=client_credentials" https://api.creativecommons.engineering/v1/auth_tokens/token/
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
$ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=test
```
<br>
<blockquote>
   <b>NOTE :</b> Your token will be throttled like an anonymous user \
   until the email address has been verified.
</blockquote>

# Glossary

## Access Token
A private string that authorizes an application to make API requests 

## API
An abbreviation for Application Programming Interface.

## CC
An abbreviation for Creative Commons.

## Client ID
A publicly exposed string used by CC Catalog API to identify the application.

## Client Secret
A private string that authenticates the identity of the application to the CC Catalog API.

## Copyright
A type of intellectual property that gives the owner an exclusive right to reproduce, publish, sell or distribute content.

## Mature content
Any content that requires the audience to be 18 and older.

## OAuth2
An authorization framework that enables a third party application to get access to an HTTP service.

## Sensitive content
Any content that depicts graphic violence, adult content, and hostility or malice against others based on their race, religion, disability, sexual orientation, ethnicity and national origin.
"""  # noqa

logo_url = "https://mirrors.creativecommons.org/presskit/logos/cc.logo.svg"
tos_url = "https://api.creativecommons.engineering/terms_of_service.html"
license_url =\
    "https://github.com/creativecommons/cccatalog-api/blob/master/LICENSE"
schema_view = get_schema_view(
    openapi.Info(
        title="Creative Commons Catalog API",
        default_version=API_VERSION,
        description=description,
        contact=openapi.Contact(email="cccatalog-api@creativecommons.org"),
        license=openapi.License(name="MIT License", url=license_url),
        terms_of_service=tos_url,
        x_logo={
            "url": logo_url,
            "backgroundColor": "#FFFFFF"
        }
    ),
    public=True,
    permission_classes=(rest_framework.permissions.AllowAny,),
)

report_image_bash = \
    """
    # Report an issue about image ID (7c829a03-fb24-4b57-9b03-65f43ed19395)
    curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" -d '{"reason": "mature", "identifier": "7c829a03-fb24-4b57-9b03-65f43ed19395", "description": "This image contains sensitive content"}' https://api.creativecommons.engineering/v1/images/7c829a03-fb24-4b57-9b03-65f43ed19395/report
    """  # noqa

report_image_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['reason', 'identifier'],
    properties={
        'reason': openapi.Schema(
            title="Reason",
            type=openapi.TYPE_STRING,
            enum=["mature", "dmca", "other"],
            max_length=20,
            description="The reason to report image to Creative Commons."
        ),
        'identifier': openapi.Schema(
            title="Identifier",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description="The ID for image to be reported."
        ),
        'description': openapi.Schema(
            title="Description",
            type=openapi.TYPE_STRING,
            max_length=500,
            nullable=True,
            description="The explanation on why image is being reported."
        )
    },
    example={
        "reason": "mature",
        "identifier": "7c829a03-fb24-4b57-9b03-65f43ed19395",
        "description": "This image contains sensitive content"
    }
)

decorated_report_image_view = \
    swagger_auto_schema(
        method='post',
        responses={
            "201": openapi.Response(
                description="OK",
                examples=images_report_create_201_example,
                schema=ReportImageSerializer
            )
        },
        request_body=report_image_request,
        code_examples=[
            {
                'lang': 'Bash',
                'source': report_image_bash
            }
        ]
    )(ReportImageView.as_view())

versioned_paths = [
    path('', schema_view.with_ui('redoc', cache_timeout=None), name='root'),
    path('auth_tokens/register', Register.as_view(), name='register'),
    path('rate_limit', CheckRates.as_view(), name='key_info'),
    path(
        'auth_tokens/verify/<str:code>',
        VerifyEmail.as_view(),
        name='verify-email'
    ),
    re_path(
        r'auth_tokens/',
        include('oauth2_provider.urls', namespace='oauth2_provider')
    ),
    path(
        'images/<str:identifier>', ImageDetail.as_view(), name='image-detail'
    ),
    path(
        'images/<str:identifier>/report',
        decorated_report_image_view,
        name='report-image'
    ),
    path(
        'recommendations/images/<str:identifier>',
        RelatedImage.as_view(),
        name='related-images'
    ),
    re_path('images', SearchImages.as_view(), name='images'),
    path(
        'sources',
        ImageStats.as_view(),
        name='about-image'
    ),
    path('link', CreateShortenedLink.as_view(), name='make-link'),
    path('link/<str:path>', ResolveShortenedLink.as_view(), name='resolve'),
    path('thumbs/<str:identifier>', ProxiedImage.as_view(), name='thumbs'),
    path('oembed', OembedView.as_view(), name='oembed')
]
if WATERMARK_ENABLED:
    versioned_paths.append(
        path('watermark/<str:identifier>', Watermark.as_view())
    )

urlpatterns = [
    path('', RedirectView.as_view(url='/v1')),
    path('admin/', admin.site.urls),
    re_path('healthcheck', HealthCheck.as_view()),
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'
    ),
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=15),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=15),
        name='schema-redoc'
    ),
    path('v1/', include(versioned_paths))
]
