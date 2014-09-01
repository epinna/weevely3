#!/usr/bin/env python

"""Generate obfuscated backdoor.

Usage:
  weevely.py <url> <password>
  weevely.py <session file>

"""

from core.terminal import Terminal
from core import sessions
from core import modules
from core import messages
import getopt
import sys
import core.log
import logging

if __name__ == '__main__':

    args_optional, args_mandatory = getopt.getopt(sys.argv[1:], '')

    if args_mandatory:
        if len(args_mandatory) >= 2:
            session = sessions.start_session_by_url(
                args_mandatory[0],
                args_mandatory[1])
        elif len(args_mandatory) == 1:
            session = sessions.start_session_by_file(args_mandatory[0])

        modules.load_modules(session)
        Terminal(session).cmdloop()

    else:
        logging.info(
            '%s\n%s' %
            (messages.generic.error_missing_arguments_s %
             '', __doc__))
