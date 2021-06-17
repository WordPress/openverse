import argparse
from pathlib import Path


IMAGE_STORE_INIT = 'image_store = ImageStore(provider=PROVIDER)'
AUDIO_STORE_INIT = 'audio_store = AudioStore(provider=PROVIDER)'


def _get_filled_template(template_path, provider, media_type=None):
    with open(template_path, 'r', encoding='utf8') as template:
        template_string = template.read()
        script_string = template_string.replace(
            '{provider_title_case}', provider.title()
        ).replace(
            '{provider_upper_case}', provider.upper()
        ).replace(
            '{provider}', provider
        )
        if media_type:
            if media_type == 'image':
                media_store_init = IMAGE_STORE_INIT
                media_store = 'image_store'
            else:
                media_store_init = AUDIO_STORE_INIT
                media_store = 'audio_store'
            script_string = script_string.replace(
                'media_store_init',
                media_store_init
            ).replace(
                '{media_store}',
                media_store
            )
        return script_string


def fill_template(provider, media_type):
    templates_path = Path(__file__).parent
    template_name = 'template_provider.py_template'
    script_template_path = templates_path / template_name

    dags_path = templates_path.parent / 'dags'
    filename = provider.replace(" ", '_').lower()

    api_path = dags_path / 'provider_api_scripts'
    api_script_path = api_path / f"{filename}.py"
    with open(api_script_path, 'w+', encoding='utf8') as api_script:
        api_script_string = _get_filled_template(
            script_template_path, provider, media_type
        )
        api_script.write(api_script_string)
        print(f"Created api script: {api_script_path}")

    test_script_path = api_path / f"test_{filename}.py"
    with open(test_script_path, 'w+', encoding='utf8') as test_script:
        test_script.write('# TODO: Write your tests!')
        print(f"Created api script test: {test_script_path}")

    workflow_template_path = templates_path / 'workflow.py_template'
    workflow_path = dags_path / f"{filename}_workflow.py"
    with open(workflow_path, 'w+', encoding='utf8') as workflow_file:
        workflow_string = _get_filled_template(
            workflow_template_path, provider
        )
        workflow_file.write(workflow_string)
        print(f"Created workflow file: {workflow_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Create a new provider API script',
        add_help=True,
    )
    parser.add_argument(
        '--provider',
        help='Name of the provider to create the script for.')
    parser.add_argument(
        '--media',
        help='Media type to collect data for, `audio` or `image`'
    )
    args = parser.parse_args()
    if args.provider:
        provider = args.provider
        media_type = args.media
        if media_type not in ['audio', 'image']:
            print(f"Media type {media_type} is not supported,"
                  f" assuming it's image")
            media_type = 'image'
        fill_template(provider, media_type)


if __name__ == "__main__":
    main()
