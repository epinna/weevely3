#!/usr/bin/env python

"""Start weevely terminal.

Usage:
  weevely.py <url> <password>
  weevely.py <session file>
"""

from core.terminal import Terminal
from core.weexceptions import FatalException
from core.loggers import log
from core.sessions import SessionURL, SessionFile
from core import modules
from core import messages
from core import config
import sys
import pprint

if __name__ == '__main__':

    try:
        if len(sys.argv) == 3 and sys.argv[1].startswith('http'):
            session = SessionURL(
                url = sys.argv[1],
                password = sys.argv[2])
        elif len(sys.argv) == 2:
            session = SessionFile(sys.argv[1])
        else:
            log.info(__doc__)
            raise FatalException(messages.generic.error_missing_arguments)

        log.debug(
            pprint.pformat(session)
        )

        modules.load_modules(session)
        Terminal(session).cmdloop()

    except (KeyboardInterrupt, EOFError):
        log.info('Exiting.')
    except FatalException as e:
        log.critical('Exiting: %s' % e)
