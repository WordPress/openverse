from django.urls import path

from catalog.api.views.audio_views import (
    SearchAudio,
    AudioDetail,
    RelatedAudio,
    AudioStats,
    AudioArt,
)

urlpatterns = [
    path(
        'stats',
        AudioStats.as_view(),
        name='audio-stats'
    ),
    path(
        '<str:identifier>',
        AudioDetail.as_view(),
        name='audio-detail'
    ),
    path(
        '<str:identifier>/thumb',
        AudioArt.as_view(),
        name='audio-thumb'
    ),
    path(
        '<str:identifier>/recommendations',
        RelatedAudio.as_view(),
        name='audio-related'
    ),
    path(
        '',
        SearchAudio.as_view(),
        name='audio'
    ),
]
