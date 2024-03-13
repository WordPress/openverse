from django import forms

from api.models import UserPreferences


class UserPreferencesAdminForm(forms.ModelForm):
    blur_images = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = UserPreferences
        fields = ["blur_images"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["blur_images"] = self._get_blur_images()

    def _get_blur_images(self):
        mod_preferences = self.instance.preferences.get("moderator", {})
        return mod_preferences.get("blur_images", True)

    @staticmethod
    def _set_blur_images(instance, value):
        mod_preferences = instance.preferences.get("moderator", {})
        mod_preferences["blur_images"] = value
        instance.preferences = instance.preferences | {"moderator": mod_preferences}

    def save(self, commit=True):
        instance: UserPreferences = super().save(commit=False)
        blur_images = self.cleaned_data.get("blur_images", True)
        self._set_blur_images(instance, blur_images)
        if commit:
            instance.save()
        return instance
