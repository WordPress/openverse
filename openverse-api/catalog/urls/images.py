from django.urls import path

from catalog.api.views.image_views import (
    SearchImages,
    ImageDetail,
    RelatedImage,
    ImageStats,
    ReportImageView,
)

urlpatterns = [
    path(
        'stats',
        ImageStats.as_view(),
        name='image-stats'
    ),
    path(
        'recommendations/<str:identifier>',
        RelatedImage.as_view(),
        name='image-related'
    ),
    path(
        '<str:identifier>',
        ImageDetail.as_view(),
        name='image-detail'
    ),
    path(
        '<str:identifier>/report',
        ReportImageView.as_view(),
        name='report-image'
    ),
    path(
        '',
        SearchImages.as_view(),
        name='images'
    ),
]
