from django.urls import path

from catalog.api.views.image_views import (
    SearchImages,
    ImageDetail,
    RelatedImage,
    ImageStats,
    ReportImageView,
    ProxiedImage,
    OembedView,
)

urlpatterns = [
    path(
        'stats',
        ImageStats.as_view(),
        name='image-stats'
    ),
    path(
        'oembed',
        OembedView.as_view(),
        name='image-oembed'
    ),
    path(
        '<str:identifier>',
        ImageDetail.as_view(),
        name='image-detail'
    ),
    path(
        '<str:identifier>/thumb',
        ProxiedImage.as_view(),
        name='image-thumb'
    ),
    path(
        '<str:identifier>/recommendations',
        RelatedImage.as_view(),
        name='image-related'
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
