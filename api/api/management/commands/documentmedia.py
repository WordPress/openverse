from dataclasses import dataclass
from inspect import getdoc
from pathlib import Path

from django.core.management import BaseCommand
from django.db import connection
from django.db.models import NOT_PROVIDED
from django.db.models.fields import Field

import yaml

from api.models.media import AbstractMedia


PREAMBLE_PATH = Path(__file__).parents[2] / "docs" / "media_properties" / "preamble.md"
OUTPUT_PATH = Path(__file__).parents[3] / "media_properties.md"


@dataclass
class RelationInfo:
    """Store information about a relational field."""

    nature: str
    to: str


@dataclass
class ValueInfo:
    """Store information about a value-based field."""

    allows_blank: bool
    allows_null: bool
    is_pk: bool
    needs_unique: bool
    default: str
    help_text: str


@dataclass
class FieldInfo:
    """Store common information that is applicable to all types of fields."""

    name: str
    field: type[Field]
    db_type: str
    is_relation: bool
    notes: str | None

    relation_info: RelationInfo | None = None
    value_info: ValueInfo | None = None

    @staticmethod
    def dj_docs_url(internal_type: str) -> str | None:
        if internal_type == "ForeignObject":
            # ``ForeignObject`` doesn't have any official documentation.
            return None
        if internal_type == "ArrayField":
            # ``ArrayField`` is a PostgreSQL-specific field.
            return "https://docs.djangoproject.com/en/stable/ref/contrib/postgres/fields/#arrayfield"
        return f"https://docs.djangoproject.com/en/stable/ref/models/fields/#{internal_type.lower()}"

    @property
    def internal_type(self) -> str | tuple[str, str]:
        internal_type = self.field.get_internal_type()
        if internal_type == "ArrayField":
            return internal_type, self.field.base_field.get_internal_type()
        return internal_type

    @property
    def type_repr(self) -> str:
        internal_types = self.internal_type
        if not isinstance(internal_types, tuple):
            internal_types = (internal_types,)
        output = " of ".join(
            f"[`{internal_type}`]({docs})"
            if (docs := FieldInfo.dj_docs_url(internal_type))
            else f"`{internal_type}`"
            for internal_type in internal_types
        )
        return output


def parse_notes(model_class: type[AbstractMedia]) -> dict[str, str]:
    """
    Parse additional notes about model fields from model docstring.

    :param model_class: the model class whose docstring is being parsed
    :return: the mapping of field name to manual notes about the field
    """

    documentation = getdoc(model_class)
    if not documentation:
        return {}

    heading = "Properties\n=========="
    if (pos := documentation.find(heading)) == -1:
        return {}

    props = documentation[pos + len(heading) :].strip()
    info = yaml.safe_load(props)

    return info


def parse_fields(model_class: type[AbstractMedia]) -> list[FieldInfo]:
    """
    Parse the fields from a model class. This function generates a list of
    ``FieldInfo`` objects representing the fields of the model.

    :param model_class: the model class to parse
    :return: a list of ``FieldInfo`` objects
    """

    notes = {}
    for ancestor in reversed(model_class.__mro__):
        notes |= parse_notes(ancestor)

    fields = list(model_class._meta.get_fields())
    fields.sort(key=lambda x: x.name)
    field_infos = []
    for field in fields:
        field_info = FieldInfo(
            name=field.name,
            field=field,
            db_type=field.db_type(connection),
            is_relation=field.is_relation,
            notes=notes.get(field.name),
        )
        field_infos.append(field_info)

        if field_info.is_relation:
            natures = [
                "many_to_many",
                "many_to_one",
                "one_to_many",
                "one_to_one",
            ]
            field_info.relation_info = RelationInfo(
                nature=next(
                    nature for nature in natures if getattr(field, nature, False)
                ),
                to=field.related_model.__name__,
            )
        else:
            field_info.value_info = ValueInfo(
                allows_blank=field.blank,
                allows_null=field.null,
                is_pk=field.primary_key,
                needs_unique=field.unique,
                default=field.default,
                help_text=field.help_text,
            )

    return field_infos


def parse_models() -> dict[str, list[FieldInfo]]:
    """
    Parse all non-abstract descendants of ``AbstractMedia`` that represent media
    types indexed by Openverse and return a mapping of a model to its fields.

    :return: the mapping of a model to a list of its fields
    """

    media_models = AbstractMedia.__subclasses__()
    return {
        model_class.__name__: parse_fields(model_class) for model_class in media_models
    }


