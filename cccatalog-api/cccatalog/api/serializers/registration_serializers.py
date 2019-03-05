from rest_framework import serializers
from cccatalog.api.models import OAuth2Registration
from oauth2_provider.models import AbstractApplication


class OAuth2RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuth2Registration
        fields = ('name', 'description', 'email')


class OAuth2RegistrationSuccessful(serializers.ModelSerializer):
    class Meta:
        model = AbstractApplication
        fields = ('name', 'client_id', 'client_secret')
