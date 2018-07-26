from cccatalog.api.serializers.list_serializers import ImageListSerializer
from cccatalog.api.models import ImageList
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import throttle_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


class ListCreateThrottler(UserRateThrottle):
    rate = '30/day'


class _List(GenericAPIView):
    serializer_class = ImageListSerializer
    queryset = ImageList.objects.all()
    lookup_field = 'id'


class CreateList(_List):

    class _CreateResponse(serializers.Serializer):
        url = serializers.HyperlinkedRelatedField(
            view_name='list-detail',
            read_only=True,
            help_text="The URL of the new list."
        )

    @swagger_auto_schema(operation_id="list_create",
                         responses={
                             201: _CreateResponse,
                             400: "Bad Request"
                         })
    @throttle_classes([ListCreateThrottler])
    def post(self, request, format=None):
        """
        Create a public collection of images. Returns the ID of the newly
        created list.

        To prevent abuse, only up to 30 lists can be made by a single user per
        day, and lists can only contain up to 500 items. Additionally, all
        input primary keys must be valid. If any of these constraints are
        violated, a validation error is returned.
        """
        serialized = ImageListSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(
                status=400,
                data=serialized.errors
            )

        list_id = serialized.save()
        url = request.build_absolute_uri(reverse('list-detail', [list_id]))
        return Response(
            status=200,
            data={
                'url': url
            }
        )


class DetailList(_List, RetrieveModelMixin):
    @swagger_auto_schema(operation_id="list_detail",
                         responses={
                             200: ImageListSerializer,
                             404: 'Not Found'
                         })
    def get(self, request, id, format=None):
        """ Get the details of a single list. """
        return self.retrieve(request, id)
