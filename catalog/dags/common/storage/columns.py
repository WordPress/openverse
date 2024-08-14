import json
import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from textwrap import dedent
from typing import NewType


logger = logging.getLogger(__name__)

NOW = "NOW()"
FALSE = "'f'"
NULL = "NULL"


class Datatype(Enum):
    bool = "boolean"
    char = "character"
    int = "integer"
    jsonb = "jsonb"
    timestamp = "timestamp with time zone"
    uuid = "uuid"
    double = "double precision"


class UpsertStrategy(Enum):
    now = auto()
    false = auto()
    newest_non_null = auto()
    merge_jsonb_objects = auto()
    merge_jsonb_arrays = auto()
    merge_array = auto()
    merge_tags = auto()
    no_change = ()
    calculate_value = auto()


Datatypes = NewType("Datatype", Datatype)
UpsertStrategies = NewType("UpsertStrategy", UpsertStrategy)


def _calculate_value(function: str, prefix: str, *args) -> str:
    """
    Return SQL to calculate the value by calling the given
    function with the given args.
    """
    if args:
        arguments = ", ".join([prefix + str(arg) for arg in args])
        return f"{function}({arguments})"

    # Handle function with no args
    return f"{function}()"


def _newest_non_null(column: str) -> str:
    return f"{column} = COALESCE(EXCLUDED.{column}, old.{column})"


def _merge_jsonb_objects(column: str) -> str:
    """
    Return an SQL that merges the top-level keys of a JSONB column.
    This takes the newest available non-null value.
    """
    return f"""{column} = COALESCE(
           jsonb_strip_nulls(old.{column})
             || jsonb_strip_nulls(EXCLUDED.{column}),
           EXCLUDED.{column},
           old.{column}
         )"""


def _merge_jsonb_arrays(column: str) -> str:
    return f"""{column} = COALESCE(
           (
             SELECT jsonb_agg(DISTINCT x)
             FROM jsonb_array_elements(old.{column} || EXCLUDED.{column}) t(x)
           ),
           EXCLUDED.{column},
           old.{column}
         )"""


def _merge_array(column: str) -> str:
    return f"""{column} = COALESCE(
       (
         SELECT array_agg(DISTINCT x)
         FROM unnest(old.{column} || EXCLUDED.{column}) t(x)
       ),
       EXCLUDED.{column},
       old.{column}
       )"""


def _merge_tags(*args) -> str:
    """
    Merge provider tags with additional tags.

    Always keep all additional tags, but never retain previous provider tags,
    to ensure any provider tags during reingestion exactly match those at
    the provider, and no tags deleted or changed upstream are incorrectly retained
    in Openverse.

    See https://github.com/WordPress/openverse/issues/4732 for rationale.

    This approach applies to media table tags. As such, the column name is not configurable.
    Other jsonb array columns with similar needs must implement their own strategies to
    sound merging of incoming and existing values.

    Table name `old` comes from `upsert_records_to_db_table` implementation details.
    `EXCLUDED` is because this is interpolated into `DO UPDATE SET`.
    """
    return dedent(
        """
        tags = COALESCE(
            (
                SELECT EXCLUDED.tags || jsonb_path_query_array(
                    old.tags,
                    '$ ? (@.provider != $provider)',
                    jsonb_build_object('provider', old.provider)
                )
            ),
            EXCLUDED.tags,
            old.tags
        )
        """
    ).strip()


def _now(column: str):
    return f"{column} = {NOW}"


def _false(column):
    return f"{column} = {FALSE}"


