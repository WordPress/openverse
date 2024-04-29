import logging

from django.conf import settings
from django.contrib import admin
from django.urls import reverse

from elasticsearch import NotFoundError
from elasticsearch_dsl import Search

from api.models import PENDING


class MediaReportAdmin(admin.ModelAdmin):
    change_form_template = "admin/api/media_report/change_form.html"
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

    def get_other_reports(self, obj):
        if not self.media_type or not obj:
            return []

        reports = (
            self.model.objects.filter(media_obj__identifier=obj.media_obj.identifier)
            .exclude(id=obj.id)
            .order_by("created_at")
        )
        return reports

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
        ]

    def _get_media_obj_data(self, obj):
        additional_data = {
            "other_reports": self.get_other_reports(obj),
            "identifier": obj.media_obj.identifier,
            "foreign_landing_url": obj.media_obj.foreign_landing_url,
            "description": obj.media_obj.meta_data.get("description", ""),
            "title": obj.media_obj.title,
            "provider": obj.media_obj.provider,
            "source": obj.media_obj.source,
            "creator": obj.media_obj.creator or obj.media_obj.creator_url,
            "creator_url": obj.media_obj.creator_url,
            "url": obj.media_obj.url,
            "tags": {},
            "reverse_media_url": reverse(
                f"admin:api_{self.media_type}_change", args=[obj.media_obj.identifier]
            ),
        }

        if obj.media_obj.tags:
            tags_by_provider = {}
            for tag in obj.media_obj.tags:
                tags_by_provider.setdefault(tag["provider"], []).append(tag["name"])
            additional_data["tags"] = tags_by_provider
        return additional_data

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["media_type"] = self.media_type

        obj = self.get_object(request, object_id)
        if obj and obj.media_obj:
            additional_data = self._get_media_obj_data(obj)
            extra_context = {**extra_context, **additional_data}

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        context.update(
            {
                "add": add,
                "change": change,
            }
        )
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        readonly_fields = [
            "created_at",
            "reason",
            "description",
            "has_sensitive_text",
            "media_obj_id",
        ]
        # ``status`` cannot be changed on a finalised report.
        if obj.status != PENDING:
            readonly_fields.append("status")
        return readonly_fields


class ImageReportAdmin(MediaReportAdmin):
    media_type = "image"


class AudioReportAdmin(MediaReportAdmin):
    media_type = "audio"


class MediaSubreportAdmin(admin.ModelAdmin):
    exclude = ("media_obj",)
    search_fields = ("media_obj__identifier",)
    readonly_fields = ("media_obj_id",)

    def has_add_permission(self, *args, **kwargs):
        """Create ``_Report`` instances instead."""
        return False
