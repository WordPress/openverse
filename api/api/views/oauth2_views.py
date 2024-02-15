import json
import logging as log
import secrets
import smtplib
from textwrap import dedent

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema
from oauth2_provider.generators import generate_client_secret
from oauth2_provider.views import TokenView as BaseTokenView
from redis.exceptions import ConnectionError

from api.docs.oauth2_docs import key_info, register, token
from api.models import OAuth2Verification, ThrottledApplication
from api.serializers.oauth2_serializers import (
    OAuth2KeyInfoSerializer,
    OAuth2RegistrationSerializer,
)
from api.utils.oauth2_helper import get_token_info
from api.utils.throttle import OnePerSecond, TenPerDay


module_logger = log.getLogger(__name__)


@extend_schema(tags=["auth"])
class Register(APIView):
    throttle_classes = (TenPerDay,)

    @register
    def post(self, request, format=None):
        """
        Register an application to access to API via OAuth2.

        Upon registering, you will receive a `client_id` and `client_secret`,
        which you can then use to authenticate using the standard OAuth2 flow.

        > ⚠️ **WARNINGS:**
        > - Store your `client_id` and `client_secret` because you will not be
        >   able to retrieve them later.
        > - You must keep `client_secret` confidential, as anybody with your
        >   `client_secret` can impersonate your application.

        You must verify your email address by click the link sent to you in an
        email. Until you do that, the application will be subject to the same
        rate limits as an anonymous user.
        """

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
        verification_msg = dedent(
            f"""
            To verify your Openverse API credentials, click on the following link:

            {link}

            If you believe you received this message in error, please disregard it.
        """
        )
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
    """Enable a user's OAuth2 key upon visiting the emailed verification link."""

    schema = None  # Hide this view from the OpenAPI schema.

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


@extend_schema(tags=["auth"])
class TokenView(APIView, BaseTokenView):
    @token
    def post(self, request):
        """
        Get an access token using client credentials.

        To authenticate your requests to the Openverse API, you need to provide
        an access token as a bearer token in the `Authorization` header of your
        requests. This endpoints takes your client ID and secret, and issues an
        access token.

        > **NOTE:** This endpoint only accepts data as
        > `application/x-www-form-urlencoded`. Any other encoding will not work.

        Once your access token expires, you can request another one from this
        endpoint.
        """

        res = super().post(request._request)
        data = json.loads(res.content)
        return Response(data, status=res.status_code)


@extend_schema(tags=["auth"])
class CheckRates(APIView):
    throttle_classes = (OnePerSecond,)

    @key_info
    def get(self, request, format=None):
        """
        Get information about your API key.

        You can use this endpoint to get information about your API key such as
        `requests_this_minute`, `requests_today`, and `rate_limit_model`.

        > ℹ️ **NOTE:** If you get a 403 Forbidden response, it means your access
        > token has expired.
        """

        # TODO: Replace 403 responses with DRF `authentication_classes`.
        if not request.auth:
            raise PermissionDenied("Forbidden", 403)

        access_token = str(request.auth)
        token_info = get_token_info(access_token)

        if not token_info or not (client_id := token_info.client_id):
            # This shouldn't happen if `request.auth` was true above,
            # but better safe than sorry
            raise PermissionDenied("Forbidden", 403)

        throttle_type = token_info.rate_limit_model
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
            return APIException("Unknown API key rate limit type")

        try:
            sustained_requests_list = cache.get(sustained_throttle_key)
            sustained_requests = (
                len(sustained_requests_list) if sustained_requests_list else None
            )
            burst_requests_list = cache.get(burst_throttle_key)
            burst_requests = len(burst_requests_list) if burst_requests_list else None
            status = 200
        except ConnectionError:
            logger = module_logger.getChild("CheckRates.get")
            logger.warning("Redis connect failed, cannot get key usage.")
            burst_requests = None
            sustained_requests = None
            status = 424

        response_data = OAuth2KeyInfoSerializer(
            {
                "requests_this_minute": burst_requests,
                "requests_today": sustained_requests,
                "rate_limit_model": throttle_type,
                "verified": token_info.verified,
            }
        )
        return Response(status=status, data=response_data.data)
