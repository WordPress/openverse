"""
This file hardcodes the logical order for serializer fields.

This leads to the JSON output being more suitable for human consumption.
"""

json_fields = [
    "id",
    "title",
    "foreign_landing_url",
    "url",
    "creator",
    "creator_url",
    "license",
    "license_version",
    "license_url",
    "provider",
    "source",
    "category",
    "genres",  # audio-only
    "filesize",
    "filetype",
    "tags",
    "alt_files",  # audio-only
    "attribution",
    # Hits
    "fields_matched",
    "mature",
    # Image specific
    "height",
    "width",
    # Audio specific
    "audio_set",
    "duration",
    "bit_rate",
    "sample_rate",
    # Hyperlinks
    "thumbnail",
    "detail_url",
    "related_url",
    "waveform",  # audio-only
    # Add-ons
    "peaks",  # audio-only
]

field_position_map: dict[str, int] = {
    field: idx for idx, field in enumerate(json_fields)
}
#: mapping of JSON fields to their sort positions
