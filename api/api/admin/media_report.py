from functools import update_wrapper
from typing import Sequence

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, F, Min
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import structlog
from elasticsearch import NotFoundError
from elasticsearch_dsl import Search
from openverse_attribution.license import License

from api.models import PENDING
from api.utils.moderation_lock import LockManager


logger = structlog.get_logger(__name__)


def _production_deferred(*values: str) -> Sequence[str]:
    """
    Define a sequence in all environment except production.

    The autocomplete/search queries in Django are woefully unoptimized for massive
    tables, and so enabling certain utility features in production will often incur
    a significant performance hit or outage. This will return the input values except
    when the environment is production, in which case it will return an empty sequence.
    """
    if settings.ENVIRONMENT == "production":
        return ()
    return values


class PredeterminedOrderChangelist(ChangeList):
    """
    ChangeList class which does not apply any default ordering to the items.

    This is necessary for lists where the ordering is done on an annotated field, since
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

    def choices(self, changelist):
        """Set default to "pending" rather than "all"."""
        choices = list(super().choices(changelist))
        choices[0]["display"] = "Pending"
        return choices

    def lookups(self, request, model_admin):
        return (("all", "All"),)

    def queryset(self, request, queryset):
        value = self.value()
        if value != "all":
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
    search_fields = _production_deferred("identifier")
    media_type = None
    # Ordering is not set here, see get_queryset

    def total_report_count(self, obj):
        return obj.total_report_count

    def pending_report_count(self, obj):
        return obj.pending_report_count

    def oldest_report_date(self, obj):
        return obj.oldest_report_date

    def pending_reports_links(self, obj):
        reports = getattr(obj, f"{self.media_type}_report")
        pending_reports = reports.filter(decision__isnull=True)
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
        qs = qs.filter(**{f"{self.media_type}_report__isnull": False})
        # Annotate and order by report count
        qs = qs.annotate(total_report_count=Count(f"{self.media_type}_report"))
        # Show total pending reports by subtracting the number of reports
        # from the number of reports that have decisions
        qs = qs.annotate(
            pending_report_count=F("total_report_count")
            - Count(f"{self.media_type}_report__decision__pk")
        )
        qs = qs.annotate(
            oldest_report_date=Min(f"{self.media_type}_report__created_at")
        )
        qs = qs.order_by(
            "-total_report_count", "-pending_report_count", "oldest_report_date"
        )
        return qs

    def get_changelist(self, request, **kwargs):
        return PredeterminedOrderChangelist


class MediaReportAdmin(admin.ModelAdmin):
    change_list_template = "admin/api/media_report/change_list.html"
    change_form_template = "admin/api/media_report/change_form.html"
    list_display = ("id", "reason", "is_pending", "description", "created_at", "url")
    list_filter = (
        ("decision", admin.EmptyFieldListFilter),  # ~status, i.e. pending or moderated
        "reason",
    )
    list_display_links = ("id",)
    list_select_related = ("media_obj",)
    search_fields = _production_deferred("description", "media_obj__identifier")
    autocomplete_fields = _production_deferred("media_obj")
    actions = None
    media_type = None

    def __init__(self, *args, **kwargs):
        self.lock_manager = LockManager(self.media_type)
        super().__init__(*args, **kwargs)

    def get_urls(self):
        # Code partially copied from django/contrib/admin/options.py

        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.opts.app_label, self.opts.model_name

        urls = super().get_urls()
        urls.insert(
            -1,
            path(
                "<path:object_id>/lock/",
                wrap(self.soft_lock_view),
                name="{:s}_{:s}_lock".format(*info),
            ),
        )
        return urls

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

    def soft_lock_view(self, request, object_id):
        """
        Soft-lock the provided report to the current user.

        This view is polled from the frontend when a user has the report
        change page open. Not polling this endpoint will automatically
        release the lock when it expires.

        The endpoint returns the lock expiration timestamp.

        :param request: the incoming request to soft-lock the report
        :param object_id: the ID of the report to soft-lock
        """

        expiration = self.lock_manager.add_locks(request.user.get_username(), object_id)
        return JsonResponse(
            data={"expiration": expiration},
            status=503 if expiration == 0 else 200,
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        mods = self.lock_manager.moderator_set(object_id)
        mods -= {request.user.get_username()}
        if len(mods):
            messages.warning(
                request,
                f"Other moderator(s) looking at this report: {', '.join(mods)}.",
            )

        extra_context = extra_context or {}
        extra_context["media_type"] = self.media_type

        obj = self.get_object(request, object_id)
        if obj and obj.media_obj:
            additional_data = self._get_media_obj_data(obj)
            extra_context |= additional_data

        return super().change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        valid_locks = self.lock_manager.prune()
        locked_reports = list(
            int(item.replace(f"{self.media_type}:", ""))
            for lock_set in valid_locks.values()
            for item in lock_set
        )

        extra_context = extra_context or {}
        extra_context |= {"locked_reports": locked_reports}

        return super().changelist_view(request, extra_context)

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
