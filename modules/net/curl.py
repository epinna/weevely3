from core.vectors import PhpCode, ShellCmd, ModuleExec, PhpFile, Os
from core.module import Module
from core import modules
from core import messages
from core.loggers import log
import os

class Curl(Module):

    """Perform a curl-like HTTP requests."""

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
              name = 'file_get_contents',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_context.tpl'),
              name = 'fopen_stream_get_contents',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_context.tpl'),
              name = 'fopen_fread',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_curl.tpl'),
              name = 'php_curl',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_httprequest1.tpl'),
              name = 'php_httprequest1',
            ),
            ShellCmd(
              payload = """curl -s ${ '-A %s' % user_agent if user_agent else '' } ${ '--connect-timeout %i' % connect_timeout } ${ '-X %s' % request if request else '' } ${ '-H '.join(header) } ${ '-b '.join(cookie) } ${ '-d '.join(data) } ${ url }""",
              name = 'sh_curl',
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'url' },
          { 'name' : '--header', 'dest' : 'header', 'action' : 'append', 'default' : [] },
          { 'name' : '-H', 'dest' : 'header', 'action' : 'append', 'default' : [] },
          { 'name' : '--cookie', 'dest' : 'cookie', 'action' : 'append', 'default' : [] },
          { 'name' : '-b', 'dest' : 'cookie', 'action' : 'append', 'default' : [] },
          { 'name' : '--data', 'dest' : 'data', 'action' : 'append', 'default' : [] },
          { 'name' : '-d', 'dest' : 'data', 'action' : 'append', 'default' : [] },
          { 'name' : '--user-agent', 'dest' : 'user_agent' },
          { 'name' : '-A', 'dest' : 'user_agent' },
          { 'name' : '--connect-timeout', 'type' : int, 'default' : 2, 'help' : 'Default: 2' },
          { 'name' : '--request', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT' ), 'default' : 'GET' },
          { 'name' : '-X', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT' ), 'default' : 'GET' },
          { 'name' : '--output', 'dest' : 'output' },
          { 'name' : '-o', 'dest' : 'output' },
          { 'name' : '-local', 'action' : 'store_true', 'default' : False, 'help' : 'Save file locally with -o|--output' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'file' }
        ])

    def run(self, args):

        vector_name, result = self.vectors.find_first_result(
                names = [ args.get('vector') ],
                format_args = args,
                condition = lambda r: r if r else None
            )

        # Print error and exit with no response
        if not vector_name:
            log.warn(messages.module_net_curl.empty_response)
            return

        # If response must not be saved, just print it
        output_path = args.get('output')
        if not output_path:
            return result[-1:] if result[-1] == '\n' else result

        # If response must be saved, it's anyway safer to save it
        # within additional requests
        if not args.get('local'):
            return ModuleExec('file_upload', [ '-content', result, output_path ]).run()
        else:
            try:
                open(output_path, 'wb').write(result)
            except Exception as e:
                log.warning(
                  messages.generic.error_loading_file_s_s % (output_path, str(e)))
                return
