from argparse import Namespace
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dacite.core import from_dict


def from_ns(ns: Namespace):
    base = from_dict(CLIArgs, vars(ns))
    dtype = ExecuteCLIArgs if base.command == "execute" else ParseCLIArgs
    return from_dict(dtype, vars(ns))


@dataclass
class CLIArgs:
    command: Literal["execute", "params"]
    input: Path = field(default_factory=Path)


@dataclass
class ExecuteCLIArgs(CLIArgs):
    out: Path = field(default_factory=Path)


@dataclass
class ParseCLIArgs(CLIArgs):
    json: bool = False
