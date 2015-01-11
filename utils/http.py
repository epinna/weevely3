from core.weexceptions import FatalException
from core import messages
from core import config
import string
import utils
import os

agents_list_path = 'utils/_http/user-agents.txt'

def load_all_agents():

    try:
        agents_file = open(
            os.path.join(config.weevely_path,
            agents_list_path)
        )
    except Exception as e:
        raise FatalException(
            messages.generic.error_loading_file_s_s %
            (agents_list_path, str(e)))

    return agents_file.read().split('\n')

def add_random_url_param(url):

    random_param = '%s=%s' % (
        utils.strings.randstr(
            n = 4,
            fixed = False,
            charset = string.letterss
        ),
        utils.strings.randstr(
            n = 10,
            fixed = False
        )
    )

    if '?' not in url:
        url += '?%s' % random_param
    else:
        url += '&%s' % random_param

    return url
