from rest_framework import serializers
from catalog.api.models import OAuth2Registration
from oauth2_provider.models import Application


class OAuth2RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuth2Registration
        fields = ('name', 'description', 'email')


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
        fields = ('name', 'client_id', 'client_secret')


class OAuth2KeyInfo(serializers.Serializer):
    requests_this_minute = serializers.IntegerField(
        help_text="The number of requests your key has performed in the last "
                  "minute.",
        allow_null=True
    )
    requests_today = serializers.IntegerField(
        help_text="The number of requests your key has performed in the last "
                  "day.",
        allow_null=True
    )
    rate_limit_model = serializers.CharField(
        help_text="The type of rate limit applied to your key. Can be "
                  "'standard' or 'enhanced'; enhanced users enjoy higher rate "
                  "limits than their standard key counterparts. Contact "
                  "Creative Commons if you need a higher rate limit."
    )
