import os


TOKEN = os.getenv("REQUEST_TOKEN", "<Openverse API token>")
DOMAIN = os.getenv("CANONICAL_DOMAIN")
_proto = "http" if "localhost" in DOMAIN else "https"
ORIGIN = f"{_proto}://{DOMAIN}"
