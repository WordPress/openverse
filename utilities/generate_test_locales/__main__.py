import json
import re
from pathlib import Path

import argostranslate.package
import argostranslate.translate


reporoot = Path(__file__).parents[2]

from_lang = "en"

# Must be generated using `just p frontend i18n:en`
from_json_path = reporoot / "frontend" / "src" / "locales" / "en.json"

to_langs = ["ar", "es"]
to_json_paths = {
    lang: reporoot / "frontend" / "test" / "locales" / f"{lang}.json"
    for lang in to_langs
}


def install_packages():
    print("Updating package index")
    argostranslate.package.update_package_index()

    print("Retrieving available packages")
    available_packages = argostranslate.package.get_available_packages()

    print("Reading installed packages")
    installed_packages = argostranslate.package.get_installed_packages()

    for to_lang in to_langs:
        lang_package = next(
            filter(
                lambda x: x.from_code == from_lang and x.to_code == to_lang,
                available_packages,
            )
        )

        if lang_package not in installed_packages:
            print(
                f"{lang_package} is unavailable or out of date; installing the latest version now"
            )
            lang_package.install()

    print("Finished installing packages\n")


def _flatten_dict(d: dict[str, str | dict]) -> dict[str, str]:
    flat = {}

    for key, value in d.items():
        if isinstance(value, dict):
            inner_flattened = _flatten_dict(value)
            for inner_key, inner_value in inner_flattened.items():
                flat[f"{key}.{inner_key}"] = inner_value
        else:
            flat[key] = value

    return flat


def _flat_json(p: Path) -> dict[str, str]:
    return _flatten_dict(json.loads(p.read_text()))


def _explode_dict(d: dict[str, str]) -> dict[str, str | dict]:
    exploded = {}

    for path, value in d.items():
        path_segments = path.split(".")
        destination = exploded
        for segment in path_segments[:-1]:
            if segment not in destination:
                destination[segment] = {}
            destination = destination[segment]
        destination[path_segments[-1]] = value

    return exploded


def _explode_json(d: dict[str, str]) -> str:
    return json.dumps(_explode_dict(d), ensure_ascii=False, indent=2)


placeholders_pattern = re.compile(r"\{.*?\}")


def generate_test_locales():
    print("Generating test locales")
    from_json: dict[str, str | dict] = _flat_json(from_json_path)

    to_jsons: dict[str, dict[str, str | dict]] = {
        lang: _flat_json(p) for lang, p in to_json_paths.items()
    }

    new_to_jsons: dict[str, dict[str, str | dict]] = {
        to_lang: {} for to_lang in to_langs
    }

    # Traverse from_json
    # For each key, determine if that key is in the each to_json.
    # If it is, copy that value into `new_to_jsons`
    # If not, generate it using argos

    for key, from_value in from_json.items():
        placeholders = []

        def replace_placeholder_with_translatable_text(m: re.Match):
            """
            Replace placeholders with "PLACEHOLDER" text, which can be translated.

            Previous attempts tried to find a placeholder that argos would respect.
            However, argos, being a machine translation tool, does not have any
            support for placeholders/variable interpolation. That makes sense,
            because for it to be possible, we'd need to mark several grammatical details
            about the role each variable plays in a sentence.

            Using the all-caps "PLACEHOLDER" means Argos will not fail to translate
            the string, and in all likelihood most of the string will still make
            _some_ sense, or at least be a vague approximation of what the actual string
            would be in production (most importantly, to match a reasonable length).
            """
            placeholders.append(m.group(0))
            return "PLACEHOLDER"

        safe_value = placeholders_pattern.sub(
            replace_placeholder_with_translatable_text, from_value
        )

        print(f"Picking translations for {key}")
        for to_lang, to_json in to_jsons.items():
            new_to_json = new_to_jsons[to_lang]
            if key in to_json:
                print(f"Reusing existing {to_lang} value for {key}")
                new_to_json[key] = to_json[key]
            else:
                print(f"Translating {key} to {to_lang}")
                new_to_json[key] = argostranslate.translate.translate(
                    safe_value, from_lang, to_lang
                )

    for lang, new_to_json in new_to_jsons.items():
        out = to_json_paths[lang]
        new_json = _explode_json(new_to_json)
        out.unlink(missing_ok=True)
        out.write_text(f"{new_json}\n")


if __name__ == "__main__":
    install_packages()
    generate_test_locales()
