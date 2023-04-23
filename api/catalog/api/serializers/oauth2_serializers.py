from rest_framework import serializers

from oauth2_provider.models import Application

from catalog.api.models import OAuth2Registration


class OAuth2RegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        help_text=(
            "A unique human-readable name for your application or project "
            "requiring access to the Openverse API."
        ),
        required=True,
        min_length=1,
        max_length=150,
    )
    description = serializers.CharField(
        help_text=(
            "A description of what you are trying to achieve with your project "
            "using the API. Please provide as much detail as possible!"
        ),
        min_length=1,
        max_length=10000,
    )
    email = serializers.EmailField(
        help_text=(
            "A valid email that we can reach you at if we have any questions "
            "about your use case or data consumption."
        ),
        min_length=1,
        max_length=254,
    )

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
