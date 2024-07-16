import json
import os
import sys
from pathlib import Path
from textwrap import dedent


SHARED_ALIASES = {
    "j": {
        "cmd": ["just"],
        "doc": "A common alias for `just` to save three keystrokes (it adds up!)",
    },
    "nuxt": {
        "cmd": ["j", "p", "frontend", "dev"],
        "doc": "Run the Openverse frontend local development site",
    },
}


# Document alias usage and configuration here. Including it
# in the command makes it easy to discover and noticeable when
# making changes, so it will not go out of sync.
# ov aliases is included in the root `ov` script to help make this visible
# and is mentioned in the general setup documentation
ALIAS_USAGE = """
ov aliases

USAGE
    ov ALIAS [...args]
        Run an aliased command configured for ov.

    ov aliases [--help|-h]
        List all available aliases. If --help is passed, display this help message instead.

DESCRIPTION
    `ov init` creates a ./ov_profile.json file at the root of the repository.
    The "aliases" key of this JSON file should be a dictionary, with alias
    configuration objects as the keys. The configuration object is a dictionary with
    a "cmd" key assigned to a list of command arguments to expand the alias to.
    You may also provide a "doc" key to document the alias. The documentation for
    each alias is displayed by running `ov aliases`.

    To run an alias, pass it as the command argument to ov. To run the built-in "j"
    alias, run `ov j`.

    Only the first argument passed to ov will be expanded using aliases. Aliases can
    stack (that is, repeatedly expand the first argument, if an alias refers to another alias)
    but only ever the leading argument of the expanded alias. For example, the built-in
    alias "nuxt" expands to "j p frontend dev", and ov will expand "j" to "just". However,
    if an alias "p", "frontend", or "dev" existed, ov will not expand those, as they are
    not the leading argument of the expanded arguments list.
""".strip()


def alias_info(aliases: dict, args: list[str]):
    if "--help" in args or "-h" in args:
        print(ALIAS_USAGE)
        return

    # else, assume --list
    output = "ov aliases\n"
    longest_alias = len(sorted(aliases.keys())[-1])
    for alias, cmd in aliases.items():
        if isinstance(cmd, dict):
            doc = cmd["doc"]
            cmd = cmd["cmd"]
        else:
            doc = "No documentation found."

        joined = " ".join(cmd)
        output += dedent(
            f"""
            {alias}{' ' * (longest_alias - len(alias))} -> {joined}
                {doc}
                {'(Built-in alias)' if alias in SHARED_ALIASES else '(Personal alias)'}
            """
        )

    print(output)


def expand_aliases(args: list[str]):
    ov_profile = Path(os.getenv("OPENVERSE_PROJECT")) / ".ov_profile.json"
    aliases = SHARED_ALIASES.copy()
    if ov_profile.is_file():
        aliases |= json.loads(ov_profile.read_text()).get("aliases", {})

    args = sys.argv[1:]

    if args[0] == "aliases":
        return alias_info(aliases, args)

    while args[0] in aliases:
        alias = aliases.pop(args[0])
        if isinstance(alias, dict):
            args = alias["cmd"] + args[1:]
        else:
            args = alias + args[1:]

    return args


if __name__ == "__main__":
    args = expand_aliases(sys.argv[1:])
    try:
        if args is not None:
            os.execvp(args[0], args)
    except FileNotFoundError:
        print(f"{args[0]}: command not found")
        exit(1)
    else:
        exit(0)
