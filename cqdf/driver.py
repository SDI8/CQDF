from dataclasses import dataclass
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from cadquery import Shape

from .cq_serialize import register
from .design import _load_design  # type: ignore
from .interface import ParameterValue, ParameterValueResponse

register()

FINISH_TIMEOUT = 5


@dataclass
class CurrentRun:
    process: Process
    connection: Connection
    has_params: bool = False


current_runs: dict[int, CurrentRun] = {}


def start_evaluate(path: str):
    run_id, run = _make_run(path)

    # run until script provides us with DesignParameters
    parameter_dtos: list[ParameterValue] = run.connection.recv()
    run.has_params = True
    return run_id, parameter_dtos


def terminate_evaluate(run_id: int):
    run = current_runs.get(run_id)
    if run:
        run.process.terminate()


def finish_evaluate(run_id: int, res_params: list[ParameterValueResponse]):
    run = current_runs.get(run_id)
    if not run:
        raise ValueError("Given run does not exist.")
    if not run.has_params:
        raise ValueError(
            "Can not finish script that has not provided parameters yet. Have you forgotten to call `design.user_input`?"
        )

    try:
        # send response and await completion
        run.connection.send(res_params)
        # TODO: race wait for finish and p.join
        response: Shape | None = run.connection.recv()
        run.process.join(FINISH_TIMEOUT)
    except Exception as e:
        _stop_run(run_id)
        raise e
    else:
        _stop_run(run_id)
        return response


def _make_run(path: str):
    parent_conn, child_conn = Pipe()
    p = Process(
        target=_load_design,
        args=(
            path,
            child_conn,
        ),
    )
    p.start()
    if not p.pid:
        p.terminate()
        raise Exception("Unable to start child process.")

    run = CurrentRun(p, parent_conn)
    current_runs.update({p.pid: run})
    return p.pid, run


def _stop_run(run_id: int):
    run = current_runs.pop(run_id)
    run.connection.close()
    run.process.terminate()
