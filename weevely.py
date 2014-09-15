#!/usr/bin/env python

"""Generate obfuscated backdoor.

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
import getopt
import sys
import pprint

if __name__ == '__main__':

    args_optional, args_mandatory = getopt.getopt(sys.argv[1:], '')

    if not args_mandatory:
        log.info(
            '%s\n%s' %
            (messages.generic.error_missing_arguments_s %
             '', __doc__))
    else:

        try:
            if len(args_mandatory) >= 2:
                session = SessionURL(
                    url = args_mandatory[0],
                    password = args_mandatory[1])
            elif len(args_mandatory) == 1:
                session = SessionFile(args_mandatory[0])

            log.debug(
                pprint.pformat(session)
            )

            modules.load_modules(session)
            Terminal(session).cmdloop()

        except (KeyboardInterrupt, EOFError):
            log.info('Exiting.')
        except FatalException as e:
            log.critical('Exiting: %s' % e)
