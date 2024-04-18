from api.examples.audio_requests import (
    audio_complain_curl,
    audio_detail_curl,
    audio_related_curl,
    audio_search_curl,
    audio_search_list_curl,
    audio_stats_curl,
    audio_waveform_curl,
)
from api.examples.audio_responses import (
    audio_complain_201_example,
    audio_detail_200_example,
    audio_detail_404_example,
    audio_related_200_example,
    audio_related_404_example,
    audio_search_200_example,
    audio_search_400_example,
    audio_stats_200_example,
    audio_waveform_200_example,
    audio_waveform_404_example,
)
from api.examples.image_requests import (
    image_complain_curl,
    image_detail_curl,
    image_oembed_curl,
    image_related_curl,
    image_search_curl,
    image_search_list_curl,
    image_stats_curl,
)
from api.examples.image_responses import (
    image_complain_201_example,
    image_detail_200_example,
    image_detail_404_example,
    image_oembed_200_example,
    image_oembed_404_example,
    image_related_200_example,
    image_related_404_example,
    image_search_200_example,
    image_search_400_example,
    image_stats_200_example,
)
from api.examples.oauth2_requests import (
    auth_key_info_curl,
    auth_register_curl,
    auth_token_curl,
)
from api.examples.oauth2_responses import (
    auth_key_info_200_example,
    auth_register_201_example,
    auth_token_200_example,
)


audio_mappings = {
    audio_search_curl: audio_search_200_example,
    audio_stats_curl: audio_stats_200_example,
    audio_detail_curl: audio_detail_200_example,
    audio_complain_curl: audio_complain_201_example,
}
image_mappings = {
    image_search_curl: image_search_200_example,
    image_stats_curl: image_stats_200_example,
    image_detail_curl: image_detail_200_example,
    image_complain_curl: image_complain_201_example,
    image_oembed_curl: image_oembed_200_example,
}
