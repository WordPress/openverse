from rest_framework.routers import SimpleRouter

from api.views.audio_views import AudioViewSet
from api.views.image_views import ImageViewSet


router = SimpleRouter(use_regex_path=False)
router.register("audio", AudioViewSet, basename="audio")
router.register("images", ImageViewSet, basename="image")

urlpatterns = router.urls
