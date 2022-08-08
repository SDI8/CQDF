from dataclasses import dataclass
from typing import Any, Sequence

from .parameter import DesignParameters, PType, Value, VType
from .util import natural_str


@dataclass
class ParameterValue:
    key: str
    ptype: PType
    value: Value[Any]


@dataclass
class ParameterValueResponse:
    key: str
    value: Any


def make_parameter(key: str, value: Value[Any]):
    """
    Constructs a DTO from the given value
    """

    param = ParameterValue(key, PType(type(value)), value)
    if not param.value.name:
        param.value.name = natural_str(param.key)
    return param


def apply_response(
    params: DesignParameters, res_params: Sequence[ParameterValueResponse]
):
    """
    Updates the design parameters' values from the given responses
    """

    for res_param in res_params:
        if not hasattr(params, res_param.key):
            raise LookupError(f"Received unrecognized parameter {res_param.key}")

        if not isinstance(_param := getattr(params, res_param.key), Value):
            raise TypeError(
                f"Received value for parameter {res_param.key}, which does not subclass `Value`"
            )

        if not (
            isinstance(res_param.value, _param.vtype.value)
            or (_param.vtype == VType.Float and isinstance(res_param.value, int))
        ):
            raise TypeError(
                f"Received value for parameter {res_param.key}, which is of wrong type. "
                + f"Expected {_param.vtype.value}, but received {type(res_param.value)}"
            )

        try:
            _param.value = res_param.value
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Received invalid value for parameter {res_param.key}"
            ) from e
    return params
