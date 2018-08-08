from cccatalog.api.serializers.list_serializers import\
    ImageListCreateSerializer, ImageListResponseSerializer
from django.forms.models import model_to_dict
from cccatalog.api.models import ImageList
from cccatalog.api.utils.throttle import PostRequestThrottler
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import throttle_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


class _List(GenericAPIView):
    serializer_class = ImageListCreateSerializer
    queryset = ImageList.objects.all()
    lookup_field = 'id'


class _CreateResponse(serializers.Serializer):
    url = serializers.HyperlinkedRelatedField(
        view_name='list-detail',
        read_only=True,
        help_text="The URL of the new list."
    )


class CreateList(_List):

    @swagger_auto_schema(operation_id="list_create",
                         responses={
                             201: _CreateResponse,
                             400: "Bad Request"
                         })
    @throttle_classes([PostRequestThrottler])
    def post(self, request, format=None):
        """
        Create a public collection of images. Returns the ID of the newly
        created list.

        To prevent abuse, only up to 30 lists can be made by a single user per
        day, and lists can only contain up to 500 items. Additionally, all
        input primary keys must be valid. If any of these constraints are
        violated, a validation error is returned.
        """
        serialized = ImageListCreateSerializer(data=request.data)
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


class ListDetail(_List, RetrieveModelMixin):
    @swagger_auto_schema(operation_id="list_detail",
                         responses={
                             200: ImageListResponseSerializer,
                             404: 'Not Found'
                         })
    def get(self, request, slug, format=None):
        """ Get the details of a single list. """
        _list = ImageList.objects.get(slug=slug)
        resolved = {
            'id': slug,
            'images': [model_to_dict(x) for x in _list.images.all()]
        }
        serialized = ImageListResponseSerializer(data=resolved)
        return Response(status=200, data=serialized.initial_data)
