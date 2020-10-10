from common import urls

from abc import ABC, abstractmethod
import json
import logging

logger = logging.getLogger(__name__)


class Column(ABC):
    """
    Implementations of this base class represent columns in a PostgreSQL DB.

    Each implementation must implement a `prepare_string` method to
    properly format data for a given column type.
    """
    def __init__(self, name: str, required: bool):
        self.NAME = name
        self.REQUIRED = required

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
            return ' '.join(
                str(data)
                .replace('"', "'")
                .replace('\b', '')
                .replace('\\', '\\\\')
                .split()
            )

    def __enforce_char_limit(self, string, limit, truncate=True):
        if not type(string) == str:
            logger.debug(
                f'Cannot limit characters on non-string type {type(string)}.'
                f'Input was {string}.'
            )
            return None
        if len(string) > limit:
            logger.warning(
                f'String over char limit of {limit}.  Input was {string}.'
            )
            return string[:limit] if truncate else None
        else:
            return string


class IntegerColumn(Column):
    """
    Represents a PostgreSQL column of type integer.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    """

    def prepare_string(self, value):
        """
        Returns a string representation to the best integer approx of input.

        If there is no sane mapping from the input to an integer,
        returns None.

        value: for useful output this should be reasonably castable to an int.
        """
        try:
            number = str(int(float(value)))
        except Exception as e:
            logger.debug(
                f'input {value} is not castable to an int.  The error was {e}'
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

    def prepare_string(self, value):
        """
        Returns a string `t` or `f`, as appropriate to input.

        If there is no sane mapping from the input to a boolean,
        returns None.

        value: for useful output this should be reasonably castable to a bool.
        """
        bool_map = {
            't': [True, 'true', 'True', 't', 'T'],
            'f': [False, 'false', 'False', 'f', 'F']
        }
        for tf in bool_map:
            if value in bool_map[tf]:
                return tf
        logger.debug(
            f'{value} is not a valid PostgreSQL bool'
        )
        return None


class JSONColumn(Column):
    """
    Represents a PostgreSQL column of type jsonb.

    name:      name of the corresponding column in the DB
    required:  whether the column should be considered required by the
               instantiating script.  (Not necessarily mapping to
               `not null` columns in the PostgreSQL table)
    """

    def prepare_string(self, value):
        """
        Returns a json string as appropriate to input.

        Also sanitizes values within the json to ensure they are
        loadable into a PostgreSQL table.

        If given empty input, returns None.

        value: lists and dicts will be turned into json,
               other input will be turned into sanitized strings.
        """
        sanitized_json = self._sanitize_json_values(value)
        return json.dumps(sanitized_json, ensure_ascii=False) if sanitized_json else None

    def _sanitize_json_values(self, value, recursion_limit=100):
        """
        Recursively sanitizes the non-dict, non-list values of an input
        dictionary or list in preparation for dumping to JSON string.
        """
        input_type = type(value)

        if value is None:
            return value
        elif input_type not in [dict, list] or recursion_limit <= 0:
            return self._Column__sanitize_string(value)
        elif input_type == list:
            return [
                self._sanitize_json_values(
                    item,
                    recursion_limit=recursion_limit - 1
                )
                for item in value
            ]
        else:
            return {
                key: self._sanitize_json_values(
                    val,
                    recursion_limit=recursion_limit - 1
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

    def __init__(self, name: str, required: bool, size: int, truncate: bool):
        self.SIZE = size
        self.TRUNCATE = truncate
        super().__init__(name, required)

    def prepare_string(self, value):
        """
        Sanitizes input and enforces the character limit, returning a string.
        """
        return self._Column__enforce_char_limit(
            self._Column__sanitize_string(value),
            self.SIZE,
            self.TRUNCATE
        )


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
    def __init__(self, name: str, required: bool, size: int):
        self.SIZE = size
        super().__init__(name, required)

    def prepare_string(self, value):
        """
        Returns input unchanged, as long as it is a valid URL string.

        Also enforces the character limit of the column. If the input
        value fails a validation, returns None.
        """
        if self._Column__sanitize_string(value) != value:
            return None
        else:
            return self._Column__enforce_char_limit(
                urls.validate_url_string(value),
                self.SIZE,
                False
            )
