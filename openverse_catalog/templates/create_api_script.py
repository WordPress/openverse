import argparse
from pathlib import Path


IMAGE_STORE_INIT = "image_store = ImageStore(provider=PROVIDER)"
AUDIO_STORE_INIT = "audio_store = AudioStore(provider=PROVIDER)"
TEMPLATES_PATH = Path(__file__).parent
REPO_PATH = TEMPLATES_PATH.parents[1]
PROJECT_PATH = REPO_PATH.parent


def _get_filled_template(template_path: Path, provider: str, media_type: str):
    with template_path.open("r", encoding="utf-8") as template:
        template_string = template.read()
        script_string = (
            template_string.replace("{provider_title_case}", provider.title())
            .replace("{provider_upper_case}", provider.upper())
            .replace("{provider}", provider.lower())
        )
        if media_type == "audio":
            media_store_init = AUDIO_STORE_INIT
            media_store = "audio_store"
        else:
            media_store_init = IMAGE_STORE_INIT
            media_store = "image_store"
        script_string = (
            script_string.replace("media_store_init", media_store_init)
            .replace("{media_store}", media_store)
            .replace("{media_type}", media_type)
        )

        return script_string


def _render_file(
    target: Path,
    template_path: Path,
    provider: str,
    media_type: str,
    name: str,
):
    with target.open("w", encoding="utf-8") as target_file:
        filled_template = _get_filled_template(template_path, provider, media_type)
        target_file.write(filled_template)
        print(f"{name + ':':<18} {target.relative_to(PROJECT_PATH)}")


def fill_template(provider, media_type):
    print(f"Creating files in {REPO_PATH}")

    dags_path = TEMPLATES_PATH.parent / "dags"
    api_path = dags_path / "provider_api_scripts"
    filename = provider.replace(" ", "_").lower()

    # Render the API file itself
    script_template_path = TEMPLATES_PATH / "template_provider.py_template"
    api_script_path = api_path / f"{filename}.py"
    _render_file(
        api_script_path, script_template_path, provider, media_type, "API script"
    )

    # Render the DAG workflow
    workflow_template_path = TEMPLATES_PATH / "workflow.py_template"
    workflow_path = dags_path / f"{filename}_workflow.py"
    _render_file(
        workflow_path,
        workflow_template_path,
        provider,
        media_type,
        "Airflow DAG",
    )

    # Render the tests
    script_template_path = TEMPLATES_PATH / "template_test.py_template"
    tests_path = REPO_PATH / "tests"
    # Mirror the directory structure, but under the "tests" top level directory
    test_script_path = tests_path.joinpath(*api_path.parts[-2:]) / f"test_{filename}.py"
    _render_file(
        test_script_path, script_template_path, provider, media_type, "API script test"
    )

    print(
        """
NOTE: You will also need to add the Airflow workflow file to the WORKFLOWS list in the \
DAG parsing test file (openverse-catalog/tests/dags/test_dag_parsing.py).
"""
    )


def main():
    parser = argparse.ArgumentParser(
        description="Create a new provider API script",
        add_help=True,
    )
    parser.add_argument(
        "provider", help='Create the script for this provider (eg. "Wikimedia").'
    )
    parser.add_argument(
        "-m",
        "--media",
        type=str,
        choices=["image", "audio"],
        help="Script will collect media of this type"
        " ('audio'/'image'). Default value is 'image'",
    )
    args = parser.parse_args()
    provider = args.provider
    media_type = args.media
    if media_type not in ["audio", "image"]:
        print("No media type given, assuming it's `image`")
        media_type = "image"

    fill_template(provider, media_type)


if __name__ == "__main__":
    main()
