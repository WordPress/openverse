from jinja2 import Environment, PackageLoader, select_autoescape

from openverse_api_client_generator.components import (
    py_type_string,
    ts_type_string,
    ts_comment,
)


template_env = Environment(
    loader=PackageLoader("openverse_api_client_generator"),
    autoescape=select_autoescape(),
)

template_env.filters["ts_type_string"] = ts_type_string
template_env.filters["py_type_string"] = py_type_string
template_env.filters["ts_comment"] = ts_comment


class MultiTemplate:
    def __init__(self, name: str, defaults: dict):
        self.template = template_env.get_template(name)
        self.defaults = defaults

    def render(self, **context) -> str:
        return self.template.render(**(self.defaults | context))


templates = {
    "py": {
        "models": template_env.get_template("models.py.j2"),
        "async_client": MultiTemplate(
            "client.py.j2",
            defaults={
                "await": "await ",
                "a": "a",
                "def": "async def",
                "Async": "Async",
            },
        ),
        "sync_client": MultiTemplate(
            "client.py.j2",
            defaults={
                "await": "",
                "a": "",
                "def": "def",
                "Async": "",
            },
        ),
    },
    "ts": {
        "models": template_env.get_template("models.ts.j2"),
        "routes": template_env.get_template("routes.ts.j2"),
    },
}
