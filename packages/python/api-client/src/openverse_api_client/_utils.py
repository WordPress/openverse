from typing_extensions import Any, TypeGuard


class Empty:
    pass


EMPTY = Empty()


def is_empty(val: Any) -> TypeGuard[Empty]:
    return val is EMPTY
