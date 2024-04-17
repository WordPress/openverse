from django import forms

from api.models import UserPreferences


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
