import sys
from logging import Logger, getLogger, Formatter, StreamHandler


def __create_package_logger() -> 'Logger':
    __logger = getLogger("Graphy")
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler = StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    __logger.addHandler(stdout_handler)
    return __logger


logger = __create_package_logger()
