from core.vectors import PhpCode, ShellCmd, ModuleExec, PhpFile, Os
from core.module import Module
from core import modules
import os

class Curl(Module):

    """Perform HTTP requests."""

    aliases = [ 'curl' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors(
            [
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_context.tpl'),
              name = 'php_context',
            ),
            ]
        )

        self.register_arguments([
          { 'name' : 'url' },
          { 'name' : '--header', 'dest' : 'header', 'action' : 'append', 'default' : [] },
          { 'name' : '-H', 'dest' : 'header', 'action' : 'append', 'default' : [] },
          { 'name' : '--cookie', 'dest' : 'cookie', 'action' : 'append', 'default' : [] },
          { 'name' : '-b', 'dest' : 'cookie', 'action' : 'append', 'default' : [] },
          { 'name' : '--user-agent', 'dest' : 'user_agent', 'action' : 'append', 'default' : [] },
          { 'name' : '-A', 'dest' : 'user_agent', 'action' : 'append', 'default' : [] },
          { 'name' : '--data', 'dest' : 'data', 'action' : 'append', 'default' : [] },
          { 'name' : '-d', 'dest' : 'data', 'action' : 'append', 'default' : [] },
          { 'name' : '--request', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT' ), 'default' : 'GET' },
          { 'name' : '-X', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT' ), 'default' : 'GET' },
        ])

    def run(self, args):

        return self.vectors.get_result('php_context', args)
