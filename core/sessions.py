from core import messages
from core.weexceptions import FatalException
from mako import template
from core.config import sessions_path, sessions_ext
from core.loggers import log, stream_handler
from core.module import Status
import os
import yaml
import glob
import logging
import urlparse
import atexit
import ast

print_filters = [
    'debug',
    'channel'
]

set_filters = [
    'debug',
    'channel'
]

class Session(dict):

    def _session_save_atexit(self):

        yaml.dump(
            dict(self),
            open(self['path'], 'w'),
            default_flow_style = False
        )

    def print_to_user(self, module_filter = ''):

        for mod_name, mod_value in self.items():

            if isinstance(mod_value, dict):
                mod_args = mod_value.get('stored_args')

                # Is a module, print all the storable stored_arguments
                for argument, arg_value in mod_args.items():
                    if not module_filter or ("%s.%s" % (mod_name, argument)).startswith(module_filter):
                        log.info("%s.%s = '%s'" % (mod_name, argument, arg_value))
            else:
                # If is not a module, just print if matches with print_filters
                if any(f for f in print_filters if f == mod_name):
                    log.info("%s = '%s'" % (mod_name, mod_value))

    def get_connection_info(self):
     return template.Template(messages.sessions.connection_info).render(
         url = self['url'],
         user = self['system_info']['results'].get('whoami', ''),
         host = self['system_info']['results'].get('hostname', ''),
         path = self['file_cd']['results'].get('cwd', '.')
     )


    def action_debug(self, module_argument, value):

        if value:
            stream_handler.setLevel(logging.DEBUG)
        else:
            stream_handler.setLevel(logging.INFO)

    def set(self, module_argument, value):
        """Called by user to set or show the session variables"""

        # I safely evaluate the value type to avoid to save only
        # strings type. Dirty but effective.
        # TODO: the actual type of the argument could be acquired
        # from modules[module].argparser.
        try:
            value = ast.literal_eval(value)
        except Exception as e:
            # If is not evalued, just keep it as string
            pass

        # If action_<module_argument> function exists, trigger the action
        action_name = 'action_%s' % (module_argument.replace('.','_'))
        if hasattr(self, action_name):
            action_func = getattr(self, action_name)
            if hasattr(action_func, '__call__'):
                action_func(module_argument, value)

        if module_argument.count('.') == 1:
            module_name, arg_name = module_argument.split('.')
            if arg_name not in self[module_name]['stored_args']:
                log.warn(messages.sessions.error_storing_s_not_found % ( '%s.%s' % (module_name, arg_name) ))
            else:
                self[module_name]['stored_args'][arg_name] = value
                log.info("%s.%s = '%s'" % (module_name, arg_name, value))
        else:
            module_name = module_argument
            if module_name not in self or module_name not in set_filters:
                log.warn(messages.sessions.error_storing_s_not_found % (module_name))
            else:
                self[module_name] = value
                log.info("%s = %s" % (module_name, value))

                # If the channel is changed, the basic shell_php is moved
                # to IDLE and must be setup again.
                if module_name == 'channel':
                    self['shell_php']['status'] = Status.IDLE

class SessionFile(Session):

    def __init__(self, dbpath, volatile = False):

        try:
            sessiondb = yaml.load(open(dbpath, 'r').read())
        except Exception as e:
            log.warn(
                messages.generic.error_loading_file_s_s %
                (dbpath, str(e)))
            raise FatalException(messages.sessions.error_loading_sessions)

        saved_url = sessiondb.get('url')
        saved_password = sessiondb.get('password')

        if saved_url and saved_password:
            if not volatile:
                # Register dump at exit and return
                atexit.register(self._session_save_atexit)

            self.update(sessiondb)
            return

        log.warn(
            messages.sessions.error_loading_file_s %
            (dbpath, 'no url or password'))

        raise FatalException(messages.sessions.error_loading_sessions)

class SessionURL(Session):

    def __init__(self, url, password, volatile = False):

        if not os.path.isdir(sessions_path):
            os.makedirs(sessions_path)

        # Guess a generic hostfolder/dbname
        hostname = urlparse.urlparse(url).hostname
        if not hostname:
            raise FatalException(messages.generic.error_url_format)

        hostfolder = os.path.join(sessions_path, hostname)
        dbname = os.path.splitext(os.path.basename(urlparse.urlsplit(url).path))[0]

        # Check if session already exists
        sessions_available = glob.glob(
            os.path.join(
                hostfolder,
                '*%s' %
                sessions_ext))

        for dbpath in sessions_available:

            try:
                sessiondb = yaml.load(open(dbpath, 'r').read())
            except Exception as e:
                log.warn(
                    messages.generic.error_loading_file_s_s %
                    (dbpath, str(e)))
            else:
                saved_url = sessiondb.get('url')
                saved_password = sessiondb.get('password')

                if not saved_url or not saved_password:
                    log.warn(
                        messages.generic.error_loading_file_s_s %
                        (dbpath, 'no url or password'))

                if saved_url == url and saved_password == password:

                    # Found correspondent session file.
                    # Register dump at exit and return
                    if not volatile:
                        atexit.register(self._session_save_atexit)

                    self.update(sessiondb)
                    return

        # If no session was found, create a new one with first available filename
        index = 0

        while True:
            dbpath = os.path.join(
                hostfolder, '%s_%i%s' %
                (dbname, index, sessions_ext))
            if not os.path.isdir(hostfolder):
                os.makedirs(hostfolder)

            if not os.path.exists(dbpath):
                sessiondb = {}
                sessiondb.update(
                    {   'path': dbpath,
                        'url': url,
                        'password': password,
                        'debug': False,
                        'channel' : None,
                        'default_shell' : None
                    }
                )

                # Register dump at exit and return
                if not volatile:
                    atexit.register(self._session_save_atexit)

                self.update(sessiondb)
                return

            else:
                index += 1

        raise FatalException(messages.sessions.error_loading_sessions)
