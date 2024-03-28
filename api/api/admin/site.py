from django.contrib import admin

from api.constants.media_types import MEDIA_TYPE_CHOICES


class OpenverseAdmin(admin.AdminSite):
    site_header = "Openverse administration"

    def get_app_list(self, *args, **kwargs):
        """
        Present media specific models outside the main API group.

        This modifies the app and model list to make it shorter and easier to
        comprehend, thereby making it faster to locate the model of interest.
        """

        app_list = super().get_app_list(*args, **kwargs)
        api_app = next((app for app in app_list if app["app_label"] == "api"), None)
        if api_app is None:
            return app_list

        for media_type, media_type_name in MEDIA_TYPE_CHOICES:
            models = []
            for model in api_app["models"][:]:
                if media_type in model["object_name"].lower():
                    models.append(model)
                    api_app["models"].remove(model)

            def key(entry):
                name = entry["name"]
                if name in ["Audios", "Images"]:
                    return "0"
                elif "report" in name:
                    return "1"
                else:
                    return name

            models.sort(key=key)

            media_app = {
                "name": media_type_name,
                "app_label": media_type,
                "app_url": f"/admin/{media_type}",
                "has_module_perms": True,
                "models": models,
            }
            app_list.insert(0, media_app)

        # Move user preferences to its own section
        for model in api_app["models"][:]:
            if model["object_name"] == "UserPreferences":
                model["name"] = "My Preferences"
                api_app["models"].remove(model)
                app_list.insert(
                    -1,
                    {
                        "name": "User Preferences",
                        "app_label": "preferences",
                        "app_url": "/admin/api/userpreferences/",
                        "has_module_perms": True,
                        "models": [model],
                    },
                )

        return app_list


openverse_admin = OpenverseAdmin()
