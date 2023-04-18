import os


app = os.environ["APP"]
tag_date = os.environ["DATE"]
release_body = os.environ["RELEASE_BODY"]

file_path = f"documentation/changelogs/{app}/{tag_date}.md"

with open(file_path, "w") as f:
    f.write(f"# {tag_date}\n\n")
    f.write(f"""{release_body}\n""")
