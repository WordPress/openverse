"""
Determine which files have changed in the documentation preview between
the preview branch and the main branch.

This uses the `diff` CLI utility to determine the list of files that have
changed. It then converts the paths to URLs that can be used to view the
files on the docs preview site. Finally, it outputs the preview site docs
generated comment along with a list of new and changed files.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from shared.actions import write_to_github_output


ORIGINAL_FOLDER = Path("/tmp/gh-pages")
OUTPUT_FOLDER = Path("/tmp/gh-pages-for-diff/")
BASE_URL = "https://docs.openverse.org"
PR_NUMBER = os.environ.get("PR_NUMBER")
EXCLUSIONS = {
    "*.js",
    "*.json",
    "*.html",
    ".*",
    "CNAME",
    "*.pickle",
    "*.doctree",
    "*.inv",
    "*.map",
}


def folder_setup():
    """
    Copy the input folder to the output recursively and delete any existing
    previews.
    """
    print(f"Copying {ORIGINAL_FOLDER} to {OUTPUT_FOLDER} and deleting previews...")
    shutil.copytree(ORIGINAL_FOLDER, OUTPUT_FOLDER, dirs_exist_ok=True)
    shutil.rmtree(OUTPUT_FOLDER / "_preview", ignore_errors=True)


def run_diff() -> str:
    """Use the `diff` CLI utility to determine the list of files that have changed."""
    exclusion_args = [f"--exclude='{exclusion}'" for exclusion in EXCLUSIONS]
    command = " ".join(
        [
            "diff",
            "--brief",
            "--ignore-space-change",
            "--recursive",
            *exclusion_args,
            str(OUTPUT_FOLDER),
            str(ORIGINAL_FOLDER / "_preview" / str(PR_NUMBER)),
        ]
    )
    print(f"Running diff command: {command}")

    completed = subprocess.run(command, capture_output=True, text=True, shell=True)
    # diff returns 0 if there are no differences, 1 if there are differences
    if completed.returncode > 1:
        print("Error running diff:")
        print(completed.stderr)
        sys.exit(1)
    return completed.stdout


def convert_path_to_url(path: str) -> str:
    """
    Convert a path to a URL that can be used to view the file on the docs
    preview site.
    """
    # Remove the piece of the path before _preview
    path = "/_preview/" + path.split("/_preview/")[1]
    # Remove the _sources subfolder
    path = path.replace("/_sources", "")
    # Convert the .md.txt to .html
    path = path.replace(".md.txt", ".html")
    # Prepend the base URL
    return f"{BASE_URL}{path}"


def process_diff(diff_output: str) -> tuple[list[str], list[str]]:
    """
    Parse the output of the `diff` utility and create two lists of files:
    - changed: files that have changed between the two folders
    - new: files that exist in the preview folder but not in the main folder
    """
    changed = []
    new = []
    for line in diff_output.strip().splitlines():
        print(f"Processing line: '{line}'")
        if line.startswith("Files"):
            # e.g.: Files /tmp/gh-pages-for-diff/_sources/meta/index.md.txt and /tmp/gh-pages/_preview/2647/_sources/meta/index.md.txt differ  # noqa: E501
            updated = line.split()[3]
            converted = convert_path_to_url(updated)
            if converted.endswith("html"):
                changed.append(converted)
        elif line.startswith("Only in"):
            if PR_NUMBER not in line:
                continue
            # e.g. Only in /tmp/gh-pages/_preview/2647/_sources/meta: examplefile.md.txt
            added = line.replace(": ", "/").split()[2]
            converted = convert_path_to_url(added)
            if converted.endswith("html"):
                new.append(converted)
    return changed, new


def format_list(items: list[str]) -> str:
    """Format a list of items as a Markdown list."""
    text = "\n".join([f"- {item}" for item in items])
    if len(items) > 10:
        text = f"<details><summary>View full list ({len(items)})</summary>\n\n{text}\n</details>"  # noqa: E501
    return text


def write_output(changed: list[str], new: list[str]):
    """Write the changed and new files to the GitHub output."""
    new_text = "**New files :heavy_plus_sign:**:\n" + format_list(new) if new else ""
    changed_text = (
        "**Changed files :arrows_counterclockwise:**:\n" + format_list(changed)
        if changed
        else ""
    )
    body = f"""\
**Full-stack documentation**: <https://docs.openverse.org/_preview/{PR_NUMBER}>

Please note that GitHub pages takes a little time to deploy newly pushed code, if the links above don't work or you see old versions, wait 5 minutes and try again.

You can check [the GitHub pages deployment action list](https://github.com/WordPress/openverse/actions/workflows/pages/pages-build-deployment) to see the current status of the deployments.

{new_text}

{changed_text}
"""  # noqa: E501
    # This specific syntax makes it possible to write multi-line strings to the
    # GitHub output without having to escape or convert the newlines.
    write_to_github_output(["body<<EOF", body, "EOF"])


if __name__ == "__main__":
    folder_setup()
    diff_output = run_diff()
    print(f"Diff output:\n{diff_output}")
    changed, new = process_diff(diff_output)
    write_output(changed, new)
