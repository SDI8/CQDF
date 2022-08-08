from dataclasses import dataclass
from enum import Enum
from typing import Generic, Sequence, TypedDict, TypeVar

from typing_extensions import NotRequired, Unpack

from .util import first

TA = TypeVar("TA", float, int, bool, str)
TN = TypeVar("TN", float, int)


class VType(Enum):
    """Valid value type of parameters"""

    Str = str
    Float = float
    Int = int
    Bool = bool


class Unit(Enum):
    unitless = "unitless"
    μm = "micron"
    mm = "millimeter"
    cm = "centimeter"
    m = "meter"
    inch = "inch"
    foot = "foot"


@dataclass(frozen=True)
class Category:
    name: str
    is_advanced: bool = False


class Options(TypedDict):
    name: NotRequired[str]
    description: NotRequired[str]
    unit: NotRequired[Unit]
    category: NotRequired[Category]


class DesignParameters:
    ...


@dataclass
class Value(Generic[TA]):
    """Base class for all parameter types"""

    name: str
    description: str
    unit: Unit
    value: TA
    vtype: VType
    category: Category | None

    def __init__(self, default: TA, **options: Unpack[Options]):
        self.value = default
        self.vtype = VType(type(default))
        self.unit = options.get("unit", Unit.unitless)
        self.name = options.get("name", "")
        self.description = options.get("description", "")
        self.advanced = options.get("advanced", False)
        self.category = options.get("category")


@dataclass(init=False)
class Numeric(Value[TN]):
    """
    A numeric parameter. Valid value types are `int` and `float`
    """


@dataclass(init=False)
class Text(Value[str]):
    """
    A text parameter.
    """


@dataclass(init=False)
class Toggle(Value[bool]):
    """
    A boolean parameter.
    """


@dataclass
class Choice(Value[TA]):
    """
    A parameter which value can only be one of a given set of values.
    All possible values have to be of the same type.
    """

    allowed: Sequence[TA]

    def __init__(
        self,
        allowed: Sequence[TA],
        default: TA | None = None,
        **options: Unpack[Options],
    ):
        self.allowed = allowed
        if len(allowed) == 0:
            raise ValueError("Allowed choices can not be empty.")
        if len(vtypes := set(type(v) for v in allowed)) > 1 and vtypes:
            raise TypeError(
                f"Allowed choices can not be of mixed types. Found {vtypes}"
            )

        default = allowed[0] if default is None else default
        super().__init__(vtypes.pop()(default), **options)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, x: TA):
        if not x in self.allowed:
            raise ValueError(
                f"Value out of range. Should be one of '{self.allowed}' but was '{x}'"
            )
        self._value = x


@dataclass
class Range(Numeric[TN]):
    """
    A numeric parameter which value can only be inside the given range (start and end inclusive).
    """

    start: TN
    end: TN

    def __init__(
        self, start: TN, end: TN, default: TN | None = None, **options: Unpack[Options]
    ):
        self.start = start
        self.end = end
        default = start if default is None else default
        vtype = (
            float
            if first((start, end, default), lambda v: isinstance(v, float)) != None
            else int
        )
        super().__init__(vtype(default), **options)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, x: TN):
        if not self.start <= x <= self.end:
            raise ValueError(
                f"Value out of range. Should be between '{self.start}' and '{self.end}' but was '{x}'"
            )
        self._value = x


class PType(Enum):
    """Types of parameters"""

    Numeric = Numeric
    Text = Text
    Toggle = Toggle
    Choice = Choice
    Range = Range
