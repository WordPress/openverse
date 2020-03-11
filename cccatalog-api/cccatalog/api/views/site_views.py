import logging as log
import secrets
import smtplib
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import serializers
from cccatalog.api.controllers.search_controller import get_providers
from cccatalog.api.serializers.oauth2_serializers import\
    OAuth2RegistrationSerializer, OAuth2RegistrationSuccessful, OAuth2KeyInfo
from drf_yasg.utils import swagger_auto_schema
from cccatalog.api.models import ContentProvider, Image
from cccatalog.api.models import ThrottledApplication, OAuth2Verification
from cccatalog.api.utils.throttle import TenPerDay, OnePerSecond
from cccatalog.api.utils.oauth2_helper import get_token_info
from cccatalog.settings import THUMBNAIL_PROXY_URL, THUMBNAIL_WIDTH_PX
from django.core.cache import cache
from django.shortcuts import redirect

IDENTIFIER = 'provider_identifier'
NAME = 'provider_name'
FILTER = 'filter_content'
URL = 'domain_name'


class HealthCheck(APIView):
    """
    Returns a `200 OK` response if the server is running.

    This endpoint is used in production to ensure that the server should receive
    traffic. If no response is provided, the server is deregistered from the
    load balancer and destroyed.
    """
    swagger_schema = None

    def get(self, request, format=None):
        return Response('', status=200)


class AboutImageResponse(serializers.Serializer):
    """ The full image search response. """
    source_name = serializers.CharField()
    image_count = serializers.IntegerField()
    display_name = serializers.CharField()
    source_url = serializers.CharField()


class ImageStats(APIView):
    """
    List all providers in the Creative Commons image catalog, in addition to the
    number of images from each data source.
    """
    @swagger_auto_schema(operation_id='image_stats',
                         responses={
                             200: AboutImageResponse(many=True)
                         })
    def get(self, request, format=None):
        provider_data = ContentProvider \
            .objects \
            .values(IDENTIFIER, NAME, FILTER, URL)
        provider_table = {
            rec[IDENTIFIER]:
                (rec[NAME], rec[FILTER], rec[URL]) for rec in provider_data
        }
        providers = get_providers('image')
        response = []
        for provider in providers:
            if provider in provider_table:
                display_name, _filter, provider_url = provider_table[provider]
                if not _filter:
                    response.append(
                        {
                            'source_name': provider,
                            'image_count': providers[provider],
                            'display_name': display_name,
                            'source_url': provider_url
                        }
                    )
            else:
                msg = 'provider_identifier missing from content_provider' \
                      ' table: {}. Check for typos/omissions.'.format(provider)
                log.error(msg)
        return Response(status=200, data=response)


class Register(APIView):
    """
    Register for access to the API via OAuth2. Authenticated users have higher
    rate limits than anonymous users. Additionally, by identifying yourself,
    you can request Creative Commons to adjust your personal rate limit
    depending on your organization's needs.

    Upon registering, you will receive a `client_id` and `client_secret`, which
    you can then use to authenticate using the standard OAuth2 Client
    Credentials flow. You must keep `client_secret` confidential; anybody with
    your `client_secret` can impersonate your application.

    Example registration and authentication flow:

    First, register for a key.
    ```
    $ curl -XPOST -H "Content-Type: application/json" -d '{"name": "My amazing project", "description": "A description", "email": "example@example.com"}' https://api.creativecommons.engineering/v1/auth_tokens/register
    {
        "client_secret" : "YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e",
        "client_id" : "pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda",
        "name" : "My amazing project"
    }

    ```

    Now, exchange your client credentials for a token.
    ```
    $ curl -X POST -d "client_id=pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda&client_secret=YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e&grant_type=client_credentials" https://api.creativecommons.engineering/v1/auth_tokens/token/
    {
       "access_token" : "DLBYIcfnKfolaXKcmMC8RIDCavc2hW",
       "scope" : "read write groups",
       "expires_in" : 36000,
       "token_type" : "Bearer"
    }
    ```

    Check your email for a verification link. After you have followed the link,
    your API key will be activated.

    Include the `access_token` in the authorization header to use your key in
    your future API requests.

    ```
    $ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=test
    ```

    **Be advised** that your token will be throttled like an anonymous user
    until the email address has been verified.
    """  # noqa
    throttle_classes = (TenPerDay,)

    @swagger_auto_schema(operation_id='register_api_oauth2',
                         request_body=OAuth2RegistrationSerializer,
                         responses={
                             201: OAuth2RegistrationSuccessful
                         })
    def post(self, request, format=None):
        # Store the registration information the developer gave us.
        serialized = OAuth2RegistrationSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(
                status=400,
                data=serialized.errors
            )
        else:
            serialized.save()

        # Produce a client ID, client secret, and authorize the application in
        # the OAuth2 backend.
        new_application = ThrottledApplication(
            name=serialized.validated_data['name'],
            skip_authorization=False,
            client_type='Confidential',
            authorization_grant_type='client-credentials',
            verified=False
        )
        new_application.save()
        # Send a verification email.
        verification = OAuth2Verification(
            email=serialized.validated_data['email'],
            code=secrets.token_urlsafe(64),
            associated_application=new_application
        )
        verification.save()
        token = verification.code
        link = request.build_absolute_uri(reverse('verify-email', [token]))
        verification_msg = f"""
To verify your CC Catalog API credentials, click on the following link:

{link}

If you believe you received this message in error, please disregard it.
        """
        try:
            send_mail(
                subject='Verify your API credentials',
                message=verification_msg,
                from_email='noreply-cccatalog@creativecommons.engineering',
                recipient_list=[verification.email],
                fail_silently=False
            )
        except smtplib.SMTPException as e:
            log.error('Failed to send API verification email!')
            log.error(e)
        # Give the user their newly created credentials.
        return Response(
            status=201,
            data={
                'client_id': new_application.client_id,
                'client_secret': new_application.client_secret,
                'name': new_application.name,
                'msg': 'Check your email for a verification link.'
            }
        )