class Column(ABC):
    """
    Implementations of this base class represent columns in a PostgreSQL DB.

    Each implementation must implement a `prepare_string` method to
    properly format data for a given column type.
    """

    strategies = {
        UpsertStrategy.newest_non_null: _newest_non_null,
        UpsertStrategy.now: _now,
        UpsertStrategy.false: _false,
        UpsertStrategy.merge_jsonb_objects: _merge_jsonb_objects,
        UpsertStrategy.merge_jsonb_arrays: _merge_jsonb_arrays,
        UpsertStrategy.merge_array: _merge_array,
        UpsertStrategy.merge_tags: _merge_tags,
    }

    def __init__(
        self,
        name: str,
        required: bool,
        datatype: Datatype = Datatype.char,
        upsert_strategy: UpsertStrategy | None = UpsertStrategy.newest_non_null,
        constraint: str | None = None,
        db_name: str | None = None,
        nullable: bool | None = None,
    ):
        """
        Initialize a column.

        :param name: The column name used in TSV, ImageStore and provider API scripts,
        can be different from the name in the database.
        :param required: If True, the database column will be set to 'NOT NULL'
        :param datatype: Postgres datatype representation
        :param upsert_strategy: Shows the strategy used when the data for a media item
        is re-ingested: Simple values are replaced with newer non-null values,
        json and array values are merged, some timestamps are set to the execution time.
        :param constraint: Column constraint in database
        :param db_name: Column name in database, if different from TSV name
        """
        self.name = name
        self.required = required
        self.datatype = datatype
        self.upsert_strategy = upsert_strategy
        self.constraint = constraint
        self.db_name = db_name or name
        self.nullable = nullable if nullable is not None else not required

    def __str__(self):
        return f"{type(self).__name__} {self.name}"

    @abstractmethod
    def prepare_string(self, value):
        """
        Return a string to be imported to the corresponding field in the DB.

        Return Nonetype if the eventual column in the DB should be Null.
        """
        pass

    def __sanitize_string(self, data):
        if data is None:
            return None
        else:
            # We join a split string because it removes all whitespace
            # characters
            return " ".join(
                str(data)
                .replace('"', "'")
                .replace("\b", "")
                .replace("\\", "\\\\")
                .split()
            )

    def __enforce_char_limit(self, string, limit, truncate=True):
        if not isinstance(string, str):
            logger.debug(
                f"Cannot limit characters on non-string type {type(string)}."
                f"Input was {string}."
            )
            return None
        if len(string) > limit:
            logger.warning(f"String over char limit of {limit}.  Input was {string}.")
            return string[:limit] if truncate else None
        else:
            return string

    def get_insert_value(self, *args):
        """Return the string used for this column in an INSERT statement."""
        if self.upsert_strategy == UpsertStrategy.now:
            return NOW
        elif self.upsert_strategy == UpsertStrategy.false:
            return FALSE
        else:
            return self.db_name

    def get_update_value(self, *args):
        """Return the string used for this column in the UPDATE statement."""
        strategy = Column.strategies.get(self.upsert_strategy)
        if strategy is None:
            logging.warning(
                f"Unrecognized column {self.name}; setting to NULL during upsert"
            )
            return NULL
        else:
            return strategy(self.db_name)

    def create_definition(self, is_loading: bool):
        dt = self.datatype.value
        constraint = "" if self.constraint is None else f" {self.constraint}"
        nullable = ""
        if not is_loading and not self.nullable:
            nullable = " NOT NULL"
        return f"{self.db_name} {dt}{constraint}{nullable}"


class IntegerColumn(Column):
    """
    Represents a PostgreSQL column of type integer.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    """

    def __init__(
        self,
        name: str,
        required: bool,
        constraint: str | None = None,
        db_name: str | None = None,
    ):
        super().__init__(
            name,
            required,
            datatype=Datatype.int,
            upsert_strategy=UpsertStrategy.newest_non_null,
            constraint=constraint,
            db_name=db_name,
        )

    def prepare_string(self, value):
        """
        Return a string representation to the best integer approx of input.

        If there is no reasonable mapping from the input to an integer,
        returns None.

        value: for useful output this should be reasonably castable to an int.
        """
        try:
            number = str(int(float(value)))
        except (TypeError, ValueError) as e:
            logger.debug(f"input {value} is not castable to an int.  The error was {e}")
            number = None
        return number


