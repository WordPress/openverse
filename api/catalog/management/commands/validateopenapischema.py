from argparse import ArgumentParser
from pathlib import Path

from django.core.management import BaseCommand, call_command

from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename
from openapi_spec_validator.validation import openapi_v2_spec_validator


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--output-dir",
            default=Path(".").absolute(),
            help=(
                "The direction into which to output the spec file. "
                "Defaults the the current working directory."
            ),
        )

    def handle_validation(self, spec_dict: dict):
        """Validate the spec and raise an error if the spec is not valid."""

        validate_spec(spec_dict, validator=openapi_v2_spec_validator)

        invalid_paths = [p for p in spec_dict["paths"].keys() if not p.endswith("/")]

        assert invalid_paths == [], (
            "All paths must end with a trailing slash. "
            f"Found {len(invalid_paths)} missing a trailing "
            f"slash: {', '.join(invalid_paths)}"
        )

    def handle(self, *args, **options):
        file_path = (Path(options["output_dir"]).absolute() / "openapi.yaml").absolute()
        call_command("generate_swagger", file_path, overwrite=True)
        spec_dict, spec_url = read_from_filename(file_path)
        self.handle_validation(spec_dict)
        # Only remove the file when there are no errros to ease debugging.
        # Therefore, we don't `try/except` the call to `handle_validation`
        file_path.unlink()