class VerifyEmail(APIView):
    """
    When the user follows the verification link sent to their email, enable
    their OAuth2 key.
    """
    swagger_schema = None

    def get(self, request, code, format=None):
        try:
            verification = OAuth2Verification.objects.get(code=code)
            application_pk = verification.associated_application.pk
            ThrottledApplication\
                .objects\
                .filter(pk=application_pk)\
                .update(verified=True)
            verification.delete()
            return Response(
                status=200,
                data={'msg': 'Successfully verified email. Your OAuth2 '
                             'credentials are now active.'}
            )
        except OAuth2Verification.DoesNotExist:
            return Response(
                status=500,
                data={'msg': 'Invalid verification code. Did you validate your '
                             'credentials already?'}
            )


class CheckRates(APIView):
    """
    Return information about the rate limit status of your API key.
    """
    throttle_classes = (OnePerSecond,)

    @swagger_auto_schema(operation_id='key_info',
                         responses={
                             200: OAuth2KeyInfo,
                             403: 'Forbidden'
                         })
    def get(self, request, format=None):
        if not request.auth:
            return Response(status=403, data='Forbidden')

        access_token = str(request.auth)
        client_id, rate_limit_model, verified = get_token_info(access_token)

        if not client_id:
            return Response(status=403, data='Forbidden')

        throttle_type = rate_limit_model
        throttle_key = 'throttle_{scope}_{client_id}'
        if throttle_type == 'standard':
            sustained_throttle_key = throttle_key.format(
                scope='oauth2_client_credentials_sustained',
                client_id=client_id
            )
            burst_throttle_key = throttle_key.format(
                scope='oauth2_client_credentials_burst',
                client_id=client_id
            )
        elif throttle_type == 'enhanced':
            sustained_throttle_key = throttle_key.format(
                scope='enhanced_oauth2_client_credentials_sustained',
                client_id=client_id
            )
            burst_throttle_key = throttle_key.format(
                scope='enhanced_oauth2_client_credentials_burst',
                client_id=client_id
            )
        else:
            return Response(status=500, data='Unknown API key rate limit type')

        sustained_requests_list = cache.get(sustained_throttle_key)
        sustained_requests = \
            len(sustained_requests_list) if sustained_requests_list else None
        burst_requests_list = cache.get(burst_throttle_key)
        burst_requests = \
            len(burst_requests_list) if burst_requests_list else None

        response_data = {
            'requests_this_minute': burst_requests,
            'requests_today': sustained_requests,
            'rate_limit_model': throttle_type,
            'verified': verified
        }
        return Response(status=200, data=response_data)


class Thumbs(APIView):

    @swagger_auto_schema(operation_id="thumb_lookup",
                         responses={
                             200: None,
                             301: 'Moved Permanently',
                             400: 'Bad Request',
                             404: 'Not Found'
                         })

    def get(self, request, path, format=None):
        path_element = path.split(".")
        identifier = path_element[0]
        extname = ""
        if len(path_element) == 2:
            extname = path_element[1]
        elif len(path_element) > 2:
            return Response(status=400)
        try:
            image = Image.objects.get(identifier=identifier)
            if extname and image.url.split(".")[-1] != extname:
                return Response(status=404, data='Not Found')
        except Image.DoesNotExist:
            return Response(status=404, data='Not Found')
        proxied = '{proxy_url}/{width}/{original}'.format(
                proxy_url=THUMBNAIL_PROXY_URL,
                width=THUMBNAIL_WIDTH_PX,
                original=image.url
            )
        return redirect(proxied)
