import json
from typing import Any

from django.views.generic import TemplateView


scalar_config = {
    "hideModels": True,
}


class ScalarView(TemplateView):
    template_name = "open_api/scalar.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["configuration"] = json.dumps(scalar_config)
        return context
