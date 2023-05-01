"""
Determine which Docker images to build and publish. For more information refer
to the documentation:
https://docs.openverse.org/meta/ci_cd/jobs/docker_preparation.html#determine-images
"""

import json
import os
import sys


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
    "catalog": {"image": "catalog", "context": "catalog", "target": "cat"},
    "ingestion_server": {
        "image": "ingestion_server",
        "context": "ingestion_server",
        "target": "ing",
    },
    "api": {"image": "api", "context": "api", "target": "api"},
    "api_nginx": {"image": "api_nginx", "context": "api", "target": "nginx"},
    "frontend": {"image": "frontend", "context": "frontend", "target": "app"},
}

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
    build_matrix["image"].add("frontend")
    publish_matrix["image"].add("frontend")

build_matrix["include"] = [includes[item] for item in build_matrix["image"]]

do_build = "true" if len(build_matrix["image"]) else "false"
do_publish = "true" if len(publish_matrix["image"]) else "false"
build_matrix = json.dumps(build_matrix, default=ser_set)
publish_matrix = json.dumps(publish_matrix, default=ser_set)

with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as gh_out:
    for dest in [sys.stdout, gh_out]:
        print(f"do_build={do_build}", file=dest)
        print(f"build_matrix={build_matrix}", file=dest)
        print(f"do_publish={do_publish}", file=dest)
        print(f"publish_matrix={publish_matrix}", file=dest)
