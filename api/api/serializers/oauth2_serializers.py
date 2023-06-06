from rest_framework import serializers

from oauth2_provider.models import Application

from api.models import OAuth2Registration


class OAuth2RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuth2Registration
        fields = ("name", "description", "email")


class OAuth2ApplicationSerializer(serializers.Serializer):
    client_id = serializers.CharField(
        help_text="The unique, public identifier of your application.",
    )
    client_secret = serializers.CharField(
        help_text="The secret key used to authenticate your application.",
    )
    name = serializers.CharField(
        help_text="The name of your application or project.",
    )
    msg = serializers.CharField(
        help_text="Some additional information about the application.",
    )


class OAuth2RegistrationSuccessful(serializers.ModelSerializer):
    name = serializers.CharField(
        help_text="A unique human-readable name for your application "
        "or project requiring access to the Openverse API."
    )
    client_id = serializers.CharField(
        help_text="A publicly exposed string used by Openverse API "
        "to identify the application."
    )
    client_secret = serializers.CharField(
        help_text="A private string that authenticates the identity "
        "of the application to the Openverse API."
    )

    class Meta:
        model = Application
        fields = ("name", "client_id", "client_secret")


class OAuth2KeyInfoSerializer(serializers.Serializer):
    requests_this_minute = serializers.IntegerField(
        help_text="The number of requests your key has performed in the last minute.",
        allow_null=True,
    )
    requests_today = serializers.IntegerField(
        help_text="The number of requests your key has performed in the last day.",
        allow_null=True,
    )
    rate_limit_model = serializers.CharField(
        help_text="The type of rate limit applied to your key. Can be "
        "'standard' or 'enhanced'; enhanced users enjoy higher rate "
        "limits than their standard key counterparts. Contact "
        "Openverse if you need a higher rate limit."
    )
    verified = serializers.BooleanField(
        help_text="Whether the application has verified the submitted email address."
    )


class OAuth2TokenRequestSerializer(serializers.Serializer):
    """
    Serializes a request for an access token.

    This is a dummy serializer for OpenAPI and is not actually used.
    """

    client_id = serializers.CharField(
        help_text="The unique, public identifier of your application.",
    )

    client_secret = serializers.CharField(
        help_text="The secret key used to authenticate your application.",
    )

    grant_type = serializers.ChoiceField(choices=["client_credentials"])


class OAuth2TokenSerializer(serializers.Serializer):
    """
    Serializes the response for an access token.

    This is a dummy serializer for OpenAPI and is not actually used.
    """

    access_token = serializers.CharField(
        help_text="The access token that can be used to authenticate requests.",
    )
    token_type = serializers.CharField(
        help_text="The type of token. This will always be 'Bearer'.",
    )
    expires_in = serializers.IntegerField(
        help_text="The number of seconds until the token expires.",
    )
    scope = serializers.CharField(
        help_text="The scope of the token.",
    )
