from cccatalog.api.serializers.list_serializers import ImageListSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.throttling import AnonRateThrottle


class ListThrottler(AnonRateThrottle):
    rate = '30/day'


class List(CreateAPIView):
    """
    Create a list of images.
    """
    throttle_classes = (ListThrottler,)
    serializer_class = ImageListSerializer
