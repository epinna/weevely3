import logging.handlers
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


if not os.path.isdir(core.config.base_path):
    os.makedirs(core.config.base_path)

"""Initialize the handler to dump log to files"""
log_path = os.path.join(core.config.base_path, 'weevely.log')
file_handler = logging.handlers.RotatingFileHandler(
    log_path,
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=2,
    encoding=None,
    delay=0
    )
file_handler.setFormatter(WeevelyFormatter())

"""Initialize the normal handler"""
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(WeevelyFormatter())

"""Initialize the standard logger"""
log = logging.getLogger('log')
log.addHandler(file_handler)
log.addHandler(stream_handler)
# We can set the a different level for to the two handlers,
# but the global has to be set to the lowest. Fair enough.
log.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.INFO)

"""Initialize the debug logger, that dumps just to logfile"""
dlog = logging.getLogger('dlog')
dlog.addHandler(file_handler)
dlog.setLevel(logging.INFO)