class CalculatedColumn(Column):
    """
    A specially handled PostgreSQL column of type double precision, which
    is always calculated at insertion and update.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    sql_args:  optionally, a list of string arguments passed to the SQL
               function used to calculate the column value
    """

    def __init__(
        self,
        name: str,
        required: bool,
        sql_args: list[str] | None = None,
        constraint: str | None = None,
        db_name: str | None = None,
    ):
        super().__init__(
            name,
            required,
            datatype=Datatype.double,
            upsert_strategy=UpsertStrategy.calculate_value,
            constraint=constraint,
            db_name=db_name,
        )
        self.sql_args = sql_args

    def get_insert_value(self, sql_function, prefix=""):
        """
        Return the string used for this column in an INSERT statement.

        For a calculated column, this will be a call to the SQL function with the
        given arguments, with no prefix applied. E.g.:

        `standardized_image_popularity(provider, meta_data)`
        """
        return _calculate_value(sql_function, prefix, *self.sql_args)

    def get_update_value(self, sql_function):
        """
        Return the string used for this column in an UPDATE statement, when there is
        a conflict during INSERT.

        For a calculated column, this will be an assignment to the SQL function with
        the given arguments, with the `EXCLUDED.` prefix applied: this indicates that
        in the upsert, the columns used as arguments should come from the new row we
        are attempting to upsert, rather than the existing data (i.e., we should use the
        more up-to-date information). E.g.:

        ```
        standardized_popularity = standardized_image_popularity(
            EXCLUDED.provider, EXCLUDED.meta_data
        )
        ```
        """
        function_call = self.get_insert_value(sql_function, prefix="EXCLUDED.")
        return f"{self.db_name} = {function_call}"

    def prepare_string(self, value):
        """
        Return a string representation to the best float approx of input.

        If there is no reasonable mapping from the input to a float,
        returns None.

        value: for useful output this should be reasonably castable to a float.
        """
        try:
            number = str(float(value))
        except (TypeError, ValueError) as e:
            logger.debug(
                f"input {value} is not castable to a float.  The error was {e}"
            )
            number = None
        return number


class BooleanColumn(Column):
    """
    Represents a PostgreSQL column of type boolean.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    """

    def __init__(
        self,
        name: str,
        required: bool,
        upsert_strategy: UpsertStrategy | None = UpsertStrategy.newest_non_null,
        constraint: str | None = None,
        db_name: str | None = None,
    ):
        super().__init__(
            name,
            required,
            datatype=Datatype.bool,
            upsert_strategy=upsert_strategy,
            constraint=constraint,
            db_name=db_name,
        )
        self.constraint = constraint

    def prepare_string(self, value):
        """
        Return a string `t` or `f`, as appropriate to input.

        If there is no reasonable mapping from the input to a boolean,
        returns None.

        value: for useful output this should be reasonably castable to a bool.
        """
        bool_map = {
            "t": [True, "true", "True", "t", "T"],
            "f": [False, "false", "False", "f", "F"],
        }
        for tf in bool_map:
            if value in bool_map[tf]:
                return tf
        logger.debug(f"{value} is not a valid PostgreSQL bool")
        return None


class JSONColumn(Column):
    """
    Represents a PostgreSQL column of type jsonb.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    """

    def __init__(
        self,
        name: str,
        required: bool,
        db_name: str | None = None,
        upsert_strategy: UpsertStrategy | None = None,
    ):
        strategy = upsert_strategy or UpsertStrategy.merge_jsonb_objects
        super().__init__(
            name,
            required,
            datatype=Datatype.jsonb,
            upsert_strategy=strategy,
            db_name=db_name,
            constraint=None,
        )

    def prepare_string(self, value):
        """
        Return a json string as appropriate to input.

        Also sanitizes values within the json to ensure they are
        loadable into a PostgreSQL table.

        If given empty input, returns None.

        value: lists and dicts will be turned into json,
               other input will be turned into sanitized strings.
        """
        sanitized_json = self._sanitize_json_values(value)
        return (
            json.dumps(sanitized_json, ensure_ascii=False) if sanitized_json else None
        )

    def _sanitize_json_values(self, value, recursion_limit=100):
        """
        Recursively sanitize the non-dict/non-list values of an input dict or list in
        preparation for dumping to a JSON string.
        """
        input_type = type(value)

        if value is None:
            return value
        elif input_type not in [dict, list] or recursion_limit <= 0:
            return self._Column__sanitize_string(value)
        elif input_type is list:
            return [
                self._sanitize_json_values(item, recursion_limit=recursion_limit - 1)
                for item in value
            ]
        else:
            return {
                key: self._sanitize_json_values(
                    val, recursion_limit=recursion_limit - 1
                )
                for key, val in value.items()
            }


