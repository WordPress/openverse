from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.http.response import HttpResponseRedirect
from django.urls import reverse

from api.models import UserPreferences


def register(site):
    site.register(User, UserAdmin)
    site.register(Group, GroupAdmin)

    site.register(UserPreferences, IndividualUserPreferencesAdmin)


class UserPreferencesAdminForm(forms.ModelForm):
    blur_images = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = UserPreferences
        fields = ["blur_images"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["blur_images"] = self.instance.blur_images

    def save(self, commit=True):
        self.instance.blur_images = self.cleaned_data.get("blur_images")
        return super().save(commit=commit)


class IndividualUserPreferencesAdmin(admin.ModelAdmin):
    """
    Model admin for showing user preferences. This should only ever show the
    currently logged-in user's preferences
    """

    verbose_name_plural = "My Preferences"
    verbose_name = "My Preferences"
    form = UserPreferencesAdminForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(*args, **kwargs):
        return False

    def has_delete_permission(*args, **kwargs):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.get_queryset(request).first()
        return HttpResponseRedirect(
            reverse("admin:api_userpreferences_change", args=[obj.id])
        )
