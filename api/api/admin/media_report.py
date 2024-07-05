from functools import update_wrapper
from typing import Sequence

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, F, Min
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import structlog
from elasticsearch import NotFoundError
from elasticsearch_dsl import Search

from api.constants.moderation import DecisionAction
from api.models import (
    Audio,
    AudioDecision,
    AudioDecisionThrough,
    AudioReport,
    Image,
    ImageDecision,
    ImageDecisionThrough,
    ImageReport,
)
from api.models.media import AbstractDeletedMedia, AbstractSensitiveMedia
from api.utils.moderation_lock import LockManager


logger = structlog.get_logger(__name__)


def register(site):
    site.register(Image, ImageListViewAdmin)
    site.register(Audio, AudioListViewAdmin)

    site.register(AudioReport, AudioReportAdmin)
    site.register(ImageReport, ImageReportAdmin)

    for klass in [
        *AbstractSensitiveMedia.__subclasses__(),
        *AbstractDeletedMedia.__subclasses__(),
    ]:
        site.register(klass, MediaSubreportAdmin)

    site.register(ImageDecision, ImageDecisionAdmin)
    site.register(AudioDecision, AudioDecisionAdmin)


def get_report_form(media_type: str):
    report_class = {
        "image": ImageReport,
        "audio": AudioReport,
    }[media_type]

    class MediaReportForm(forms.ModelForm):
        class Meta:
            fields = ["media_obj", "reason", "description"]
            model = report_class

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs.update({"form": "report-create"})

    return MediaReportForm


class MultipleValueField(forms.MultipleChoiceField):
    """
    This is a variant of ``MultipleChoiceField`` that does not validate
    the individual values.
    """

    def valid_value(self, value):
        return True


