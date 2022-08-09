import multiprocessing
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from multiprocessing.queues import SimpleQueue
from typing import Any

from cadquery import Shape

from .cq_serialize import register
from .design import _load_design  # type: ignore
from .interface import ParameterValue, ParameterValueResponse

register()


class Session:
    process: Process
    connection: Connection
    queue: SimpleQueue[str]

    def __init__(self) -> None:
        ...

    def __enter__(self):
        self.connection, child_conn = Pipe()
        self.queue = SimpleQueue(ctx=multiprocessing)
        self.process = Process(
            target=_load_design,
            args=(
                self.queue,
                child_conn,
            ),
        )
        self.process.start()
        if not self.process.pid:
            raise Exception("Unable to start child process.")
        return self

    def __exit__(self, _exc_type: Any, _exc_value: Any, _exc_traceback: Any):
        self.connection.close()
        self.queue.close()
        self.process.terminate()

    def add(self, path: str):
        self.queue.put(path)


class Evaluation:
    completed = False
    parameters: list[ParameterValue] | None = None
    result: Shape | None = None

    def __init__(self, path: str, session: Session) -> None:
        self.path = path
        self.session = session

    def start(self) -> list[ParameterValue]:
        """Run until script provides us with DesignParameters. Call `finish` afterwards to complete evaluation"""
        if self.parameters is not None or self.completed:
            raise ValueError(
                "Can not start script that has already started. Have you called `start` before?"
            )
        self.session.add(self.path)
        self.parameters = self.session.connection.recv()
        return self.parameters

    def start_params(self) -> list[ParameterValue]:
        """Run until script provides us with DesignParameters, then terminate evaluation"""
        params = self.start()
        self.session.connection.send(None)
        self.completed = True
        return params

    def finish(self, res_params: list[ParameterValueResponse]):
        """Complete script with the provided ParameterValueResponse"""
        if self.completed:
            raise ValueError(
                "Can not finish script that has already finished. Have you called `finish` before?"
            )
        if not self.parameters:
            raise ValueError(
                "Can not finish script that has not provided parameters yet. Have you forgotten to call `user_input`?"
            )
        try:
            # send response and await completion
            self.session.connection.send(res_params)
            self.result: Shape | None = self.session.connection.recv()
        except Exception as e:
            raise e
        else:
            self.completed = True
            return self.result
