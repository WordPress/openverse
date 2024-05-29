from django import forms
from django.contrib import admin

from oauth2_provider.models import AccessToken

from api.constants.restricted_features import RestrictedFeature
from api.models.oauth import ThrottledApplication


def register(site):
    site.register(ThrottledApplication, ThrottledApplicationAdmin)
    site.register(AccessToken, AccessTokenAdmin)


class ThrottledApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = ThrottledApplication
        exclude = (
            "client_type",
            "redirect_uris",
            "post_logout_redirect_uris",
            "skip_authorization",
            "algorithm",
            "user",
        )

    # ArrayField doesn't have a good default field, so use a multiple choice field, but
    # override default widget of multi-<select>, which is much more annoying to use
    # and easy to accidentally un-select an option. The multi-checkbox is much easier to use
    privileges = forms.MultipleChoiceField(
        choices=RestrictedFeature.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )


class ThrottledApplicationAdmin(admin.ModelAdmin):
    form = ThrottledApplicationAdminForm
    view_on_site = False

    search_fields = ("client_id", "name", "rate_limit_model", "privileges")
    list_display = ("client_id", "name", "created", "rate_limit_model", "privileges")
    ordering = ("-created",)

    readonly_fields = (
        "name",
        "created",
        "client_id",
        "verified",
        "authorization_grant_type",
        "client_secret",
    )

    def has_delete_permission(self, *args, **kwargs):
        """
        Disallow deleting throttled applications. Use ``revoke`` instead.

        This also hides the delete button on the change view.
        """
        return False


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
