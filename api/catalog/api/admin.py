from django.contrib import admin

from catalog.api.models import (
    PENDING,
    ContentProvider,
    DeletedImage,
    ImageReport,
    MatureImage,
    SourceLogo,
)


@admin.register(ImageReport)
class ImageReportAdmin(admin.ModelAdmin):
    list_display = ("reason", "status", "image_url", "description", "created_at")
    list_filter = ("status", "reason")
    list_display_links = ("status",)
    search_fields = ("description", "identifier")
    actions = None

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        always_readonly = [
            "reason",
            "image_url",
            "description",
            "identifier",
            "created_at",
        ]
        if obj.status == PENDING:
            return always_readonly
        else:
            status_readonly = ["status"]
            status_readonly.extend(always_readonly)
            return status_readonly


@admin.register(MatureImage)
class MatureImageAdmin(admin.ModelAdmin):
    search_fields = ("identifier",)


@admin.register(DeletedImage)
class DeletedImage(admin.ModelAdmin):
    search_fields = ("identifier",)


class InlineImage(admin.TabularInline):
    model = SourceLogo


@admin.register(ContentProvider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("provider_name", "provider_identifier", "media_type")
    search_fields = ("provider_name", "provider_identifier")
    exclude = ("notes",)
    inlines = [InlineImage]
