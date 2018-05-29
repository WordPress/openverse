from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_social_oauth2.authentication import SocialAuthentication


class ProtectedView(APIView):
    authentication_classes = (SocialAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        msg = 'You have access!'
        return Response(msg)


class PublicView(APIView):

    def get(self, request, format=None):
        return Response('Public view without login')