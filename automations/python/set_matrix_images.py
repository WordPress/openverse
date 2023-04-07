"""Python script Set Matrix Images for workflow"""

import json
import os
import sys

changes = json.loads(os.environ.get('CHANGES'))

build_matrix = {"image": [], "include": []}
publish_matrix = {"image": []}

if "frontend" in changes:
    build_matrix["image"].append("frontend")
    build_matrix["include"].append({"image": "frontend",
                                    "context": "frontend", "target": "app"})
    publish_matrix["image"].append("frontend")
if "api" in changes or "ingestion_server" in changes:
    # Always build the ingestion server and API images for either changeset
    build_matrix["image"] += ["api", "ingestion_server"]
    build_matrix["include"] += [
                                {"image": "ingestion_server",
                                    "context": "ingestion_server",
                                    "target": "ing"},
                                {"image": "api", "context": "api",
                                 "target": "api"},
                                ]
    if "api" in changes:
        build_matrix["image"].append("api_nginx")
        build_matrix["include"].append({"image": "api_nginx",
                                        "context": "api", "target": "nginx"})
        publish_matrix["image"] += ["api", "api_nginx"]
    if "ingestion_server" in changes:
        publish_matrix["image"].append("ingestion_server")

DO_BUILD = 'true' if len(build_matrix["image"]) else 'false'
DO_PUBLISH = 'true' if len(publish_matrix["image"]) else 'false'

with open(os.environ.get("GITHUB_OUTPUT"), "a", encoding='utf-8') as gh_out:
    for dest in [sys.stdout, gh_out]:
        print(f"do_build={DO_BUILD}", file=dest)
        print(f"build_matrix={json.dumps(build_matrix)}", file=dest)
        print(f"do_publish={DO_PUBLISH}", file=dest)
        print(f"publish_matrix={json.dumps(publish_matrix)}", file=dest)
