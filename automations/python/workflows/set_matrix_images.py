"""
Determine which Docker images to build and publish. For more information refer
to the documentation:
https://docs.openverse.org/meta/ci_cd/jobs/docker.html#determine-images
"""

import json
import os
from dataclasses import asdict, dataclass

from shared.actions import write_to_github_output


@dataclass
class Include:
    image: str
    target: str

    context: str
    file: str
    build_contexts: str
    build_args: str

    def __init__(
        self,
        image: str,
        target: str,
        context: str | None = None,
        file: str | None = None,
        build_contexts: str | None = None,
        build_args: str | None = None,
    ):
        self.image = image
        self.target = target
        self.context = context or image
        self.file = file or f"{self.context}/Dockerfile"
        self.build_contexts = build_contexts or ""
        self.build_args = build_args or ""

    @property
    def asdict(self) -> dict[str, str]:
        return {k.replace("_", "-"): v for k, v in asdict(self).items()}


changes = json.loads(os.environ.get("CHANGES"))


def ser_set(x):
    """Convert ``set`` into ``list``, else return the parameter as-is."""
    return list(x) if isinstance(x, set) else x


build_matrix = {"image": set()}
publish_matrix = {"image": set()}

includes: dict[str, Include] = {
    "upstream_db": Include(
        image="upstream_db",
        target="db",
        context="docker/upstream_db",
    ),
    "catalog": Include(image="catalog", target="cat"),
    "ingestion_server": Include(image="ingestion_server", target="ing"),
    "api": Include(
        image="api",
        target="api",
        build_contexts="packages=./packages/python",
        build_args="PDM_INSTALL_ARGS=--prod",
    ),
    "api_nginx": Include(
        image="api_nginx",
        target="nginx",
        context="api",
        build_contexts="packages=./packages/python",
    ),
    "frontend": Include(
        image="frontend",
        target="app",
        build_contexts="repo_root=.",
    ),
    "frontend_nginx": Include(
        image="frontend_nginx",
        target="nginx",
        context="frontend",
        file="frontend/Dockerfile.nginx",
    ),
}

if "ci_cd" in changes:
    build_matrix["image"] |= set(includes.keys())
if "catalog" in changes:
    build_matrix["image"] |= {"upstream_db", "catalog"}
    publish_matrix["image"].add("catalog")
if "ingestion_server" in changes:
    build_matrix["image"] |= {"upstream_db", "ingestion_server", "api"}
    publish_matrix["image"].add("ingestion_server")
if "api" in changes:
    build_matrix["image"] |= {"upstream_db", "ingestion_server", "api", "api_nginx"}
    publish_matrix["image"] |= {"api", "api_nginx"}
if "frontend" in changes:
    build_matrix["image"] |= {"frontend", "frontend_nginx"}
    publish_matrix["image"] |= {"frontend", "frontend_nginx"}


build_matrix["include"] = [includes[item].asdict for item in build_matrix["image"]]

for item in build_matrix["include"]:
    if "context" not in item:
        item["context"] = item["image"]

    if "file" not in item:
        item["file"] = f"{item['context']}/Dockerfile"

do_build = "true" if len(build_matrix["image"]) else "false"
do_publish = "true" if len(publish_matrix["image"]) else "false"
build_matrix = json.dumps(build_matrix, default=ser_set)
publish_matrix = json.dumps(publish_matrix, default=ser_set)

lines = [
    f"do_build={do_build}",
    f"build_matrix={build_matrix}",
    f"do_publish={do_publish}",
    f"publish_matrix={publish_matrix}",
]
write_to_github_output(lines)
