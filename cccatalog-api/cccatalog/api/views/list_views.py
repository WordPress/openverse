import json
from cccatalog.api.serializers.list_serializers import ImageListSerializer
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response


class ListThrottler(UserRateThrottle):
    rate = '30/day'


class List(APIView):
    """
    Create a public collection of images. Return the ID of the list.

    To prevent abuse, only up to 30 lists can be made by a single user per day,
    and lists can only have up to 500 items.
    """
    throttle_classes = (ListThrottler,)
    serializer_class = ImageListSerializer

    def post(self, request, format=None):
        serialized = ImageListSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(
                status=400,
                data=serialized.errors
            )

        list_id = serialized.save()
        return Response(
            status=200,
            data={
                'id': list_id
            }
        )