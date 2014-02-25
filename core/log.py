import logging, sys

class SpecialFormatter(logging.Formatter):
    FORMATS = {logging.DEBUG :"[D][%(module)s.%(funcName)s:%(lineno)d] %(message)s",
               logging.ERROR : "[!][%(module)s] %(message)s",
               logging.INFO : "%(message)s",
               'DEFAULT' : "[%(levelname)s] %(message)s"}

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)

hdlr = logging.StreamHandler(sys.stderr)
hdlr.setFormatter(SpecialFormatter())
logging.root.addHandler(hdlr)
logging.root.setLevel(logging.DEBUG)