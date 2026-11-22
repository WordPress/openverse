import json

from airflow.sdk.definitions._internal.types import NOTSET
from airflow.sdk.exceptions import AirflowRuntimeError, ErrorType
from airflow.sdk.execution_time.comms import ErrorResponse, PutVariable


class FakeVariable:
    """
    Stand-in for `airflow.sdk.Variable`, whose `set` only works inside a running task.

    Like the real one, it stores values as strings, rejects non-string values unless
    `serialize_json` is set, and raises for a missing key without a default.
    """

    values: dict[str, str] = {}

    @classmethod
    def get(cls, key, default=NOTSET, deserialize_json=False):
        if key not in cls.values:
            if default is NOTSET:
                raise AirflowRuntimeError(
                    ErrorResponse(error=ErrorType.VARIABLE_NOT_FOUND, detail={})
                )
            return default
        value = cls.values[key]
        return json.loads(value) if deserialize_json else value

    @classmethod
    def set(cls, key, value, description=None, serialize_json=False):
        if serialize_json:
            value = json.dumps(value)
        cls.values[key] = PutVariable(
            key=key, value=value, description=description
        ).value

    @classmethod
    def delete(cls, key):
        cls.values.pop(key, None)
