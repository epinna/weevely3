from core import messages
from core.weexceptions import FatalException
from core.config import sessions_path, sessions_ext
from core.loggers import log
import os
import json
import glob
import urlparse
import atexit

class SessionFile(dict):

    def __init__(self, dbpath, volatile = False):

        try:
            sessiondb = json.load(open(dbpath, 'r'))
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

    def _session_save_atexit(self):
        path = self['path']
        json.dump(self, open(path, 'w'))

    def set_from_terminal(self, module_name, value):
        if len(args) > 2:
            args[1] = ' '.join(args[1:])

        if args[0].count('.') == 1:
            module_name, arg_name = args[0].split('.')
            self.session[module_name]['stored_args'][arg_name] = args[1]
            log.info("%s.%s = '%s'" % (module_name, arg_name, args[1]))
        else:
            module_name = args[0]
            self.session[module_name] = args[1]
            log.info("%s = '%s'" % (module_name, args[1]))


class SessionURL(SessionFile):

    def __init__(self, url, password, volatile = False):

        if not os.path.isdir(sessions_path):
            os.makedirs(sessions_path)

        # Guess a generic hostfolder/dbname
        hostname = urlparse.urlparse(url).hostname
        if not hostname:
            raise FatalException(messages.sessions.error_loading_sessions)

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
                sessiondb = json.load(open(dbpath, 'r'))
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
                        'debug': '',
                        'default_shell' : ''
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
