from rest_framework.generics import get_object_or_404

from asgiref.sync import sync_to_async


aget_object_or_404 = sync_to_async(get_object_or_404)
