import argparse
from pathlib import Path


IMAGE_STORE_INIT = 'image_store = ImageStore(provider=PROVIDER)'
AUDIO_STORE_INIT = 'audio_store = AudioStore(provider=PROVIDER)'


def _get_filled_template(template_path, provider, media_type='image'):
    with open(template_path, 'r', encoding='utf8') as template:
        template_string = template.read()
        script_string = template_string.replace(
            '{provider_title_case}', provider.title()
        ).replace(
            '{provider_upper_case}', provider.upper()
        ).replace(
            '{provider}', provider.lower()
        )
        if media_type == 'audio':
            media_store_init = AUDIO_STORE_INIT
            media_store = 'audio_store'
        else:
            media_store_init = IMAGE_STORE_INIT
            media_store = 'image_store'
        script_string = script_string.replace(
            'media_store_init', media_store_init
        ).replace(
            '{media_store}', media_store
        ).replace(
            '{media_type}', media_type
        )

        return script_string


def fill_template(provider, media_type, templates_path):
    project_path = templates_path.parent.parent.parent
    template_name = 'template_provider.py_template'
    script_template_path = templates_path / template_name
    print(f"Creating files in {project_path}")

    dags_path = templates_path.parent / 'dags'
    filename = provider.replace(" ", '_').lower()

    api_path = dags_path / 'provider_api_scripts'
    api_script_path = api_path / f"{filename}.py"
    with open(api_script_path, 'w+', encoding='utf8') as api_script:
        api_script_string = _get_filled_template(
            script_template_path, provider, media_type
        )
        api_script.write(api_script_string)
        print(f"API script: {api_script_path.relative_to(project_path)}")

    template_name = 'template_test.py_template'
    script_template_path = templates_path / template_name
    test_script_path = api_path / f"test_{filename}.py"
    with open(test_script_path, 'w+', encoding='utf8') as test_script:
        test_string = _get_filled_template(
            script_template_path, provider, media_type
        )
        test_script.write(test_string)
        print(f"API script test: {test_script_path.relative_to(project_path)}")

    workflow_template_path = templates_path / 'workflow.py_template'
    workflow_path = dags_path / f"{filename}_workflow.py"
    with open(workflow_path, 'w+', encoding='utf8') as workflow_file:
        workflow_string = _get_filled_template(
            workflow_template_path, provider
        )
        workflow_file.write(workflow_string)
        print("Airflow workflow file: "
              f"{workflow_path.relative_to(project_path)}")


def main():
    parser = argparse.ArgumentParser(
        description='Create a new provider API script',
        add_help=True,
    )
    parser.add_argument(
        "provider",
        help='Create the script for this provider (eg. "Wikimedia").')
    parser.add_argument(
        '-m', '--media', type=str, choices=['image', 'audio'],
        help="Script will collect media of this type"
             " ('audio'/'image'). Default value is 'image'"
    )
    args = parser.parse_args()
    provider = args.provider
    media_type = args.media
    if media_type not in ['audio', 'image']:
        print("No media type given, assuming it's `image`")
        media_type = 'image'
    templates_path = Path(__file__).parent
    fill_template(provider, media_type, templates_path)


if __name__ == "__main__":
    main()
