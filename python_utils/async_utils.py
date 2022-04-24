# import platform
import asyncio
import time
from typing import List, Callable, Coroutine, Any, Tuple, NamedTuple
from asyncio.streams import StreamReader
# from collections import namedtuple
import logging

# class ILogger:
#     debug: Callable
#     info: Callable
#     warning: Callable
#     error: Callable
#     critical: Callable


Command = NamedTuple('Command', [('command', str), ('name', str)])
Subprocess = NamedTuple('Subprocess', [('proc', asyncio.subprocess.Process), ('name', str)])
OutputCallback = Callable[[bytes, str, str], None]


class AsyncCommands:

    def __init__(self, logger: logging.Logger = None):
        if logger:
            self.logger = logger
        else:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger()

        self.procs: List[Subprocess] = []

        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        # if platform.system() == "Windows":
        #     asyncio.set_event_loop(asyncio.ProactorEventLoop())
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

    def __del__(self):
        self.loop.close()

    @staticmethod
    async def proc_terminate(proc: asyncio.subprocess.Process, wait_sec: int = None):
        proc.terminate()
        if wait_sec:
            time.sleep(wait_sec)
        return await proc.wait()

    def close(self, wait_term: int = None):
        for proc in self.procs:
            if proc.proc.returncode is None:
                if self.loop.is_running():
                    return_code = self.loop.create_task(AsyncCommands.proc_terminate(proc.proc, wait_term))
                else:
                    return_code = self.loop.run_until_complete(AsyncCommands.proc_terminate(proc.proc, wait_term))
            else:
                return_code = proc.proc.returncode
            self.logger.info('Process PID: {pid} exited with code {code}'.format(pid=proc.proc.pid, code=return_code))
        # self.loop.close()

    @staticmethod
    def get_n_batches(data_size: int, batch_size: int) -> int:
        return data_size // batch_size + (
            0 if data_size % batch_size == 0 else 1)

    @staticmethod
    def generate_coro_batches(tasks: List[Coroutine[Any, Any, Tuple[bytes, bytes]]], chunk_size: int):
        for i in range(0, len(tasks), chunk_size):
            yield tasks[i: i + chunk_size]

    @staticmethod
    async def read_stream(stream: StreamReader, cb: Callable[[bytes, str, str], None], pid: str, name: str = None):
        if not name or len(name) == 0:
            name = 'sub-process'
        while True:
            line = await stream.readline()
            if line:
                cb(line, pid, name)
            else:
                break

    async def get_coro(
            self,
            command: Command,
            stdout_cb: OutputCallback = None,
            stderr_cb: OutputCallback = None
    ) -> Tuple[bytes, bytes]:

        # Create subprocess
        proc = await asyncio.create_subprocess_shell(
            command.command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        if not command.name or len(command.name) == 0:
            command_name = 'sub-process'
        else:
            command_name = command.name

        # Add to procs pool
        self.procs.append(Subprocess(proc, command.name))

        # Create output readers
        readers = []
        if stdout_cb:
            readers.append(AsyncCommands.read_stream(proc.stdout, stdout_cb, str(proc.pid), command_name))
        if stderr_cb:
            readers.append(AsyncCommands.read_stream(proc.stderr, stderr_cb, str(proc.pid), command_name))

        if len(readers) > 0:
            await asyncio.wait(readers)

        return await proc.communicate()

    def run_coros(self, tasks: List[Coroutine[Any, Any, Tuple[bytes, bytes]]], max_concurrent_tasks: int = 0):
        all_results = []

        if max_concurrent_tasks == 0:
            coros_batch = [tasks]
            num_batches = len(coros_batch)
        else:
            coros_batch = AsyncCommands.generate_coro_batches(tasks=tasks, chunk_size=max_concurrent_tasks)
            num_batches = AsyncCommands.get_n_batches(len(tasks), max_concurrent_tasks)

        batch = 1
        for tasks_in_batch in coros_batch:
            self.logger.debug("Beginning work on chunk %s/%s" % (batch, num_batches))
            commands = asyncio.gather(*tasks_in_batch)
            if self.loop.is_running():
                results = self.loop.create_task(commands)
            else:
                results = self.loop.run_until_complete(commands)
            all_results += results
            self.logger.info("Completed work on chunk %s/%s" % (batch, num_batches))
            batch += 1

        return all_results

    def _run_async_shell_commands(
            self,
            commands: List[Command],
            max_concurrent_tasks: int,
            cb_stdout: OutputCallback,
            cb_stderr: OutputCallback
    ):
        tasks = []
        for command in commands:
            tasks.append(self.get_coro(command,
                                       stdout_cb=cb_stdout,
                                       stderr_cb=cb_stderr
                                       ))

        return self.run_coros(tasks, max_concurrent_tasks=max_concurrent_tasks)

    @staticmethod
    def run_async_shell_commands(
            commands: List[Command],
            max_concurrent_tasks: int,
            cb_stdout: OutputCallback,
            cb_stderr: OutputCallback,
            logger: logging.Logger = None,
            wait_term: int = None
    ):
        cls = AsyncCommands(logger)

        try:
            return cls._run_async_shell_commands(
                commands,
                max_concurrent_tasks,
                cb_stdout,
                cb_stderr
            )
        except KeyboardInterrupt:
            cls.close(wait_term)
