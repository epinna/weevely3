import logging
import sys
import core.config
import os

log = None
logfile = None

class WeevelyFormatter(logging.Formatter):

    FORMATS = {
        # logging.DEBUG :"[D][%(module)s.%(funcName)s:%(lineno)d] %(message)s",
        logging.DEBUG: "[D][%(module)s] %(message)s",
        logging.INFO: "%(message)s",
        logging.WARNING: "[-][%(module)s] %(message)s",
        logging.ERROR: "[!][%(module)s] %(message)s",
        logging.CRITICAL: "[!][%(module)s] %(message)s",
        'DEFAULT': "[%(levelname)s] %(message)s"}

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)

def setup_logger(logger_name, log_file = None, level = logging.INFO):

    """Returns the proper logger.
    When logfile parameter is set, the logger dumps to the file"""

    l = logging.getLogger(logger_name)
    formatter = WeevelyFormatter()

    if log_file:
        fileHandler = logging.FileHandler(log_file)
        fileHandler.setFormatter(formatter)
        l.addHandler(fileHandler)
    else:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        l.addHandler(streamHandler)

    l.setLevel(level)

if not os.path.isdir(core.config.base_path):
    os.makedirs(core.config.base_path)

setup_logger('log',
              level = logging.DEBUG)
setup_logger('logfile',
              log_file = os.path.join(core.config.base_path, 'weevely.log'),
              level = logging.INFO)

log = logging.getLogger('log')
logfile = logging.getLogger('logfile')
