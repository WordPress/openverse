class Md:
    horizontal_line = "\n----\n\n"

    @staticmethod
    def heading(level: int, text: str) -> str:
        """Add a heading to a markdown string."""
        return f"{'#' * level} {text}\n"

    @staticmethod
    def line(text: str) -> str:
        """Add a line to a markdown string."""
        return f"{text}\n"

    @staticmethod
    def parse(text: str) -> dict[str, dict[str, str]]:
        """
        Parse the text content of the markdown documentation file and return a dictionary with the
        field name as key and the description as value.
        """
        contents = [line for line in text.split("\n") if line.strip()]
        current_field = ""
        properties = {}
        prop = ""
        value = {}
        for i, line in enumerate(contents):
            if line.startswith("# "):
                if current_field and value:
                    properties[current_field] = value
                current_field = line.replace("# ", "").strip()
                value = {}
            elif line.startswith("## "):
                if prop and prop in value:
                    value[prop] = value[prop].strip()
                prop = line.replace("## ", "").strip()
                value[prop] = ""
            elif not prop:
                continue
            elif i == len(contents) - 1:
                value[prop] = f"{value[prop]}{line}".strip()
                properties[current_field] = value
            else:
                value[prop] += line

        return properties
