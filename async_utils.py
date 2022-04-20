import platform
import asyncio
from loguru import logger
import sys


class AsyncCommander():

    def __init__(self, logger):
        self.logger = logger

    async def run_command_shell(self, command, stdout_cb, stderr_cb):
        """Run command in subprocess (shell).

        Note:
            This can be used if you wish to execute e.g. "copy"
            on Windows, which can only be executed in the shell.
        """
        # Create subprocess
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Status
        self.logger.info("Subprocess started. PID: {} COMMAND: {}".format(str(process.pid), command))

        await asyncio.wait([self._read_stream(process.stdout, stdout_cb),
                            self._read_stream(process.stderr, stderr_cb)])

        # # Wait for the subprocess to finish
        # stdout, stderr = await process.communicate()
        #
        # # Progress
        # if process.returncode == 0:
        #     print("Done:", command, "(pid = " + str(process.pid) + ")", flush=True)
        # else:
        #     print(
        #         "Failed:", command, "(pid = " + str(process.pid) + ")", flush=True
        #     )
        #
        # result_out = stdout.decode().strip()
        # result_err = stderr.decode().strip()
        #
        # # Return stdout
        # return {"RESULT": result_out, "ERROR": result_err}
        return await process.communicate()

    def make_chunks(self, l, n):
        """Yield successive n-sized chunks from l.

        Note:
            Taken from https://stackoverflow.com/a/312464
        """
        for i in range(0, len(l), n):
            yield l[i: i + n]

    def run_asyncio_commands(self, tasks, max_concurrent_tasks=0):
        """Run tasks asynchronously using asyncio and return results.

        If max_concurrent_tasks are set to 0, no limit is applied.

        Note:
            By default, Windows uses SelectorEventLoop, which does not support
            subprocesses. Therefore ProactorEventLoop is used on Windows.
            https://docs.python.org/3/library/asyncio-eventloops.html#windows
        """
        all_results = []

        if max_concurrent_tasks == 0:
            chunks = [tasks]
            num_chunks = len(chunks)
        else:
            chunks = self.make_chunks(l=tasks, n=max_concurrent_tasks)
            num_chunks = len(list(self.make_chunks(l=tasks, n=max_concurrent_tasks)))

        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        if platform.system() == "Windows":
            asyncio.set_event_loop(asyncio.ProactorEventLoop())
        loop = asyncio.get_event_loop()

        chunk = 1
        for tasks_in_chunk in chunks:
            self.logger.info("Beginning work on chunk %s/%s" % (chunk, num_chunks))
            commands = asyncio.gather(*tasks_in_chunk)  # Unpack list using *
            results = loop.run_until_complete(commands)
            all_results += results
            self.logger.info("Completed work on chunk %s/%s" % (chunk, num_chunks))
            chunk += 1

        loop.close()
        return all_results

    def run_async_shell_commands(self, commands, max_concurrent_tasks):
        tasks = []
        for command in commands:
            tasks.append(self.run_command_shell(command,
                                                lambda x: self.logger.info(x.decode('utf-8').replace("\n","")),
                                                lambda x: self.logger.error(x.decode('utf-8').replace("\n",""))
                                                ))

        return self.run_asyncio_commands(tasks, max_concurrent_tasks=max_concurrent_tasks)

    async def _read_stream(self, stream, cb):
        while True:
            line = await stream.readline()
            if line:
                cb(line)
            else:
                break

    # async def _stream_subprocess(cmd, stdout_cb, stderr_cb):
    #     process = await asyncio.create_subprocess_exec(*cmd,
    #             stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    #
    #     await asyncio.wait([
    #         _read_stream(process.stdout, stdout_cb),
    #         _read_stream(process.stderr, stderr_cb)
    #     ])
    #     return await process.wait()
    #
    #
    # def execute(cmd, stdout_cb, stderr_cb):
    #     loop = asyncio.get_event_loop()
    #     rc = loop.run_until_complete(
    #         _stream_subprocess(
    #             cmd,
    #             stdout_cb,
    #             stderr_cb,
    #     ))
    #     loop.close()
    #     return rc
