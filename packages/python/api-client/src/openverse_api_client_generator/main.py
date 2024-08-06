import re
from http.client import HTTPResponse
from pathlib import Path
from typing import TypeAlias
from urllib.request import urlopen

import yaml

from openverse_api_client_generator.components import (
    Model,
    Route,
    model_from_schema,
    route_from_schema,
)
from openverse_api_client_generator.template_env import templates


OUT = Path(__file__).parents[2] / "out"
OUT.mkdir(exist_ok=True)


def get_models(
    component_schemas: dict, model_names: list[str]
) -> tuple[dict[str, Model], dict[str, TypeAlias]]:
    models = {}
    enums = {}
    for name in model_names:
        schema = component_schemas[name]
        model = model_from_schema(name, schema)
        if isinstance(model, Model):
            models[name] = model
        else:
            enums[name] = model

    return models, enums


def get_routes(
    path_schemas: dict, path_matchers: list[str | re.Pattern]
) -> list[Route]:
    routes = []
    for path, methods in path_schemas.items():
        should_process = False
        for matcher in path_matchers:
            if isinstance(matcher, str):
                if matcher == path:
                    should_process = True
                    break
            else:
                if matcher.search(path):
                    should_process = True
                    break

        if not should_process:
            continue

        for method in methods:
            routes.append(route_from_schema(path, method, methods[method]))

    return routes


def main(openverse_api_url: str) -> None:
    openverse_api_url = (
        openverse_api_url[:-1] if openverse_api_url[-1] == "/" else openverse_api_url
    )
    schema_res: HTTPResponse = urlopen(f"{openverse_api_url}/v1/schema/")

    schema_bytes = schema_res.read()
    out_schema = Path.cwd() / "schema.yaml"
    out_schema.unlink(missing_ok=True)
    out_schema.write_bytes(schema_bytes)

    schema: dict = yaml.full_load(schema_bytes)

    models, enums = get_models(
        schema["components"]["schemas"],
        [
            "GrantTypeEnum",
            "OAuth2KeyInfo",
            "OAuth2Token",
            "OAuth2Registration",
            "OAuth2Application",
            "OAuth2TokenRequest",
            "Source",
            "Tag",
            "AudioAltFile",
            "AudioSet",
            "AudioWaveform",
            "Audio",
            "Image",
            "PaginatedImageList",
            "PaginatedAudioList",
        ],
    )

    routes = get_routes(
        schema["paths"],
        [
            re.compile(r"^/v1/(images|audio)/(stats/)?$"),
            re.compile(r"^/v1/(images|audio)/\{identifier\}/$"),
            re.compile(
                r"^/v1/(images|audio)/\{identifier\}/(thumb|related|waveform)/$"
            ),
            re.compile(r"^/v1/auth_tokens/.*$"),
            "/v1/rate_limit/",
        ],
    )

    for filetype in ["py", "ts"]:
        for name, template in templates[filetype].items():
            rendered = template.render(
                models=models,
                enums=enums,
                routes=routes,
            )

            file_out = OUT / f"{name}.{filetype}"
            file_out.unlink(missing_ok=True)
            file_out.write_text(rendered)
