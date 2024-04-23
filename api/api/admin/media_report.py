import logging

from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from elasticsearch import NotFoundError
from elasticsearch_dsl import Search

from api.models import PENDING


def create_link(url: str, text: str):
    return mark_safe(f'<a href="{url}">{text}</a>')


class MediaReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reason", "is_pending", "description", "created_at", "url")
    list_filter = (
        ("decision", admin.EmptyFieldListFilter),  # ~status, i.e. pending or moderated
        "reason",
    )
    list_display_links = ("id",)
    list_select_related = ("media_obj",)
    search_fields = ("description", "media_obj__identifier")
    autocomplete_fields = ("media_obj",)
    actions = None
    media_type = None

    @admin.display(description="Has sensitive text")
    def has_sensitive_text(self, obj):
        """
        Return `True` if the item cannot be found in the filtered index - which means the item
        was filtered out due to text sensitivity.
        """
        if not self.media_type or not obj:
            return None

        filtered_index = f"{settings.MEDIA_INDEX_MAPPING[self.media_type]}-filtered"
        try:
            search = (
                Search(index=filtered_index)
                .query("term", identifier=obj.media_obj.identifier)
                .execute()
            )
            if search.hits:
                return False
        except NotFoundError:
            logging.error(f"Could not resolve index {filtered_index}")
            return None
        return True

    @admin.display(description="Title and creator")
    def title(self, obj):
        title = obj.media_obj.title or "Unnamed media"

        if not (obj.media_obj.creator or obj.media_obj.creator_url):
            return title

        if obj.media_obj.creator and obj.media_obj.creator_url:
            return mark_safe(
                f"{title} by {create_link(obj.media_obj.creator_url, obj.media_obj.creator)}"
            )
        else:
            creator = obj.media_obj.creator or obj.media_obj.creator_url
            creator_string = f" by {creator}" if creator else ""
            return f"{title}{creator_string}"

    def media_display(self, obj):
        pass

    @admin.display(description="Media description")
    def media_description(self, obj):
        return obj.media_obj.meta_data.get("description")

    @admin.display(description="Tags")
    def tags(self, obj):
        """Display tag names grouped by provider."""
        if not obj.media_obj.tags:
            return ""
        tags_by_provider = {}
        for tag in obj.media_obj.tags:
            tags_by_provider.setdefault(tag["provider"], []).append(tag["name"])
        return mark_safe(
            "".join(
                f"<p><strong>{provider}</strong>: {', '.join(names)}</p>"
                for provider, names in tags_by_provider.items()
            )
        )

    @admin.display(description="From")
    def from_field(self, obj):
        return f"provider: {obj.media_obj.provider}, source: {obj.media_obj.source}"

    @admin.display(description="URLs")
    def landing_urls(self, obj):
        if not self.media_type or not obj:
            return "N/A"
        openverse_url = (
            f"https://openverse.org/{self.media_type}/{obj.media_obj.identifier}"
        )
        return mark_safe(
            f"<p>{create_link(obj.media_obj.foreign_landing_url, obj.media_obj.provider)}, "
            f'{create_link(openverse_url, "openverse.org")}'
        )

    @admin.display(description="Other reports")
    def other_reports(self, obj):
        """
        Display a table of other reports for the same media object.
        Cannot use the ``TabularInline`` class because it requires a Parent -> Child relationship.
        """
        if not self.media_type or not obj:
            return ""
        reports = (
            self.model.objects.filter(media_obj__identifier=obj.media_obj.identifier)
            .exclude(id=obj.id)
            .order_by("created_at")
        )
        logging.info(
            f"Found {reports.count()} other reports for {obj.media_obj.identifier}"
        )
        for report in reports:
            logging.info(
                f"Report {report.id} created at {report.created_at} for {report.media_obj.identifier}"
            )
        if not reports:
            return ""
        result = "<table><thead><tr><th>Date</th><th>Report reason</th><th>Status</th><th>Report link</th></tr></thead><tbody>"
        for report in reports:
            report_link_html = f'<a href="{reverse("admin:api_imagereport_change", args=[report.id])}">{report.id}</a>'
            created_at = report.created_at.strftime("%Y-%m-%d %H:%M:%S")
            report_row = f"<tr><td>{created_at}</td><td>{report.reason}</td><td>{report.status}</td><td>{report_link_html}</td></tr>"
            result += report_row
        result += "</tbody></table>"
        return mark_safe(result)

    def get_exclude(self, request, obj=None):
        # ``identifier`` cannot be edited on an existing report.
        if request.path.endswith("/change/"):
            return ["media_obj"]

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [
                (
                    "Report details",
                    {"fields": ["status", "decision", "reason", "description"]},
                ),
                ("Media details", {"fields": ["media_obj"]}),
            ]
        return [
            (
                "Report details",
                {
                    "fields": [
                        "created_at",
                        "status",
                        "decision",
                        "reason",
                        "description",
                        "has_sensitive_text",
                    ],
                },
            ),
            (
                "Media details",
                {
                    "fields": [
                        "media_display",
                        "title",
                        "tags",
                        "media_description",
                        "from_field",
                        "landing_urls",
                        "media_obj_id",
                    ]
                },
            ),
            ("Other reports", {"fields": ["other_reports"]}),
        ]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        readonly_fields = [
            "created_at",
            "reason",
            "description",
            "has_sensitive_text",
            "media_display",
            "title",
            "tags",
            "media_description",
            "from_field",
            "landing_urls",
            "media_obj_id",
            "other_reports",
        ]
        # ``status`` cannot be changed on a finalised report.
        if obj.status != PENDING:
            readonly_fields.append("status")
        return readonly_fields


class ImageReportAdmin(MediaReportAdmin):
    change_form_template = "admin/api/imagereport/change_form.html"
    media_type = "image"

    @admin.display(description="Image")
    def media_display(self, obj):
        """
        Display a blurred image with a clickable overlay.
        Use the image thumbnail if available, else replace with the direct image url.
        """
        if obj.media_obj.url:
            thumb_url = f"https://api.openverse.engineering{obj.media_url()}thumb/"
            return mark_safe(
                f'<div class="container"><img src="{thumb_url}" alt="Media Image" class="blur-image" height="300" '
                f'onclick="toggleBlur(this)" onerror="replace(this, \'{obj.media_obj.url}\')" style="cursor: pointer;" />'
                f"<p> Show content </p></div>"
            )
        return "No Image Available"


class AudioReportAdmin(MediaReportAdmin):
    media_type = "audio"

    @admin.display(description="Audio")
    def media_display(self, obj):
        if obj.media_obj.url:
            return mark_safe(
                f'<audio controls><source src="{obj.media_obj.url}" type="audio/mpeg">'
                f"Your browser does not support the audio element.</audio>"
            )
        return "No Audio Available"


class MediaSubreportAdmin(admin.ModelAdmin):
    exclude = ("media_obj",)
    search_fields = ("media_obj__identifier",)
    readonly_fields = ("media_obj_id",)

    def has_add_permission(self, *args, **kwargs):
        """Create ``_Report`` instances instead."""
        return False
