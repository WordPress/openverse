from django.contrib import admin
from cccatalog.api.models import ImageReport, MatureImage


@admin.register(ImageReport)
class ImageReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'status', 'image_url', 'description')
    list_filter = ('status', 'reason')
    list_display_links = ('status',)
    actions = None

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        always_readonly = ['reason', 'image_url', 'description', 'identifier']
        if obj.status == 'pending_review':
            return always_readonly
        else:
            status_readonly = ['status']
            status_readonly.extend(always_readonly)
            return status_readonly


@admin.register(MatureImage)
class MatureImageAdmin(admin.ModelAdmin):
    search_fields = ('identifier',)
