from django.contrib import admin

from oauth2_provider.models import AccessToken

from api.admin.site import openverse_admin
from api.models import PENDING, Audio, AudioReport, ContentProvider, Image, ImageReport
from api.models.media import AbstractDeletedMedia, AbstractSensitiveMedia
from api.models.oauth import ThrottledApplication


admin.site = openverse_admin
admin.sites.site = openverse_admin


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ("identifier",)


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    search_fields = ("identifier",)


class MediaReportAdmin(admin.ModelAdmin):
    list_display = ("reason", "status", "description", "created_at")
    media_specific_list_display = ()
    list_filter = ("status", "reason")
    list_display_links = ("status",)
    search_fields = ("description", "media_obj__identifier")
    autocomplete_fields = ("media_obj",)
    actions = None

    def get_list_display(self, request):
        return self.list_display + self.media_specific_list_display

    def get_exclude(self, request, obj=None):
        # ``identifier`` cannot be edited on an existing report.
        if request.path.endswith("/change/"):
            return ["media_obj"]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        readonly_fields = [
            "reason",
            "description",
            "media_obj_id",
            "created_at",
        ]
        # ``status`` cannot be changed on a finalised report.
        if obj.status != PENDING:
            readonly_fields.append("status")
        return readonly_fields


@admin.register(ImageReport)
class ImageReportAdmin(MediaReportAdmin):
    media_specific_list_display = ("image_url",)


@admin.register(AudioReport)
class AudioReportAdmin(MediaReportAdmin):
    media_specific_list_display = ("audio_url",)


class MediaSubreportAdmin(admin.ModelAdmin):
    exclude = ("media_obj",)
    search_fields = ("media_obj__identifier",)
    readonly_fields = ("media_obj_id",)

    def has_add_permission(self, *args, **kwargs):
        """Create ``_Report`` instances instead."""
        return False


for klass in [
    *AbstractSensitiveMedia.__subclasses__(),
    *AbstractDeletedMedia.__subclasses__(),
]:
    admin.site.register(klass, MediaSubreportAdmin)


@admin.register(ContentProvider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("provider_name", "provider_identifier", "media_type")
    search_fields = ("provider_name", "provider_identifier")
    ordering = ("media_type", "provider_name")


@admin.register(ThrottledApplication)
class ThrottledApplicationAdmin(admin.ModelAdmin):
    search_fields = ("client_id", "name")
    list_display = ("client_id", "name", "created", "rate_limit_model")
    ordering = ("-created",)

    readonly_fields = (
        "skip_authorization",
        "verified",
        "client_id",
        "name",
        "user",
        "algorithm",
        "redirect_uris",
        "post_logout_redirect_uris",
        "client_type",
        "authorization_grant_type",
        "client_secret",
    )


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    search_fields = ("token", "id")
    list_display = ("token", "id", "created", "scope", "expires")
    ordering = ("-created",)

    readonly_fields = (
        "id",
        "user",
        "source_refresh_token",
        "token",
        "id_token",
        "application",
        "expires",
        "scope",
        "created",
        "updated",
    )
