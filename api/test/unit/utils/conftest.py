import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def mock_image_data():
    mock_image_path = Path(__file__).parent / ".." / ".." / "factory"
    mock_image_file = mock_image_path / "sample-image.jpg"
    mock_image_info = json.loads(
        (mock_image_path / "sample-image-info.json").read_text()
    )

    yield {
        "file": mock_image_file,
        "byes": mock_image_file.read_bytes(),
        "info": mock_image_info,
    }
