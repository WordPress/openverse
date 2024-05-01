from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, F, Min
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import structlog
from elasticsearch import NotFoundError
from elasticsearch_dsl import Search
from openverse_attribution.license import License

from api.models import PENDING


logger = structlog.get_logger(__name__)


class PredeterminedOrderChangelist(ChangeList):
    """
    ChangeList class which does not apply any default ordering to the items.

    This is necessary or lists where the ordering is done on an annotated field, since
    the changelist attempts to apply the ordering to a QuerySet which is not aware that
    it has the annotated field available (and thus raises a FieldError).

    The caveat to this is that the ordering *must* be applied in
    ModelAdmin::get_queryset
    """

    def _get_default_ordering(self):
        return []


class PendingRecordCountFilter(admin.SimpleListFilter):
    title = "pending record count"
    parameter_name = "pending_record_count"

    def lookups(self, request, model_admin):
        return (("pending", "Pending"),)

    def queryset(self, request, queryset):
        value = self.value()
        if value == "pending":
            return queryset.filter(pending_report_count__gt=0)

        return queryset


class MediaListAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "total_report_count",
        "pending_report_count",
        "oldest_report_date",
        "pending_reports_links",
    )
    list_filter = (PendingRecordCountFilter,)
    # Disable link display for images
    list_display_links = None
    # Allow autocomplete to work from other referenced fields
    search_fields = ("identifier",)
    media_type = None
    # Ordering is not set here, see get_queryset

    def total_report_count(self, obj):
        return obj.total_report_count

    def pending_report_count(self, obj):
        return obj.pending_report_count

    def oldest_report_date(self, obj):
        return obj.oldest_report_date

    def pending_reports_links(self, obj):
        pending_reports = obj.media_reports.filter(decision__isnull=True)
        data = []
        for report in pending_reports.all():
            url = reverse(
                f"admin:api_{self.media_type}report_change", args=(report.id,)
            )
            data.append(format_html('<a href="{}">Report {}</a>', url, report.id))
        return mark_safe(", ".join(data))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Return all available image if this is for an autocomplete request
        if "autocomplete" in request.path:
            return qs
        # Filter down to only instances with reports
        qs = qs.filter(media_reports__isnull=False)
        # Annotate and order by report count
        qs = qs.annotate(total_report_count=Count("media_reports"))
        # Show total pending reports by subtracting the number of reports
        # from the number of reports that have decisions
        qs = qs.annotate(
            pending_report_count=F("total_report_count")
            - Count("media_reports__decision__pk")
        )
        qs = qs.annotate(oldest_report_date=Min("media_reports__created_at"))
        qs = qs.order_by(
            "-total_report_count", "-pending_report_count", "oldest_report_date"
        )
        return qs

    def get_changelist(self, request, **kwargs):
        return PredeterminedOrderChangelist


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

    def get_exclude(self, request, obj=None):
        # ``identifier`` cannot be edited on an existing report.
        if request.path.endswith("/change/"):
            return ["media_obj"]

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
            logger.error(f"Could not resolve index {filtered_index}")
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

    def _get_media_obj_data(self, obj):
        tags_by_provider = {}
        if obj.media_obj.tags:
            for tag in obj.media_obj.tags:
                tags_by_provider.setdefault(tag["provider"], []).append(tag["name"])
        additional_data = {
            "other_reports": self.get_other_reports(obj),
            "media_obj": obj.media_obj,
            "license": License(
                obj.media_obj.license,
                obj.media_obj.license_version,
            ).full_name,
            "tags": tags_by_provider,
            "description": obj.media_obj.meta_data.get("description", ""),
        }
        logger.info(f"Additional data: {additional_data}")
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
        context.update({"add": add, "change": change})
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )


class ImageReportAdmin(MediaReportAdmin):
    media_type = "image"


class AudioReportAdmin(MediaReportAdmin):
    media_type = "audio"


class ImageListViewAdmin(MediaListAdmin):
    media_type = "image"


class AudioListViewAdmin(MediaListAdmin):
    media_type = "audio"


class MediaSubreportAdmin(admin.ModelAdmin):
    exclude = ("media_obj",)
    search_fields = ("media_obj__identifier",)
    readonly_fields = ("media_obj_id",)

    def has_add_permission(self, *args, **kwargs):
        """Create ``_Report`` instances instead."""
        return False