class StringColumn(Column):
    """
    Represents a PostgreSQL column of type varchar.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    size:      width of the varchar in the table.  Erring on the small
               side is fine, but setting this value larger than the
               width of the corresponding column in the table is not
               recommended.
    truncate:  Whether or not it's acceptable to truncate the input to
               fit within the required size.  If not, input over the
               limit will be mapped to None.
    """

    def __init__(
        self,
        name: str,
        required: bool,
        size: int,
        truncate: bool,
        db_name: str | None = None,
    ):
        self.SIZE = size
        self.TRUNCATE = truncate
        super().__init__(
            name,
            required,
            datatype=Datatype.char,
            upsert_strategy=UpsertStrategy.newest_non_null,
            constraint=f"varying({size})",
            db_name=db_name,
        )

    def prepare_string(self, value):
        """Sanitizes input and enforces the character limit, returning a string."""
        return self._Column__enforce_char_limit(
            self._Column__sanitize_string(value), self.SIZE, self.TRUNCATE
        )


class UUIDColumn(Column):
    """
    Represents the PrimaryKey `identifier` column in PostgreSQL.

    name:          Column name
    """

    def __init__(self, name: str):
        super().__init__(
            name,
            required=True,
            datatype=Datatype.uuid,
            upsert_strategy=None,
            constraint="PRIMARY KEY DEFAULT public.uuid_generate_v4()",
        )

    def prepare_string(self, value):
        return value


class TimestampColumn(Column):
    """
    Represents a PostgreSQL column of type `timestamp with time zone`.

    name:             Column name
    required:         If True, `NOT NULL` constraint is added
    upsert_strategy:  Strategy to use for data for a media item is re-ingested,
                      one of the UpsertStrategy. Default is to replace with `NOW()`
    """

    def __init__(
        self,
        name: str,
        required: bool,
        upsert_strategy: UpsertStrategy | None = None,
    ):
        super().__init__(
            name,
            required=required,
            datatype=Datatype.timestamp,
            upsert_strategy=upsert_strategy or UpsertStrategy.now,
        )

    def get_insert_value(self, *args):
        return NOW

    def prepare_string(self, value):
        return value


class URLColumn(Column):
    """
    Represents a PostgreSQL column of type varchar, which should hold a URL.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    size:      width of the varchar in the table.  Erring on the small
               side is fine, but setting this value larger than the
               width of the corresponding column in the table is not
               recommended.

    Note:  Different from StringColumn in that we *never* truncate a URL
           string.
    """

    def __init__(
        self,
        name: str,
        required: bool,
        size: int,
        nullable: bool = False,
        db_name: str | None = None,
    ):
        self.SIZE = size
        super().__init__(
            name,
            required,
            datatype=Datatype.char,
            upsert_strategy=UpsertStrategy.newest_non_null,
            constraint=f"varying({size})",
            db_name=db_name,
            nullable=nullable,
        )

    def prepare_string(self, value):
        """
        Return input unchanged, as long as it is a valid URL string.

        Also enforces the character limit of the column. If the input
        value fails a validation, returns None.
        """
        if self._Column__sanitize_string(value) != value:
            return None
        else:
            return self._Column__enforce_char_limit(value, self.SIZE, False)


class ArrayColumn(Column):
    """
    Represents a PostgreSQL column of type Array.

    Arrays should hold elements of the given base_column type.

    name:           name of the corresponding column in the DB
    required:       whether the column should be considered required by the
                    instantiating script.  (Not necessarily mapping to
                    `not null` columns in the PostgreSQL table)
    base_column:    type of the elements in the array, another column
    """

    def __init__(
        self,
        name: str,
        required: bool,
        base_column: Column,
        db_name: str | None = None,
    ):
        self.base_column = base_column
        super().__init__(
            name,
            required,
            datatype=Datatype.char,
            upsert_strategy=UpsertStrategy.merge_array,
            constraint="varying(80)[]",
            db_name=db_name,
        )

    def prepare_string(self, value):
        """
        Return a string representation of an array.

        The format in PostgreSQL is: `{<item 1>, <item 2>...}`.
        Apply changes and validations of the corresponding base column type.
        """
        input_type = type(value)

        if value is None:
            return value
        elif input_type is not list:
            arr_str = self.base_column.prepare_string(value)
            return "{" + arr_str + "}" if arr_str else None

        values = []
        for val in value:
            if val is None:
                values.append(None)
            else:
                values.append(self.base_column.prepare_string(val))
        arr_str = json.dumps(values, ensure_ascii=False)
        return "{" + arr_str[1:-1] + "}" if arr_str else None


