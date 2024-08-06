import argparse
import shutil
from pathlib import Path
import subprocess

from openverse_api_client_generator.main import main


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "--openverse-api-url",
    default="http://localhost:50280",
    help="URL of the Openverse API instance to use",
)


PACKAGES = Path(__file__).parents[4]
REPO = PACKAGES.parent
GENERATED = PACKAGES / "python" / "api-client" / "out"
JS_CLIENT_OUT = PACKAGES / "js" / "api-client" / "src" / "generated"
PY_CLIENT_OUT = (
    PACKAGES / "python" / "api-client" / "src" / "openverse_api_client" / "_generated"
)


def cli():
    args = arg_parser.parse_args()
    main(**args.__dict__)

    lint_args = ["pre-commit", "run", "--files"] + [
        file.absolute() for file in GENERATED.iterdir()
    ]

    subprocess.run(lint_args)

    shutil.rmtree(JS_CLIENT_OUT, ignore_errors=True)
    JS_CLIENT_OUT.mkdir()
    shutil.rmtree(PY_CLIENT_OUT, ignore_errors=True)
    PY_CLIENT_OUT.mkdir()

    for file in GENERATED.glob("*.ts"):
        dest = JS_CLIENT_OUT / file.name
        dest.unlink(missing_ok=True)
        dest.touch()
        dest.write_bytes(file.read_bytes())

    for file in GENERATED.glob("*.py"):
        dest = PY_CLIENT_OUT / file.name
        dest.unlink(missing_ok=True)
        dest.touch()
        dest.write_bytes(file.read_bytes())
