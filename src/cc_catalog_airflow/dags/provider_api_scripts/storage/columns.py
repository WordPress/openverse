from storage import util

from abc import ABC, abstractmethod
import json
import logging

logger = logging.getLogger(__name__)


class Column(ABC):
    def __init__(self, name: str, required: bool):
        self.NAME = name
        self.REQUIRED = required

    @abstractmethod
    def prepare_string(self, value):
        """
        This method should return Nonetype if the eventual column should
        be Null.
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
                'Cannot limit characters on non-string type {}.  Input was {}.'
                .format(type(string), string)
            )
            return None
        if len(string) > limit:
            logger.warning(
                'String over char limit of {}.  Input was {}.'
                .format(limit, string)
            )
            return string[:limit] if truncate else None
        else:
            return string


class IntegerColumn(Column):

    def prepare_string(self, value):
        try:
            number = str(int(float(value)))
        except Exception as e:
            logger.debug(
                'input {} is not castable to an int.  The error was {}'
                .format(value, e)
            )
            number = None
        return number


class BooleanColumn(Column):

    def prepare_string(self, value):
        if value in ['t', 'f']:
            return value
        else:
            logger.debug(
                '{} is not a valid PostgreSQL bool'.format(value)
            )
            return None


class JSONColumn(Column):

    def prepare_string(self, value):
        sanitized_json = self._sanitize_json_values(value)
        return json.dumps(sanitized_json) if sanitized_json else None

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
    def __init__(self, name: str, required: bool, size: int, truncate: bool):
        self.SIZE = size
        self.TRUNCATE = truncate
        super().__init__(name, required)

    def prepare_string(self, value):
        return self._Column__enforce_char_limit(
            self._Column__sanitize_string(value),
            self.SIZE,
            self.TRUNCATE
        )


class URLColumn(Column):
    def __init__(self, name: str, required: bool, size: int):
        self.SIZE = size
        super().__init__(name, required)

    def prepare_string(self, value):
        if self._Column__sanitize_string(value) != value:
            return None
        else:
            return self._Column__enforce_char_limit(
                util.validate_url_string(value),
                self.SIZE,
                False
            )