FOREIGN_ID = StringColumn(
    name="foreign_identifier",
    required=True,
    size=3000,
    truncate=False,
)
LANDING_URL = URLColumn(
    name="foreign_landing_url", required=True, size=1000, nullable=True
)
DIRECT_URL = URLColumn(
    # `url` in DB
    name="url",
    required=True,
    size=3000,
    db_name="url",
)
THUMBNAIL = URLColumn(
    # `thumbnail` in DB
    name="thumbnail_url",
    required=False,
    size=3000,
    db_name="thumbnail",
)
FILESIZE = IntegerColumn(name="filesize", required=False)
LICENSE = StringColumn(
    name="license_", required=True, size=50, truncate=False, db_name="license"
)
LICENSE_VERSION = StringColumn(
    name="license_version", required=True, size=25, truncate=False
)
CREATOR = StringColumn(name="creator", required=False, size=2000, truncate=True)
CREATOR_URL = URLColumn(name="creator_url", required=False, size=2000)
TITLE = StringColumn(name="title", required=False, size=5000, truncate=True)
META_DATA = JSONColumn(name="meta_data", required=False)
TAGS = JSONColumn(
    name="tags", required=False, upsert_strategy=UpsertStrategy.merge_tags
)
WATERMARKED = BooleanColumn(name="watermarked", required=False)
PROVIDER = StringColumn(name="provider", required=False, size=80, truncate=False)
SOURCE = StringColumn(name="source", required=False, size=80, truncate=False)
INGESTION_TYPE = StringColumn(
    name="ingestion_type", required=False, size=80, truncate=False
)
WIDTH = IntegerColumn(name="width", required=False)
HEIGHT = IntegerColumn(name="height", required=False)

DURATION = IntegerColumn(name="duration", required=False)
BIT_RATE = IntegerColumn(
    name="bit_rate",
    required=False,
)

SAMPLE_RATE = IntegerColumn(
    name="sample_rate",
    required=False,
)
CATEGORY = StringColumn(
    name="category",
    required=False,
    size=80,
    truncate=False,
)
GENRES = ArrayColumn(
    name="genres",
    required=False,
    base_column=StringColumn(name="genre", required=False, size=80, truncate=False),
)
AUDIO_SET = JSONColumn(
    # set name, thumbnail, url, identifier etc.
    name="audio_set",
    required=False,
)
SET_POSITION = IntegerColumn(
    name="set_position",
    required=False,
)
ALT_FILES = JSONColumn(
    # Alternative files: url, filesize, bit_rate, sample_rate
    name="alt_files",
    required=False,
    upsert_strategy=UpsertStrategy.merge_jsonb_arrays,
)

IDENTIFIER = UUIDColumn(
    name="identifier",
)

CREATED_ON = TimestampColumn(
    name="created_on", required=True, upsert_strategy=UpsertStrategy.no_change
)

UPDATED_ON = TimestampColumn(
    name="updated_on",
    required=True,
)

LAST_SYNCED = TimestampColumn(name="last_synced_with_source", required=False)

REMOVED = BooleanColumn(
    name="removed_from_source", required=True, upsert_strategy=UpsertStrategy.false
)

FILETYPE = StringColumn(name="filetype", required=False, truncate=False, size=5)

STANDARDIZED_POPULARITY = CalculatedColumn(
    name="standardized_popularity",
    required=False,
    sql_args=[PROVIDER.db_name, META_DATA.db_name],
)

AUDIO_SET_FOREIGN_IDENTIFIER = StringColumn(
    name="audio_set_foreign_identifier",
    required=False,
    size=1000,
    truncate=False,
)

# Columns used by the Deleted Media tables

DELETED_ON = TimestampColumn(
    name="deleted_on", required=True, upsert_strategy=UpsertStrategy.no_change
)

DELETED_REASON = StringColumn(
    name="deleted_reason", required=True, size=80, truncate=True
)
