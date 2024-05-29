import pytest

from api.admin.user import UserPreferencesAdminForm
from api.models import UserPreferences


@pytest.mark.django_db
@pytest.mark.parametrize(
    "initial_preferences, blur_images_value, expected_preferences",
    [
        ({}, True, {"moderator": {"blur_images": True}}),
        ({}, False, {"moderator": {"blur_images": False}}),
        (
            {"moderator": {"blur_images": False}},
            True,
            {"moderator": {"blur_images": True}},
        ),
        (
            {"moderator": {"blur_images": False}},
            False,
            {"moderator": {"blur_images": False}},
        ),
        (
            {"moderator": {"blur_images": True}},
            True,
            {"moderator": {"blur_images": True}},
        ),
        (
            {"moderator": {"blur_images": False}},
            False,
            {"moderator": {"blur_images": False}},
        ),
        (
            {"some_other_setting": 123},
            False,
            {"some_other_setting": 123, "moderator": {"blur_images": False}},
        ),
        (
            {"moderator": {"some_other_setting": 123}},
            False,
            {"moderator": {"some_other_setting": 123, "blur_images": False}},
        ),
    ],
)
def test_user_preferences_form(
    initial_preferences, blur_images_value, expected_preferences, django_user_model
):
    user = django_user_model.objects.create(username="foobar", password="fake")
    preferences = user.userpreferences
    # Check that new user has no preferences
    assert preferences.preferences == {}
    # Set the initial user preferences
    preferences.preferences = initial_preferences
    preferences.save()

    form_data = {"blur_images": blur_images_value}
    form = UserPreferencesAdminForm(data=form_data, instance=preferences)
    assert form.is_valid(), "Form should be valid"
    instance = form.save()
    # Retrieve the instance from the database to ensure it's saved correctly
    saved_instance = UserPreferences.objects.get(id=instance.id)
    assert saved_instance.preferences == expected_preferences
