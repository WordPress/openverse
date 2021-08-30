from django.urls import path

from catalog.api.views.audio_views import (
    SearchAudio,
    AudioDetail,
    RelatedAudio,
    AudioStats,
    AudioArt,
    AudioWaveform,
)

urlpatterns = [
    path(
        'stats',
        AudioStats.as_view(),
        name='audio-stats'
    ),
    path(
        '<uuid:identifier>',
        AudioDetail.as_view(),
        name='audio-detail'
    ),
    path(
        '<uuid:identifier>/thumb',
        AudioArt.as_view(),
        name='audio-thumb'
    ),
    path(
        '<uuid:identifier>/recommendations',
        RelatedAudio.as_view(),
        name='audio-related'
    ),
    path(
        '<uuid:identifier>/waveform',
        AudioWaveform.as_view(),
        name='audio-waveform'
    ),
    path(
        '',
        SearchAudio.as_view(),
        name='audio'
    ),
]
