import json
import os
import sys
from pathlib import Path


SHARED_ALIASES = {
    "j": ["just"],
    "nuxt": ["j", "p", "frontend", "dev"],
}


def expand_aliases(args: list[str]):
    ov_aliases = Path(os.getenv("OPENVERSE_PROJECT")) / ".ov_aliases.json"
    aliases = SHARED_ALIASES
    if ov_aliases.is_file():
        aliases |= json.loads(ov_aliases.read_text())

    args = sys.argv[1:]

    while args[0] in aliases:
        args = aliases.pop(args[0]) + args[1:]

    return args


if __name__ == "__main__":
    args = expand_aliases(sys.argv[1:])
    try:
        os.execvp(args[0], args)
    except FileNotFoundError:
        sys.stdout.buffer.write(args[0].encode() + b": command not found\n")
