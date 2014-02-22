#!/usr/bin/env python

from core.terminal import Terminal
from core import sessions
import core.log

    
if __name__ == '__main__':
    
    url = 'http://localhost:9090/bd.php'
    password = 'password'
    
    session = sessions.start_session_by_url(url, password)
    
    Terminal(session).cmdloop()