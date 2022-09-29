from django.contrib import admin

from catalog.api.constants.media_types import MEDIA_TYPE_CHOICES


class OpenverseAdmin(admin.AdminSite):
    site_header = "Openverse administration"

    def get_app_list(self, *args, **kwargs):
        """
        Modify the app and model list to present media specific models outside the main
        API group. This makes the long list easier to comprehend and locating the model
        of interest faster.
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
            models.sort(key=lambda x: "0" if "report" in x["name"] else x["name"])

            media_app = {
                "name": media_type_name,
                "app_label": media_type,
                "app_url": f"/admin/{media_type}",
                "has_module_perms": True,
                "models": models,
            }
            app_list.insert(0, media_app)

        return app_list


openverse_admin = OpenverseAdmin()
