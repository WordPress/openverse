import os
from pathlib import Path
from textwrap import dedent


app = os.environ["APP"]
tag_date = os.environ["DATE"]
release_body = os.environ["RELEASE_BODY"]

changelog = f"""
# {tag_date}

{release_body}
"""

file_path = Path(__file__).parents[3] / f"documentation/changelogs/{app}/{tag_date}.md"
file_path.write_text(dedent(changelog))
