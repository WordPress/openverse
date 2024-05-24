from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username}'s preferences"

    @property
    def moderator(self):
        if "moderator" not in self.preferences:
            self.preferences["moderator"] = {}

        return self.preferences["moderator"]

    @moderator.setter
    def moderator(self, value):
        self.preferences["moderator"] = value

    @property
    def blur_images(self):
        return self.moderator.get("blur_images", True)

    @blur_images.setter
    def blur_images(self, value):
        self.moderator |= {"blur_images": value}


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)
    instance.userpreferences.save()


def get_moderators() -> models.QuerySet:
    """
    Get all users who either are members of the "Content Moderators"
    group or have superuser privileges.

    :return: a ``QuerySet`` of ``User``s who can perform moderation
    """

    User = get_user_model()
    return User.objects.filter(
        Q(groups__name="Content Moderators") | Q(is_superuser=True)
    )
