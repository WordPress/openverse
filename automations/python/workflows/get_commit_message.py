import os

from shared.actions import write_to_github_output


def main() -> None:
    """
    Get the COMMIT_MESSAGE environment variable and convert it into a single
    line of text, with quote characters escaped.

    This is necessary because GitHub Actions does not provide any functions for string
    manipulation and interpolating this wholesale into the JSON client payload
    will cause the workflow to fail since it's not valid JSON.
    """
    commit_message = os.environ["COMMIT_MESSAGE"]
    # Split newlines
    message = commit_message.split("\n", 1)[0]
    # Escape quotes
    message = message.replace('"', '\\"')
    write_to_github_output([f"commit_message={message}"])


if __name__ == "__main__":
    main()