def get_decision_form(media_type: str):
    decision_class, report_class = {
        "image": (ImageDecision, ImageReport),
        "audio": (AudioDecision, AudioReport),
    }[media_type]

    class MediaDecisionForm(forms.ModelForm):
        report_id = MultipleValueField()  # not rendered using its widget

        class Meta:
            model = decision_class
            fields = ["action", "notes"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs.update({"form": "decision-create"})

        def clean_report_id(self):
            report_ids = set(self.cleaned_data["report_id"])
            report_qs = report_class.objects.filter(
                decision=None,
                id__in=report_ids,
            )
            retrieved_report_ids = set(
                str(val) for val in report_qs.values_list("id", flat=True)
            )
            if diff := (report_ids - retrieved_report_ids):
                raise forms.ValidationError(
                    "No pending reports found for IDs %(value)s.",
                    params={"value": ", ".join(diff)},
                )
            self.cleaned_data["reports"] = report_qs
            return report_ids

    return MediaDecisionForm


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


def _non_production_deferred(*values: str) -> Sequence[str]:
    """
    Define a sequence in only the production environment.

    The raw ID field is perfectly suited for massive tables, and so enabling
    that in production will often prevent performance hits or outages. This will
    return the input values only the environment is production, and in all other
    cases it will return an empty sequence.
    """
    if settings.ENVIRONMENT != "production":
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


def get_pending_record_filter(media_type: str):
    class PendingRecordCountFilter(admin.SimpleListFilter):
        title = "pending record count"
        parameter_name = "pending_record_count"

        def choices(self, changelist):
            for lookup, title in self.lookup_choices:
                yield {
                    "selected": self.value() == lookup,
                    "query_string": changelist.get_query_string(
                        {self.parameter_name: lookup}, []
                    ),
                    "display": title,
                }

        def lookups(self, request, model_admin):
            return [
                (None, "Moderation queue"),
                ("all", "All"),
            ]

        def queryset(self, request, qs):
            value = self.value()
            if value is None:
                # Filter down to only instances with reports
                qs = qs.filter(**{f"{media_type}_report__isnull": False})

                # Annotate and order by report count
                qs = qs.annotate(total_report_count=Count(f"{media_type}_report"))
                # Show total pending reports by subtracting the number of reports
                # from the number of reports that have decisions
                qs = qs.annotate(
                    pending_report_count=F("total_report_count")
                    - Count(f"{media_type}_report__decision__pk")
                )
                qs = qs.annotate(
                    oldest_report_date=Min(f"{media_type}_report__created_at")
                )
                qs = qs.order_by(
                    "-total_report_count", "-pending_report_count", "oldest_report_date"
                )

            return qs

    return PendingRecordCountFilter


class MediaListAdmin(admin.ModelAdmin):
    media_type = None

    def __init__(self, *args, **kwargs):
        self.lock_manager = LockManager(self.media_type)

        super().__init__(*args, **kwargs)

    def get_urls(self):
        # Start of block lifted from Django source.
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        app, model = self.opts.app_label, self.opts.model_name
        # End of block lifted from Django source.

        urls = super().get_urls()

        # Using slice assignment (docs:
        # https://docs.python.org/3/tutorial/introduction.html#lists),
        # insert custom URLs at the penultimate position so that they
        # appear just before the catch-all view.
        urls[-1:-1] = [
            path(
                "<path:object_id>/report_create/",
                wrap(self.report_create_view),
                name=f"{app}_{model}_report_create",
            ),
            path(
                "<path:object_id>/decision_create/",
                wrap(self.decision_create_view),
                name=f"{app}_{model}_decision_create",
            ),
            path(
                "<path:object_id>/lock/",
                wrap(self.lock_view),
                name=f"{app}_{model}_lock",
            ),
        ]
        return urls

    @admin.display(description="Has sensitive text?", boolean=True)
    def has_sensitive_text(self, obj):
        """
        Determine if the item has sensitive text.

        If the item cannot be found in the filtered index, that means it
        was filtered out due to text sensitivity.

        This is displayed both as a column in the list page as well as a
        read-only field in the change page.

        :param obj: the item to check for presence of sensitive text
        :return: whether the item has sensitive text
        """

        filtered_index = f"{settings.MEDIA_INDEX_MAPPING[self.media_type]}-filtered"
        try:
            search = (
                Search(index=filtered_index)
                .query("term", identifier=obj.identifier)
                .execute()
            )
            if search.hits:
                return False
        except NotFoundError:
            logger.error("Could not resolve index.", name=filtered_index)
        return True

    #############
    # List view #
    #############

    change_list_template = "admin/api/media/change_list.html"
    list_display = ("identifier",)
    list_display_links = ("identifier",)
    search_fields = _production_deferred("identifier")
    sortable_by = ()  # Ordering is defined in ``get_queryset``.

    def get_list_filter(self, request):
        return (get_pending_record_filter(self.media_type),)

    def get_list_display(self, request):
        if request.GET.get("pending_record_count") != "all":
            return self.list_display + (
                "total_report_count",
                "pending_report_count",
                "oldest_report_date",
                "pending_reports_links",
                "has_sensitive_text",
            )
        else:
            return self.list_display + (
                "source",
                "provider",
            )

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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context["media_type"] = self.media_type

        valid_locks = self.lock_manager.prune()
        locked_media = list(
            int(item.replace(f"{self.media_type}:", ""))
            for moderator, lock_set in valid_locks.items()
            for item in lock_set
            if self.media_type in item and moderator != request.user.get_username()
        )
        extra_context["locked_media"] = locked_media

        return super().changelist_view(request, extra_context)

    ###############
    # Change view #
    ###############

    change_form_template = "admin/api/media/change_form.html"
    readonly_fields = (
        "attribution",
        "license_url",
        "has_sensitive_text",
    )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Populate a warning message for locked items.
        mods = self.lock_manager.moderator_set(object_id)
        mods -= {request.user.get_username()}
        if len(mods):
            messages.warning(
                request,
                f"This {self.media_type} is also being viewed by {', '.join(mods)}.",
            )

        # Expand the context based on the template's needs.
        extra_context = extra_context or {}

        extra_context["media_type"] = self.media_type

        media_obj = self.get_object(request, object_id)
        if media_obj:
            extra_context["media_obj"] = media_obj
        else:
            messages.warning(request, f"No media object found with ID {object_id}.")
            return redirect(f"admin:api_{self.media_type}_changelist")

        tags_by_provider = {}
        if tags := media_obj.tags:
            for tag in tags:
                text = tag["name"]
                if acc := tag.get("accuracy"):
                    text = f"{text} ({acc})"
                tags_by_provider.setdefault(
                    tag.get("provider", "No provider"), []
                ).append(text)
        extra_context["tags"] = tags_by_provider

        manager = getattr(media_obj, f"{self.media_type}decisionthrough_set")
        decision_throughs = manager.order_by("decision__created_on")
        extra_context["decision_throughs"] = decision_throughs

        manager = getattr(media_obj, f"{self.media_type}_report")
        reports = manager.order_by("-created_at")
        extra_context["reports"] = reports

        pending_report_count = reports.filter(decision_id=None).count()
        extra_context["pending_report_count"] = pending_report_count

        extra_context["mod_form"] = get_decision_form(self.media_type)()

        extra_context["report_form"] = get_report_form(self.media_type)()

        return super().change_view(request, object_id, form_url, extra_context)

    #############
    # Lock view #
    #############

    def lock_view(self, request, object_id):
        """
        Softly lock the media object with the current user to notify
        other moderators about a potential conflict.
        """

        if request.method == "POST":
            expiration = self.lock_manager.add_locks(
                request.user.get_username(), object_id
            )
            return JsonResponse(
                data={"expiration": expiration},
                status=503 if expiration == 0 else 200,
            )

        return redirect(f"admin:api_{self.media_type}_change", object_id)

    ########################
    # Decision create view #
    ########################

    def decision_create_view(self, request, object_id):
        """
        Create a decision for the media object and associate selected
        reports referencing the media with this decision.
        """

        redir = redirect(f"admin:api_{self.media_type}_change", object_id)

        if request.method != "POST":
            return redir

        is_allowed = (
            request.user.is_superuser
            or request.user.groups.filter(name="Content Moderators").exists()
        )
        if not is_allowed:
            messages.error(
                request,
                "You do not have permission to create decisions.",
            )
            return redir

        media_obj = self.get_object(request, object_id)

        through_model = {
            "image": ImageDecisionThrough,
            "audio": AudioDecisionThrough,
        }[self.media_type]
        form = get_decision_form(self.media_type)(request.POST)
        if form.is_valid():
            decision = form.save(commit=False)
            decision.moderator = request.user
            decision.save()

            logger.info(
                "Decision created",
                decision=decision.id,
                action=decision.action,
                notes=decision.notes,
                moderator=request.user.get_username(),
            )

            through = through_model.objects.create(
                decision=decision,
                media_obj=media_obj,
            )
            logger.info(
                "Through model created",
                through=through.id,
                decision=decision.id,
                media_obj=media_obj.id,
            )

            reports = form.cleaned_data["reports"]
            count = reports.update(decision=decision)
            logger.info(
                "Decision recorded in reports",
                report_count=count,
                decision=decision.id,
            )

            if decision.action in {
                DecisionAction.DEINDEXED_COPYRIGHT,
                DecisionAction.DEINDEXED_SENSITIVE,
            }:
                messages.info(
                    request,
                    "The media object has been deindexed from ES and deleted from DB.",
                )
                return redirect(f"admin:api_{self.media_type}_changelist")

            if decision.action == DecisionAction.MARKED_SENSITIVE:
                messages.info(
                    request,
                    "The media object has been marked as sensitive.",
                )
        else:
            logger.warning(
                "Form is invalid",
                **form.cleaned_data,
                errors=form.errors,
            )

        return redir

    ######################
    # Report create view #
    ######################

    def report_create_view(self, request, object_id):
        """Create a report for the media object."""

        if request.method == "POST":
            media_obj = self.get_object(request, object_id)

            form = get_report_form(self.media_type)(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.media_obj = media_obj
                report.save()

                logger.info(
                    "Report created",
                    report=report.id,
                    reason=report.reason,
                    description=report.description,
                    media_obj=media_obj.id,
                )
            else:
                logger.warning(
                    "Form is invalid",
                    **form.cleaned_data,
                    errors=form.errors,
                )

        return redirect(f"admin:api_{self.media_type}_change", object_id)

    #############
    # Overrides #
    #############

    def get_changelist(self, request, **kwargs):
        return PredeterminedOrderChangelist


class MediaReportAdmin(admin.ModelAdmin):
    media_type = None

    @admin.display(description="Is pending?", boolean=True)
    def is_pending(self, obj):
        """
        Set an explicit display type for the ``is_pending`` property.

        This is required so that the property, which otherwise renders
        "True" or "False" strings, now renders as check/cross icons in
        Django Admin.
        """

        return obj.is_pending

    #############
    # List view #
    #############

    list_display = (
        "id",
        "created_at",
        "reason",
        "description",
        "is_pending",
        "media_id",  # used because ``media_obj`` does not render a link
    )
    list_filter = (
        "reason",
        ("decision", admin.EmptyFieldListFilter),  # ~is_pending
    )
    list_select_related = ("media_obj",)
    search_fields = ("description", *_production_deferred("media_obj__identifier"))

    @admin.display(description="Media obj")
    def media_id(self, obj):
        path = reverse(f"admin:api_{self.media_type}_change", args=(obj.media_obj.id,))
        return format_html(f'<a href="{path}">{obj.media_obj}</a>')

    ###############
    # Change view #
    ###############

    autocomplete_fields = ("decision", *_production_deferred("media_obj"))
    raw_id_fields = _non_production_deferred("media_obj")
    actions = None

    def get_readonly_fields(self, request, obj=None):
        if obj is None:  # Create form
            return ()
        # These fields only make sense after a report has been created.
        # Hence they are only shown in the change form.
        return (
            "created_at",
            "is_pending",
            "media_obj",
        )

    def get_exclude(self, request, obj=None):
        if obj is None:  # Create form
            # The decision will be linked to the report after it has
            # been created, not during.
            return ("decision",)
        else:  # Change form
            # In the change form, we do not want to allow the media
            # object to be changed.
            return ("media_obj",)


class MediaDecisionAdmin(admin.ModelAdmin):
    media_type = None
    through_model = None

    #############
    # List view #
    #############

    list_display = (
        "id",
        "created_on",
        "moderator",
        "action",
        "notes",
        "media_ids",
    )
    list_filter = ("moderator", "action")
    list_prefetch_related = ("media_objs",)
    search_fields = ("notes", *_production_deferred("media_objs__identifier"))

    @admin.display(description="Media objs")
    def media_ids(self, obj):
        through_objs = getattr(obj, f"{self.media_type}decisionthrough_set").all()
        text = []
        for obj in through_objs:
            path = reverse(
                f"admin:api_{self.media_type}_change", args=(obj.media_obj.id,)
            )
            text.append(f'• <a href="{path}">{obj.media_obj}</a>')
        return format_html("<br>".join(text))

    ###############
    # Change view #
    ###############

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        # These fields only make sense after a decision has been created.
        # Moderator is set automatically and cannot be changed.
        return (
            "created_on",
            "moderator",
        )

    def get_exclude(self, request, obj=None):
        if obj is None:  # Create form
            # Moderator is set automatically and cannot be changed.
            return ("moderator",)
        return ()

    def get_inlines(self, request, obj=None):
        if obj is None:
            # New decision, can make changes to the media objects.
            is_mutable = True
        else:
            # Once created, media objects associated with decisions are
            # immutable.
            is_mutable = False

        class MediaDecisionThroughAdmin(admin.TabularInline):
            model = self.through_model
            extra = 1
            autocomplete_fields = _production_deferred("media_obj")
            raw_id_fields = _non_production_deferred("media_obj")

            def has_add_permission(self, request, obj=None):
                return is_mutable and super().has_change_permission(request, obj)

            def has_change_permission(self, request, obj=None):
                return is_mutable and super().has_change_permission(request, obj)

            def has_delete_permission(self, request, obj=None):
                return is_mutable and super().has_delete_permission(request, obj)

        return (MediaDecisionThroughAdmin,)

    def save_model(self, request, obj, form, change):
        obj.moderator = request.user
        return super().save_model(request, obj, form, change)


class ImageReportAdmin(MediaReportAdmin):
    media_type = "image"


class AudioReportAdmin(MediaReportAdmin):
    media_type = "audio"


class ImageListViewAdmin(MediaListAdmin):
    media_type = "image"


class AudioListViewAdmin(MediaListAdmin):
    media_type = "audio"


class ImageDecisionAdmin(MediaDecisionAdmin):
    media_type = "image"
    through_model = ImageDecisionThrough


class AudioDecisionAdmin(MediaDecisionAdmin):
    media_type = "audio"
    through_model = AudioDecisionThrough


class MediaSubreportAdmin(admin.ModelAdmin):
    exclude = ("media_obj",)
    search_fields = ("media_obj__identifier",)
    readonly_fields = ("media_obj_id",)

    def has_add_permission(self, *args, **kwargs):
        """Create ``_Report`` instances instead."""
        return False
