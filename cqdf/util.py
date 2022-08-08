from dataclasses import asdict, is_dataclass
from enum import Enum
from json import JSONEncoder
from typing import Any, Callable, Iterable, TypeVar


def natural_str(s: str):
    """
    Converts identifiers to a pretty string
    """
    return " ".join(x.capitalize() or "_" for x in s.split("_"))


T = TypeVar("T")


def first(iterable: Iterable[T], condition: Callable[[T], bool]):
    """
    Returns the first item on which `condition` returns truthy.
    If no items is truthy, returns None.
    """
    return next(
        (e for e in iterable if condition(e)),
        None,
    )


value = first([1, 2, 3, 4, 5.5], lambda x: x > 2)


class JSONCustomEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Enum):
            return o.name
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)
