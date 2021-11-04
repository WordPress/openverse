from pathlib import Path

from openverse_catalog.templates import create_api_script


def test_files_created():
    provider = "Foobar Industries"
    media_type = "image"
    dags_path = create_api_script.TEMPLATES_PATH.parent / "dags" / "providers"
    expected_provider = dags_path / "provider_api_scripts" / "foobar_industries.py"
    expected_workflow = dags_path / "foobar_industries_workflow.py"
    expected_test = (
        Path(__file__).parents[1]
        / "dags"
        / "providers"
        / "provider_api_scripts"
        / "test_foobar_industries.py"
    )
    try:
        create_api_script.fill_template(provider, media_type)
        assert expected_provider.exists()
        assert expected_workflow.exists()
        assert expected_test.exists()
    finally:
        # Clean up
        expected_provider.unlink(missing_ok=True)
        expected_workflow.unlink(missing_ok=True)
        expected_test.unlink(missing_ok=True)
