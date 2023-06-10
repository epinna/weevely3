from core import messages
from core.weexceptions import FatalException
from mako import template
from core.config import sessions_path, sessions_ext
from core.loggers import log, dlog, stream_handler
from core.module import Status
import os
import yaml
import glob
import logging
import urllib.parse
import atexit
import ast
import pprint

arg_blacklist = (
    'default_shell',
    'password',
    'command',
    'path',
    'url',
)

class Session(dict):

    def _session_save_atexit(self):

        with open(self['path'], 'w') as yamlfile:
            yaml.dump(
                dict(self),
                yamlfile,
                default_flow_style = False
            )

    def print_to_user(self, module_filter = ''):
        dlog.info(pprint.pformat(self))

        for arg in self.get_stored_args(module_filter):
            log.info(messages.sessions.set_s_s % arg)

    def get_stored_args(self, term = ''):
        args = []

        for mod_name, mod_value in self.items():
            # Is a module, print all the storable stored_arguments
            if isinstance(mod_value, dict):
                for argument, arg_value in mod_value.get('stored_args', {}).items():
                    path = ("%s.%s" % (mod_name, argument))
                    if not term or path.startswith(term):
                        args.append((path, arg_value))
            # If is not a module, just print if matches with print_filters
            elif mod_name not in arg_blacklist and mod_name.startswith(term):
                args.append((mod_name, mod_value))
        
        return args

    def get_connection_info(self):
     return template.Template(messages.sessions.connection_info).render(
         url = self['url'],
         user = self['system_info']['results'].get('whoami', ''),
         host = self['system_info']['results'].get('hostname', ''),
         path = self['file_cd']['results'].get('cwd', '.')
     )

    def load_session(self, data):
        """
        Update the session dictionary, and occasionally run
        action_<arg> function.
        """

        self.update(data)

        for module_argument, value in data.items():

            # If action_<module_argument> function exists, trigger the action
            action_name = 'action_%s' % (module_argument.replace('.', '_'))
            if hasattr(self, action_name):
                action_func = getattr(self, action_name)
                if hasattr(action_func, '__call__'):
                    action_func(module_argument, value)

    def action_debug(self, module_argument, value):

        if value:
            stream_handler.setLevel(logging.DEBUG)
        else:
            stream_handler.setLevel(logging.INFO)


    def action_proxy(self, module_argument, value):
        """After setting a new proxy, reinitiate channel if already set"""

        if 'shell_php' in self:
            self['shell_php']['status'] = Status.IDLE

    def action_channel(self, module_argument, value):
        """After setting a new channel, reinitiate it"""

        if 'shell_php' in self:
            self['shell_php']['status'] = Status.IDLE

    def unset(self, module_argument):
        """Called by user to unset the session variables"""

        # If action_<module_argument> function exists, trigger the action
        # passing None
        action_name = 'action_%s' % (module_argument.replace('.', '_'))
        if hasattr(self, action_name):
            action_func = getattr(self, action_name)
            if hasattr(action_func, '__call__'):
                action_func(module_argument, None)

        if module_argument.count('.') == 1:
            module_name, arg_name = module_argument.split('.')
            if arg_name not in self[module_name]['stored_args']:
                log.warning(messages.sessions.error_session_s_not_modified % ( '%s.%s' % (module_name, arg_name) ))
            else:
                del self[module_name]['stored_args'][arg_name]
                log.info(messages.sessions.unset_module_s_s % (module_name, arg_name))
        else:
            module_name = module_argument
            if module_name in arg_blacklist or module_name not in self:
                log.warning(messages.sessions.error_session_s_not_modified % (module_name))
            else:
                self[module_name] = None
                log.info(messages.sessions.unset_s % (module_name))


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
        action_name = 'action_%s' % (module_argument.replace('.', '_'))
        if hasattr(self, action_name):
            action_func = getattr(self, action_name)
            if hasattr(action_func, '__call__'):
                action_func(module_argument, value)

        if module_argument.count('.') == 1:
            module_name, arg_name = module_argument.split('.')

            # Should be OK to set whethever variable we want
            # and which will eventually be used by a module.
            self[module_name]['stored_args'][arg_name] = value
            log.info(messages.sessions.set_module_s_s_s % (module_name, arg_name, value))
        else:
            module_name = module_argument
            if module_name in arg_blacklist or module_name not in self:
                log.warning(messages.sessions.error_session_s_not_modified % (module_name))
            else:
                self[module_name] = value
                log.info(messages.sessions.set_s_s % (module_name, value))

class SessionFile(Session):

    def __init__(self, dbpath, volatile = False):

        try:
            with open(dbpath, 'r') as dbfile:
                sessiondb = yaml.safe_load(dbfile.read())
        except Exception as e:
            log.warning(
                messages.generic.error_loading_file_s_s %
                (dbpath, str(e)))
            raise FatalException(messages.sessions.error_loading_sessions)

        if sessiondb and isinstance(sessiondb, dict):

            saved_url = sessiondb.get('url')
            saved_password = sessiondb.get('password')

            if saved_url and saved_password:
                if not volatile:
                    # Register dump at exit and return
                    atexit.register(self._session_save_atexit)

                self.load_session(sessiondb)
                return

        log.warning(
            messages.generic.error_loading_file_s_s %
            (dbpath, 'no url or password'))

        raise FatalException(messages.sessions.error_loading_sessions)

class SessionURL(Session):

    def __init__(self, url, password, volatile = False):

        if not os.path.isdir(sessions_path):
            os.makedirs(sessions_path)

        # Guess a generic hostfolder/dbname
        hostname = urllib.parse.urlparse(url).hostname
        if not hostname:
            raise FatalException(messages.generic.error_url_format)

        hostfolder = os.path.join(sessions_path, hostname)
        dbname = os.path.splitext(os.path.basename(urllib.parse.urlsplit(url).path))[0]

        # Check if session already exists
        sessions_available = glob.glob(
            os.path.join(
                hostfolder,
                '*%s' %
                sessions_ext))

        for dbpath in sessions_available:

            try:
                with open(dbpath, 'r') as dbfile:
                    sessiondb = yaml.safe_load(dbfile.read())
            except Exception as e:
                log.warning(
                    messages.generic.error_loading_file_s_s %
                    (dbpath, str(e)))

            if sessiondb and isinstance(sessiondb, dict):

                saved_url = sessiondb.get('url')
                saved_password = sessiondb.get('password')

                if not saved_url or not saved_password:
                    log.warning(
                        messages.generic.error_loading_file_s_s %
                        (dbpath, 'no url or password'))

                if saved_url == url and saved_password == password:

                    # Found correspondent session file.
                    # Register dump at exit and return
                    if not volatile:
                        atexit.register(self._session_save_atexit)

                    self.load_session(sessiondb)
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
                        'channel': None,
                        'default_shell': None,
                        'proxy': None,
                    }
                )

                # Register dump at exit and return
                if not volatile:
                    atexit.register(self._session_save_atexit)

                self.load_session(sessiondb)
                return

            else:
                index += 1

        raise FatalException(messages.sessions.error_loading_sessions)
