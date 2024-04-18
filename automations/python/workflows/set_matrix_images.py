"""
Determine which Docker images to build and publish. For more information refer
to the documentation:
https://docs.openverse.org/meta/ci_cd/jobs/docker.html#determine-images
"""

import json
import os

from shared.actions import write_to_github_output


changes = json.loads(os.environ.get("CHANGES"))


def ser_set(x):
    """Convert ``set`` into ``list``, else return the parameter as-is."""
    return list(x) if isinstance(x, set) else x


build_matrix = {"image": set()}
publish_matrix = {"image": set()}

includes = {
    "upstream_db": {
        "image": "upstream_db",
        "context": "docker/upstream_db",
        "target": "db",
    },
    "catalog": {"image": "catalog", "target": "cat"},
    "ingestion_server": {"image": "ingestion_server", "target": "ing"},
    "api": {
        "image": "api",
        "target": "api",
        "build-contexts": "packages=./py-packages",
    },
    "api_nginx": {
        "image": "api_nginx",
        "context": "api",
        "target": "nginx",
        "build-contexts": "packages=./py-packages",
    },
    "frontend": {"image": "frontend", "target": "app", "build-contexts": "repo_root=."},
    "frontend_nginx": {
        "image": "frontend_nginx",
        "context": "frontend",
        "file": "frontend/Dockerfile.nginx",
        "target": "nginx",
    },
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


build_matrix["include"] = [includes[item] for item in build_matrix["image"]]

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
