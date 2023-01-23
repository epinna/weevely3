#!/usr/bin/env python3
import glob
import os
import pprint
import sys

from core import generate
from core import messages
from core import modules
from core.argparsers import CliParser
from core.config import agent_templates_folder_path, obfuscators_templates_folder_path
from core.loggers import log, dlog
from core.sessions import SessionURL, SessionFile
from core.terminal import Terminal
from core.weexceptions import FatalException

if sys.stdout.encoding is None:
    print("Please set PYTHONIOENCODING=UTF-8 running 'export PYTHONIOENCODING=UTF-8' before starting Weevely.")
    exit(1)


def main(arguments):

    if arguments.command == 'generate':

        obfuscated = generate.generate(
            password = arguments.password,
            obfuscator = arguments.obfuscator,
            agent = arguments.agent
        )

        generate.save_generated(obfuscated, arguments.path)

        log.info(
            messages.generate.generated_backdoor_with_password_s_in_s_size_i % (
                arguments.path,
                arguments.password,
                len(obfuscated)
            )
        )

        return

    elif arguments.command == 'terminal':
        session = SessionURL(
            **vars(arguments)
        )

    elif arguments.command == 'session':
        session = SessionFile(arguments.path)

    dlog.debug(
        pprint.pformat(session)
    )

    modules.load_modules(session)

    if not arguments.cmd:
        Terminal(session).cmdloop()
    else:
        Terminal(session).onecmd(arguments.cmd)

if __name__ == '__main__':

    parser = CliParser(prog='weevely')
    subparsers = parser.add_subparsers(dest = 'command')

    terminalparser = subparsers.add_parser('terminal', help='Run terminal or command on the target')
    terminalparser.add_argument('url', help = 'The agent URL')
    terminalparser.add_argument('password', help = 'The agent password')
    terminalparser.add_argument('-H', '--header', dest="headers", action='append', help = '(HTTP)  Extra header to include in the request. This option can be used multiple times to add/replace/remove multiple headers.')
    terminalparser.add_argument('-x', '--proxy', help = 'Use a specific proxy [protocol://]host[:port].')
    terminalparser.add_argument('-u', '--user', help='<user:password> server user and password for basic auth')
    terminalparser.add_argument('cmd', help = 'Command', nargs='?')

    sessionparser = subparsers.add_parser('session', help='Recover an existing session')
    sessionparser.add_argument('path', help = 'Session file path')
    sessionparser.add_argument('cmd', help = 'Command', nargs='?')

    agents_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % agent_templates_folder_path)
    ]

    obfuscators_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % obfuscators_templates_folder_path)
    ]

    generateparser = subparsers.add_parser('generate', help='Generate new agent')
    generateparser.add_argument('password', help = 'Agent password')
    generateparser.add_argument('path', help = 'Agent file path')
    generateparser.add_argument(
        '-obfuscator', #The obfuscation method
        choices = obfuscators_available,
        default = 'phar'
        )
    generateparser.add_argument(
        '-agent', #The agent channel type
        choices = agents_available,
        default = 'obfpost_php'
        )

    parser.set_default_subparser('terminal')

    arguments = parser.parse_args()

    try:
        main(arguments)
    except (KeyboardInterrupt, EOFError):
        log.info('Exiting.')
    except FatalException as e:
        log.critical('Exiting: %s' % e)
