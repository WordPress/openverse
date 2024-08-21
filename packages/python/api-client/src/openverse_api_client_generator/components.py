from dataclasses import dataclass
from types import NoneType, UnionType
from typing import Any, Iterable, Literal, TypeAlias, Union, get_args
from textwrap import dedent, indent


def py_type_string(t: type | TypeAlias) -> str:
    """Create a string suitable to serve as a Python type annotation"""
    if t is None or t == NoneType:
        return "None"
    elif isinstance(t, UnionType):
        return " | ".join(py_type_string(a) for a in get_args(t))
    elif isinstance(t, Model):
        return t.name
    elif name := getattr(t, "__name__", None):
        if model := _MODEL_REGISTRY.get(name):
            return model.name

        if not get_args(t):
            return name

        return str(t)

    raise ValueError(f"Could not cast {t}")


def ts_type_string(t: type | TypeAlias) -> str:
    if isinstance(t, Model):
        return t.name
    elif t is None or t == NoneType:
        return "null"
    elif t is str:
        return "string"
    elif t is bool:
        return "boolean"
    elif t is bytes:
        return "ReadableStream"
    elif t is int or t is float:
        return "number"
    elif isinstance(t, UnionType):
        return " | ".join(ts_type_string(a) for a in get_args(t))
    elif name := getattr(t, "__name__", None):
        if model := _MODEL_REGISTRY.get(name, None):
            return model.name

        args = get_args(t)

        match name:
            case "Any":
                return "unknown"

            case "Literal":
                return " | ".join([f'"{a}"' for a in args])

            case "list":
                if args:
                    return f"Array<{ts_type_string(args[0])}>"
                return "readonly unknown[]"

            case "tuple":
                if args:
                    tuple_args = ", ".join([ts_type_string(a) for a in args])
                    return f"readonly [{tuple_args}]"
                return "readonly unknown[]"

            case "dict":
                if args:
                    f"Record<string, {ts_type_string(args[-1])}"

                return "Record<string, unknown>"

    raise ValueError(f"Could not cast {t}")


def ts_comment(comment: str, indentation: int = 0) -> str:
    clean_comment = (
        comment.strip().replace(">", "\\>").replace("``", "`").replace("\n", "\n * ")
    )
    return indent(
        dedent(
            f"""
            /**
             * {clean_comment}
             */
            """
        ).strip(),
        " " * indentation,
    )


NO_DEFAULT = object()


@dataclass
class Property:
    name: str
    description: str
    type: type | TypeAlias
    nullable: bool
    required: bool
    default: Any = NO_DEFAULT

    @property
    def py_type_string(self) -> str:
        """Create a string suitable to serve as a Python type annotation"""
        return py_type_string(self.type)

    @property
    def ts_type_string(self) -> str:
        return ts_type_string(self.type)

    @property
    def ts_property_string(self) -> str:
        return "{name}{optional}:{nullable} {type}".format(
            name=self.name,
            optional="?" if not self.required else "",
            nullable=" null |" if self.nullable else "",
            type=self.ts_type_string,
        )

    @property
    def py_parameter_string(self) -> str:
        return "{name}:{nullable} {type}{default}".format(
            name=self.name,
            nullable=" None |" if self.nullable else "",
            type=self.py_type_string,
            default=" | Empty = EMPTY" if not self.required else "",
        )

    @property
    def py_property_string(self) -> str:
        inner_type = f"{'None | ' if self.nullable else ''}{self.py_type_string}"
        return "{name}: {type}".format(
            name=self.name,
            type=inner_type if self.required else f"typing.NotRequired[{inner_type}]",
        )


@dataclass
class Model:
    name: str
    description: str
    properties: dict[str, Property]

    def __post_init__(self):
        _MODEL_REGISTRY[self.name] = self

    @property
    def py_properties(self) -> Iterable[Property]:
        return sorted(self.properties.values(), key=lambda p: not p.required)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


_MODEL_REGISTRY: dict[str, Model] = {}
_ENUMS: dict[str, TypeAlias] = {}


def resolve_ref(ref: str) -> Model | TypeAlias:
    name = ref.split("/")[-1]
    if name in _MODEL_REGISTRY:
        return _MODEL_REGISTRY[name]
    else:
        return _ENUMS[name]