def generate_docs(props: dict[str, list[FieldInfo]]) -> str:
    """
    Generate the Markdown output for the media properties. This returns a string
    that can be compared to the existing contents on disk.

    :param props: the mapping of a model to a list of its fields
    :return: the Markdown output for the media properties
    """

    output = ""

    output += PREAMBLE_PATH.read_text()
    output += "\n"

    for model, fields in props.items():
        relations, values = [], []
        for field in fields:
            if field.is_relation:
                relations.append(field)
            else:
                values.append(field)

        notes, noted_fields = generate_notes(model, fields)

        output += f"## {model}\n\n"
        output += generate_relation_table(model, noted_fields, relations)
        output += "\n"
        output += generate_value_table(model, noted_fields, values)
        output += "\n"
        output += notes

    return output


def generate_relation_table(
    model: str,
    noted_fields: set[str],
    relations: list[FieldInfo],
) -> str:
    """
    Generate the data-type table for the relation fields.

    :param model: the parent model of the fields being documented
    :param noted_fields: the set of fields that have associated notes
    :param relations: the list of relation fields
    :return: the table generated for the relation fields
    """

    columns = ["Name", "Type", "DB type", "Nature", "To"]
    table = "### Relations\n\n"
    table += f"|{'|'.join(columns)}|\n"
    table += f"|{'-|'*len(columns)}\n"
    for relation in relations:
        name = f"`{relation.name}`"
        if relation.name in noted_fields:
            name = f"[{name}](#{model}-{relation.name}-notes)"
        cells = (
            name,
            relation.type_repr,
            f"`{relation.db_type}`" if relation.db_type else " ",
            relation.relation_info.nature.replace("_", " ").title(),
            f"`{relation.relation_info.to}`",
        )
        table += f"|{'|'.join(cells)}|\n"
    return table


def generate_value_table(
    model: str,
    noted_fields: set[str],
    values: list[FieldInfo],
) -> str:
    """
    Generate the data-type table for the value fields.

    :param model: the parent model of the fields being documented
    :param noted_fields: the set of fields that have associated notes
    :param values: the list of value fields
    :return: the table generated for the value fields
    """

    columns = ["Name", "Type", "DB type", "Constraints", "Default"]
    table = "### Values\n\n"
    table += f"|{'|'.join(columns)}|\n"
    table += f"|{'-|'*len(columns)}\n"
    for value in values:
        name = f"`{value.name}`"
        if value.name in noted_fields:
            name = f"[{name}](#{model}-{value.name}-notes)"
        cells = (
            name,
            value.type_repr,
            f"`{value.db_type}`" if value.db_type else " ",
            get_constraints(value.value_info),
            f"`{value.value_info.default}`"
            if value.value_info.default != NOT_PROVIDED
            else " ",
        )
        table += f"|{'|'.join(cells)}|\n"
    return table


def generate_notes(model: str, fields: list[FieldInfo]) -> tuple[str, set[str]]:
    """
    Generate notes for the fields. These notes come from the help text and the
    model docstrings.

    :param model: the parent model of the fields being documented
    :param fields: the fields for which to generate notes
    :return: the notes section for all relation and value fields
    """

    output = "### Notes\n\n"

    noted_fields = set()
    for field in fields:
        field_output = f"({model}-{field.name}-notes)=\n"
        field_output += f"#### `{field.name}`\n\n"
        record = False
        if field.notes:
            field_output += f"{field.notes}\n\n"
            record = True
        if not field.is_relation and field.value_info.help_text:
            field_output += f"**Help text:** {field.value_info.help_text}\n\n"
            record = True
        if record:
            noted_fields.add(field.name)
            output += field_output

    return output, noted_fields


def get_constraints(value_info: ValueInfo) -> str:
    """
    Present the constraints in a succinct human-readable format. This function
    inverts the presentation of ``null`` and ``blank`` since they are usually
    ``True``.

    :param value_info: the information for the value field
    :return: a string representing the constraints
    """

    constraints = []
    if not value_info.allows_null:
        constraints.append("not null")
    if not value_info.allows_blank:
        constraints.append("not blank")
    if value_info.needs_unique:
        constraints.append("unique")
    if value_info.is_pk:
        constraints.append("primary key")
    return "; ".join(constraints) or " "


class Command(BaseCommand):
    help = "Update docs for media properties in the documentation site."

    def handle(self, **options):
        props = parse_models()
        docs = generate_docs(props)
        OUTPUT_PATH.write_text(docs)
