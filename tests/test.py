import sys
sys.path.append('../')
from python_utils.shell_utils import AsyncCommands, Command, SyncCommands
# import logging
from loguru_logger_lite import Logger

commands = [
    Command('python test1.py', 'test1_process'),
    Command('python test2.py', 'test2_process'),
    Command('python test3.py', 'test3_process')
]

# logging.basicConfig(level=logging.DEBUG)
logger = Logger.get_default_logger()


def cb_stdout(stream: bytes, pid: str, name: str):
    # print(stream)
    logger.info('Subprocess: {name} | PID: {pid} | msg: {msg}'.format(
        msg=stream.decode('utf-8').replace('\n', ''),
        pid=pid,
        name=name
    ))


def cb_stderr(stream: bytes, pid: str, name: str):
    # print(stream)
    logger.error('Subprocess: {name} | PID: {pid} | msg: {msg}'.format(
        msg=stream.decode('utf-8').replace('\n', ''),
        pid=pid,
        name=name
    ))


# AsyncCommands.run_async_shell_commands(commands, 0, cb_stdout, cb_stderr, logger=logger, wait_term=3)
SyncCommands.run_shell_commands(commands, 0, cb_stdout, cb_stderr, logger=logger)
# print(_)
