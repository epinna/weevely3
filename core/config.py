# Base path for log files and sessions
base_path = '~/.weevely/'

# History path
history_path = '~/.weevely/history'

# Session path
sessions_path = '~/.weevely/sessions/'
sessions_ext = '.session'

# Supported Channels
channels = [
    # Steganographed cover channel inside Referrer
    # introduced in Weevely 3.0beta.
    'StegaRef',
    # Legacy payload obfuscation in cookies, introduced
    # in Weevely 0.5.1 the December, 2011.
    'LegacyCookie',
    # Legacy payload obfuscation in referrers, introduced
    # with the first Weevely versions.
    'LegacyReferrer'
]

# Agents and obfuscators used by generator.py
agent_templates_folder_path = 'bd/agents/'
obfuscators_templates_folder_path = 'bd/obfuscators/'
