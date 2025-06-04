from pathlib import Path


base_path = Path("~/.weevely/").expanduser()

# History path
history_path = base_path / "history"

# Session path
sessions_path = base_path / "sessions"
sessions_ext = ".session"

# Supported Channels
channels = [
    # Obfuscated channel inside POST requests introduced
    # in Weevely 3.6
    "ObfPost",
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
agent_templates_folder_path = "bd/agents/"
obfuscators_templates_folder_path = "bd/obfuscators/"


#######################################
# Resolve given paths - DO NOT CHANGE #
#######################################
# weevely_path = Path(sys.argv[0]).resolve().parent
weevely_path = Path(__file__).resolve().parent.parent
agent_templates_folder_path = weevely_path / agent_templates_folder_path
obfuscators_templates_folder_path = weevely_path / obfuscators_templates_folder_path
