import logging as log
import secrets
import smtplib

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.generators import generate_client_secret

from catalog.api.docs.media_docs import refer_sample
from catalog.api.models import OAuth2Verification, ThrottledApplication
from catalog.api.serializers.error_serializers import (
    ForbiddenErrorSerializer,
    InternalServerErrorSerializer,
)
from catalog.api.serializers.oauth2_serializers import (
    OAuth2KeyInfo,
    OAuth2RegistrationSerializer,
    OAuth2RegistrationSuccessful,
)
from catalog.api.utils.oauth2_helper import get_token_info
from catalog.api.utils.throttle import OnePerSecond, TenPerDay
from catalog.custom_auto_schema import CustomAutoSchema
from catalog.example_responses import (
    key_info_200_example,
    key_info_403_example,
    key_info_500_example,
    register_api_oauth2_201_example,
)


class Register(APIView):
    swagger_schema = CustomAutoSchema
    register_api_oauth2_description = f"""
register_api_oauth2 is an API endpoint to register access to the API via OAuth2.

Upon registering, you will receive a `client_id` and `client_secret`, which you can then
use to authenticate using the standard OAuth2 Client Credentials flow. See the Register
and Authenticate section for instructions on registering access to the API via OAuth2.

> **WARNING:** You must keep `client_secret` confidential, as anybody with your
> `client_secret` can impersonate your application.

Authenticated users have higher rate limits than anonymous users. Additionally, by
identifying yourself, you can request Openverse to adjust your personal rate limit
depending on your organization's needs.

{refer_sample}"""

    throttle_classes = (TenPerDay,)
    register_api_oauth2_response = {
        "201": openapi.Response(
            description="OK",
            examples=register_api_oauth2_201_example,
            schema=OAuth2RegistrationSuccessful,
        )
    }

    register_api_oauth2_bash = """
# Register for a key
curl \\
  -X POST \\
  -H "Content-Type: application/json" \\
  -d '{"name": "My amazing project", "description": "To access Openverse API", "email": "user@example.com"}' \\
  https://api.openverse.engineering/v1/auth_tokens/register/
"""  # noqa: E501

    register_api_oauth2_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name", "description", "email"],
        properties={
            "name": openapi.Schema(
                title="Name",
                type=openapi.TYPE_STRING,
                min_length=1,
                max_length=150,
                description="A unique human-readable name for your application "
                "or project requiring access to the Openverse API.",
            ),
            "description": openapi.Schema(
                title="Description",
                type=openapi.TYPE_STRING,
                min_length=1,
                max_length=10000,
                description="A description of what you are trying to achieve "
                "with your project using the API. Please provide "
                "as much detail as possible!",
            ),
            "email": openapi.Schema(
                title="Email",
                type=openapi.TYPE_STRING,
                min_length=1,
                max_length=254,
                format=openapi.FORMAT_EMAIL,
                description="A valid email that we can reach you at if we "
                "have any questions about your use case or "
                "data consumption.",
            ),
        },
        example={
            "name": "My amazing project",
            "description": "To access Openverse API",
            "email": "user@example.com",
        },
    )

    @swagger_auto_schema(
        operation_id="register_api_oauth2",
        operation_description=register_api_oauth2_description,
        request_body=register_api_oauth2_request,
        responses=register_api_oauth2_response,
        code_examples=[{"lang": "Bash", "source": register_api_oauth2_bash}],
    )
    def post(self, request, format=None):
        # Store the registration information the developer gave us.
        serialized = OAuth2RegistrationSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(status=400, data=serialized.errors)
        else:
            serialized.save()

        # Produce a client ID, client secret, and authorize the application in
        # the OAuth2 backend.
        client_secret = generate_client_secret()
        new_application = ThrottledApplication(
            name=serialized.validated_data["name"],
            skip_authorization=False,
            client_type="Confidential",
            authorization_grant_type="client-credentials",
            verified=False,
            client_secret=client_secret,
        )
        new_application.save()
        # Send a verification email.
        verification = OAuth2Verification(
            email=serialized.validated_data["email"],
            code=secrets.token_urlsafe(64),
            associated_application=new_application,
        )
        verification.save()
        token = verification.code
        link = request.build_absolute_uri(reverse("verify-email", [token]))
        verification_msg = f"""
To verify your Openverse API credentials, click on the following link:

{link}

If you believe you received this message in error, please disregard it.
        """
        try:
            send_mail(
                subject="Verify your API credentials",
                message=verification_msg,
                from_email=settings.EMAIL_SENDER,
                recipient_list=[verification.email],
                fail_silently=False,
            )
        except smtplib.SMTPException as e:
            log.error("Failed to send API verification email!")
            log.error(e)
        # Give the user their newly created credentials.
        return Response(
            status=201,
            data={
                "client_id": new_application.client_id,
                "client_secret": client_secret,
                "name": new_application.name,
                "msg": "Check your email for a verification link.",
            },
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
            ThrottledApplication.objects.filter(pk=application_pk).update(verified=True)
            verification.delete()
            return Response(
                status=200,
                data={
                    "msg": "Successfully verified email. Your OAuth2 "
                    "credentials are now active."
                },
            )
        except OAuth2Verification.DoesNotExist:
            return Response(
                status=500,
                data={
                    "msg": "Invalid verification code. Did you validate your "
                    "credentials already?"
                },
            )


class CheckRates(APIView):
    swagger_schema = CustomAutoSchema
    key_info_description = f"""
key_info is an API endpoint to get information about your API key.

You can use this endpoint to get information about your API key such as
`requests_this_minute`, `requests_today`, and `rate_limit_model`.

> **NOTE:** If you get a 403 Forbidden response, it means your access token has expired.

{refer_sample}"""

    throttle_classes = (OnePerSecond,)

    key_info_response = {
        "200": openapi.Response(
            description="OK", examples=key_info_200_example, schema=OAuth2KeyInfo
        ),
        "403": openapi.Response(
            description="Forbidden",
            examples=key_info_403_example,
            schema=ForbiddenErrorSerializer,
        ),
        "500": openapi.Response(
            description="Internal Server Error",
            examples=key_info_500_example,
            schema=InternalServerErrorSerializer,
        ),
    }

    key_info_bash = """
curl \\
  -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" \\
  http://api.openverse.engineering/v1/rate_limit/
"""

    @swagger_auto_schema(
        operation_id="key_info",
        operation_description=key_info_description,
        responses=key_info_response,
        code_examples=[{"lang": "Bash", "source": key_info_bash}],
    )
    def get(self, request, format=None):
        if not request.auth:
            return Response(status=403, data="Forbidden")

        access_token = str(request.auth)
        client_id, rate_limit_model, verified = get_token_info(access_token)

        if not client_id:
            return Response(status=403, data="Forbidden")

        throttle_type = rate_limit_model
        throttle_key = "throttle_{scope}_{client_id}"
        if throttle_type == "standard":
            sustained_throttle_key = throttle_key.format(
                scope="oauth2_client_credentials_sustained", client_id=client_id
            )
            burst_throttle_key = throttle_key.format(
                scope="oauth2_client_credentials_burst", client_id=client_id
            )
        elif throttle_type == "enhanced":
            sustained_throttle_key = throttle_key.format(
                scope="enhanced_oauth2_client_credentials_sustained",
                client_id=client_id,
            )
            burst_throttle_key = throttle_key.format(
                scope="enhanced_oauth2_client_credentials_burst", client_id=client_id
            )
        elif throttle_type == "exempt":
            burst_throttle_key = sustained_throttle_key = throttle_key.format(
                scope="exempt_oauth2_client_credentials_burst", client_id=client_id
            )
        else:
            return Response(status=500, data="Unknown API key rate limit type")

        sustained_requests_list = cache.get(sustained_throttle_key)
        sustained_requests = (
            len(sustained_requests_list) if sustained_requests_list else None
        )
        burst_requests_list = cache.get(burst_throttle_key)
        burst_requests = len(burst_requests_list) if burst_requests_list else None

        response_data = {
            "requests_this_minute": burst_requests,
            "requests_today": sustained_requests,
            "rate_limit_model": throttle_type,
            "verified": verified,
        }
        return Response(status=200, data=response_data)
