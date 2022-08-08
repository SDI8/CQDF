import os
import sys
from importlib import import_module
from multiprocessing.connection import Connection
from typing import NoReturn, TypeVar

from cadquery import Shape, exporters

from .interface import ParameterValueResponse, apply_response, make_parameter
from .parameter import DesignParameters, Value

_child_connection: Connection | None = None
_is_dev: bool = True


def _load_design(file: str, connection: Connection):  # type: ignore
    """
    Entry for sub-process when evaluating a design
    """
    global _child_connection, _is_dev
    _child_connection = connection
    _is_dev = False

    # TODO: many ways this can fail
    directory, module = os.path.split(os.path.abspath(file))
    sys.path.append(directory)
    import_module(module.replace(".py", ""))


TDP = TypeVar("TDP", bound=DesignParameters)


def user_input(param_cls: type[TDP]) -> TDP:
    """
    Instantiates the provided `DesignParameters` class with the users values.
    Should be called at the beginning of the script, right after defining the
    `DesignParameters` class.
    """

    design_params = param_cls()
    if not _is_dev:

        if (
            _child_connection == None
            or not _child_connection.writable
            or _child_connection.closed
        ):
            raise ValueError("No connection to driver.")

        # Filter
        parameter_ex = [
            make_parameter(k, v)  # type: ignore
            for (k, v) in vars(param_cls).items()
            if not k.startswith("_") and isinstance(v, Value)
        ]

        _child_connection.send(parameter_ex)
        res_params: list[ParameterValueResponse] = _child_connection.recv()

        apply_response(design_params, res_params)

    return design_params


def finish(obj: Shape | None) -> NoReturn:
    """
    Marks the end of the evaluation of this design.
    The provided object is treated as the result.
    """

    if not _is_dev:
        if (
            _child_connection == None
            or not _child_connection.writable
            or _child_connection.closed
        ):
            raise ValueError("No connection to driver.")

        _child_connection.send(obj)
    elif obj:
        # TODO: figure out what to do if local
        exporters.export(obj, "out.step", exportType="STEP")  # type: ignore

    raise SystemExit()
