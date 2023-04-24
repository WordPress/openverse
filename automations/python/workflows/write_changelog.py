import os
from pathlib import Path


app = os.environ["APP"]
tag_date = os.environ["DATE"]
release_body = os.environ["RELEASE_BODY"]

file_path = Path(__file__).parents[3] / f"documentation/changelogs/{app}/{tag_date}.md"
file_path.write_text(
    f"""
    # {tag_date}

    {release_body}
    """
)
