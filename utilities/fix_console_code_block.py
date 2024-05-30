import re
import sys
from pathlib import Path


CONSOLE_BLOCK = re.compile("```console")


def main(paths: list[str]):
    for path in paths:
        file = Path(path)
        text = file.read_text()
        replaced, count = CONSOLE_BLOCK.subn(
            "```bash",
            text,
        )
        if count:
            file.write_text(replaced)


if __name__ == "__main__":
    main(sys.argv[1:])
