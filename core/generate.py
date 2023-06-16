import base64
import os
import sys

from mako.template import Template

from core import messages
from core.config import agent_templates_folder_path, obfuscators_templates_folder_path
from core.weexceptions import FatalException



def generate(password, obfuscator = 'phar', agent = 'obfpost_php'):

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

        with open(agent_path, 'r') as templatefile:
            agent = Template(templatefile.read()).render(
                password=password).encode('utf-8')

    except Exception as e:
        raise FatalException(
            messages.generate.error_agent_template_s_s %
            (agent_path, str(e)))

    try:
        obfuscated = obfuscator_template.render(agent=agent)
    except Exception as e:
        raise FatalException(
            messages.generate.error_obfuscator_template_s_s %
            (obfuscator_path, str(e)))

    return obfuscated


def save_generated(obfuscated, output):
    b64 = obfuscated[:4] == 'b64:'
    final = base64.b64decode(obfuscated[4:]) if b64 else obfuscated.encode('utf-8')
    try:
        if output == '-':
            sys.stdout.buffer.write(final)
        else:
            with open(output, 'wb') as outfile:
                outfile.write(final)
    except Exception as e:
        raise FatalException(
            messages.generic.error_creating_file_s_s %
            (output, e))