@dataclass
class Route:
    path: str
    method: str
    description: str
    content_type: str

    path_params: dict[str, Property]
    query_params: dict[str, Property]
    request_body: Model | None

    response: type | TypeAlias | Model

    @property
    def json_response(self) -> bool:
        return self.response is not bytes

    @property
    def required_query_params(self) -> list[Property]:
        return [p for p in self.query_params.values() if p.required]

    @property
    def optional_query_params(self) -> list[Property]:
        return [p for p in self.query_params.values() if not p.required]

    @property
    def has_required_query_params(self) -> bool:
        return any(self.required_query_params)

    @property
    def required_body_params(self) -> list[Property]:
        if not self.request_body:
            return []

        return [p for p in self.request_body.properties.values() if p.required]

    @property
    def optional_body_params(self) -> list[Property]:
        if not self.request_body:
            return []

        return [p for p in self.request_body.properties.values() if not p.required]

    @property
    def has_required_body_params(self) -> bool:
        return any(self.required_body_params)

    @property
    def py_route_methodname(self) -> str:
        if self.path in {"/v1/audio/", "/v1/images/"}:
            path = self.path + "search/"
        elif "{identifier}" in self.path:
            # e.g., waveform endpoints
            # should be `get_v1_audio_waveform`
            path = self.path.replace("{identifier}/", "")
        else:
            path = self.path

        # trim the leading and trailing _'s
        path = path.replace("images", "image").replace("/", "_")[1:-1]

        return path

    @property
    def py_cast_content(self) -> str:
        return f"typing.cast({py_type_string(self.response)}, content)"


def python_type_from_schema(schema: dict) -> type | TypeAlias:
    match schema.get("type"):
        case "boolean":
            return bool
        case "string":
            if enum := schema.get("enum"):
                return Literal[*enum]
            return str
        case "integer":
            return int
        case "number":
            return float
        case "array":
            items = schema["items"]
            if not items:
                return list[Any]

            if "$ref" in items:
                return list[resolve_ref(items["$ref"])]

            return list[python_type_from_schema(items)]
        case "object":
            return Any
        case None:
            if "allOf" in schema:
                union_args = [
                    resolve_ref(item["$ref"])
                    if "$ref" in item
                    else python_type_from_schema(item)
                    for item in schema["allOf"]
                ]
                if len(union_args) == 1:
                    return union_args[0]

                return Union[*union_args]

            if "$ref" in schema:
                return resolve_ref(schema["$ref"])

    raise ValueError(f"Unknown type of {schema}")


def model_from_schema(name: str, schema: dict) -> Model:
    if schema.get("enum"):
        _ENUMS[name] = python_type_from_schema(schema)
        return _ENUMS[name]

    properties = {}
    for property_name, property_schema in schema["properties"].items():
        property = Property(
            name=property_name,
            type=python_type_from_schema(property_schema),
            nullable=property_schema.get("nullable", False),
            description=property_schema.get("description", ""),
            required=property_name in schema.get("required", []),
        )
        properties[property_name] = property

    return Model(
        name=name,
        description=schema.get("description", ""),
        properties=properties,
    )


def route_from_schema(path: str, method: str, schema: dict) -> Route:
    query_params = {}
    path_params = {}

    for param_schema in schema.get("parameters", []):
        parameter = Property(
            name=param_schema["name"],
            description=param_schema.get("description", ""),
            type=python_type_from_schema(param_schema["schema"]),
            required=param_schema["in"] == "path"
            or param_schema["name"] in schema.get("required", []),
            nullable=param_schema["in"] == "query"
            and param_schema.get("nullable", False),
            default=param_schema["schema"].get("default", NO_DEFAULT),
        )

        match param_schema["in"]:
            case "query":
                loc = query_params
            case "path":
                loc = path_params

        loc[parameter.name] = parameter

    if content_types := schema.get("requestBody", {}).get("content"):
        if body_schema := content_types.get("application/json"):
            content_type = "application/json"
        elif body_schema := content_types.get("application/x-www-form-urlencoded"):
            content_type = "application/x-www-form-urlencoded"

        if "$ref" in body_schema["schema"]:
            request_body = python_type_from_schema(body_schema["schema"])
        else:
            raise ValueError(f"Unknown request body schema {body_schema}")
    else:
        content_type = "application/json"
        request_body = None

    if ok := schema["responses"].get("200"):
        if "Thumbnail image" == ok.get("description"):
            response = bytes
        else:
            response = python_type_from_schema(
                ok["content"]["application/json"]["schema"]
            )
    elif created := schema["responses"].get("201"):
        response = python_type_from_schema(
            created["content"]["application/json"]["schema"]
        )
    else:
        raise ValueError(f"Unknown response schema {schema['responses']}")

    return Route(
        method=method,
        path=path,
        description=schema.get("description", ""),
        content_type=content_type,
        path_params=path_params,
        query_params=query_params,
        request_body=request_body,
        response=response,
    )
