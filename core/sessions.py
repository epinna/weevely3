from core import messages
from core.weexceptions import FatalException
from core.config import sessions_path, sessions_ext
from core.loggers import log
import os
import json
import glob
import urlparse
import atexit


def session_save_atexit(session):
    path = session['path']
    json.dump(session, open(path, 'w'))


def start_session_by_file(dbpath, volatile = False):
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
            atexit.register(session_save_atexit, session=sessiondb)
        return sessiondb

    log.warn(
        messages.sessions.error_loading_file_s %
        (dbpath, 'no url or password'))

    raise FatalException(messages.sessions.error_loading_sessions)


def start_session_by_url(url, password, volatile = False):

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
                    atexit.register(session_save_atexit, session=sessiondb)

                return sessiondb

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
                {'path': dbpath, 'url': url, 'password': password})

            # Register dump at exit and return
            if not volatile:
                atexit.register(session_save_atexit, session=sessiondb)

            return sessiondb

        else:
            index += 1

    raise FatalException(messages.sessions.error_loading_sessions)
