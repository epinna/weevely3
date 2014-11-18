from core.weexceptions import FatalException
from core import messages

agents_list_path = 'utils/_http/user-agents.txt'

def load_all_agents():

    try:
        agents_file = open(agents_list_path)
    except Exception as e:
        raise FatalException(
            messages.generic.error_loading_file_s_s %
            (agents_list_path, str(e)))

    return agents_file.read().split('\n')
