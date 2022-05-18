from core.config import agent_templates_folder_path, obfuscators_templates_folder_path
from mako.template import Template
from core.weexceptions import FatalException
from core import messages
import os

def generate(password, obfuscator = 'obfusc1_php', agent = 'obfpost_php'):

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

    try:
        with open(output, 'w') as genfile:
            genfile.write(obfuscated)
    except Exception as e:
        raise FatalException(
            messages.generic.error_creating_file_s_s %
            (output, e))
