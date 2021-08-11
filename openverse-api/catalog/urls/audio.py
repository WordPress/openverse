from django.urls import path

from catalog.api.views.audio_views import (
    SearchAudio,
    AudioDetail,
    RelatedAudio,
    AudioStats,
)

urlpatterns = [
    path(
        'stats',
        AudioStats.as_view(),
        name='audio-stats'
    ),
    path(
        'recommendations/<str:identifier>',
        RelatedAudio.as_view(),
        name='related-audio'
    ),
    path(
        '<str:identifier>',
        AudioDetail.as_view(),
        name='audio-detail'
    ),
    path(
        '',
        SearchAudio.as_view(),
        name='audio'
    ),
]
