from argparse import ArgumentParser

from cadquery import exporters
from cqdf.driver import finish_evaluate, start_evaluate, terminate_evaluate
from cqdf.interface import ParameterValueResponse
from cqdf.util import JSONCustomEncoder
from path import Path
from rich import print as richprint
from rich import print_json

from cqdf_cli.util import describe_parameters

from .models import ExecuteCLIArgs, ParseCLIArgs, from_ns

PARAM_PREFIX = "p:"

# Set up Argparse
parser = ArgumentParser(
    "cqdf_cli", description="CadQuery Design Format CLI", exit_on_error=False
)
sub_parsers = parser.add_subparsers(title="Sub command", required=True, dest="command")

## Params Command
params_parser = sub_parsers.add_parser("params")
params_parser.add_argument("input", type=Path, help="The file to get parameters for")
params_parser.add_argument("-j", "--json", action="store_true", help="Format as json")

## Execute Command
exec_parser = sub_parsers.add_parser("execute")
exec_parser.add_argument("input", type=Path, help="The file to execute")
exec_parser.add_argument(
    "-o", "--out", type=Path, default="out.step", help="Output file path"
)

cli_args = from_ns(parser.parse_known_args()[0])

if not (
    cli_args.input.exists()
    and cli_args.input.isfile()
    and cli_args.input.endswith(".py")
):
    raise FileNotFoundError("No such file", cli_args.input)

# Evaluate
rid, params = start_evaluate(cli_args.input)
match cli_args:
    case ParseCLIArgs():
        terminate_evaluate(rid)

        if cli_args.json:
            print_json(JSONCustomEncoder().encode(params))
        else:
            richprint(describe_parameters(params))

    case ExecuteCLIArgs():
        param_group = exec_parser.add_argument_group("Parameters")

        for p in params:
            param_group.add_argument(
                f"--{PARAM_PREFIX}{p.key}",
                required=False,
                type=p.value.vtype.value,
                default=p.value.value,
            )
        exec_params = vars(parser.parse_args())

        res_params = [
            ParameterValueResponse(key.removeprefix(PARAM_PREFIX), exec_params[key])
            for key in exec_params
            if key.startswith(PARAM_PREFIX)
        ]

        shape = finish_evaluate(rid, res_params)
        if shape:
            exporters.export(shape, cli_args.out)  # type: ignore
