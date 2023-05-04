from django.urls import path, re_path
from django.views.generic import RedirectView

from api.utils.status_code_view import get_status_code_view


discontinuation_message = {
    "error": "Gone",
    "reason": "This API endpoint has been discontinued.",
}

mappings = [
    ("sources", "image-stats", "about-image"),
    ("recommendations/images/<str:identifier>", "image-related", "related-images"),
    ("oembed", "image-oembed", "oembed"),
    ("thumbs/<str:identifier>", "image-thumb", "thumbs"),
]

urlpatterns = [
    path(
        source,
        RedirectView.as_view(
            pattern_name=dest, permanent=True, query_string=(source == "oembed")
        ),
        name=name,
    )
    for source, dest, name in mappings
] + [
    # Discontinued, return 410 Gone
    re_path(
        r"^link/",
        get_status_code_view(discontinuation_message, 410).as_view(),
        name="make-link",
    ),
]
