# Base path for log files and sessions
base_path = '~/.weevely/'

# History path
history_path = '~/.weevely/history'

# Session path
sessions_path = '~/.weevely/sessions/'
sessions_ext = '.session'

# Supported Channels
channels = [
    # Obfuscated channel inside POST requests introduced 
    # in Weevely 3.6
    'ObfPost',
]

# Append random GET parameters to every request to
# make sure the page is not cache by proxies.
add_random_param_nocache = False

# Add additional headers to be sent at every request e.g.
# additional_headers = [
#   ( 'Authentication', 'Basic QWxhZGRpbjpvcGVuIHNlc2FtBl==' )
# ]
additional_headers = []

# Agents and obfuscators used by generator.py
agent_templates_folder_path = 'bd/agents/'
obfuscators_templates_folder_path = 'bd/obfuscators/'





#######################################
# Resolve given paths - DO NOT CHANGE #
#######################################
import os, sys
base_path = os.path.expanduser(base_path)
history_path = os.path.expanduser(history_path)
sessions_path = os.path.expanduser(sessions_path)
weevely_path = os.path.dirname(os.path.realpath(sys.argv[0]))
agent_templates_folder_path = os.path.join(
    weevely_path,
    agent_templates_folder_path
)
obfuscators_templates_folder_path = os.path.join(
    weevely_path,
    obfuscators_templates_folder_path
)
