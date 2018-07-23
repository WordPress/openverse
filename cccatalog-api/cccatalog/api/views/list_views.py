from cccatalog.api.serializers.list_serializers import ImageListSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.throttling import UserRateThrottle


class ListThrottler(UserRateThrottle):
    rate = '30/day'


class List(CreateAPIView):
    """
    Create a public collection of images.

    To prevent abuse, only up to 30 lists can be made by a single user per day,
    and lists can only have up to 500 items.
    """
    throttle_classes = (ListThrottler,)
    serializer_class = ImageListSerializer
