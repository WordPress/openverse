from django.contrib import admin

from oauth2_provider.models import AccessToken


def register(site):
    site.register(AccessToken, AccessTokenAdmin)


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
