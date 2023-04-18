import os


app = os.environ["INPUTS_APP"]
tag_date = os.environ["STEPS_TAG_OUTPUTS_DATE"]
release_body = os.environ["STEPS_RELEASE_DRAFTER_OUTPUTS_BODY"]

file_path = f"documentation/changelogs/{app}/{tag_date}.md"

with open(file_path, "w") as f:
    f.write(f"# {tag_date}\n\n")
    f.write(f"""{release_body}\n""")
