import os
import sys


def write_to_github_output(lines: list[str]) -> None:
    """
    Write a list of strings to both stdout and the GITHUB_OUTPUT environment variable.
    Useful for GitHub Actions, although lines must be formatted as `key=value`.
    """
    with open(
        os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a", encoding="utf-8"
    ) as gh_out:
        for dest in [sys.stdout, gh_out]:
            for line in lines:
                print(line, file=dest)
