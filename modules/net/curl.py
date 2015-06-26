from core.vectors import PhpCode, ShellCmd, ModuleExec, PhpFile, Os
from core.module import Module
from core import modules
from core import messages
from core.loggers import log
import os

class Curl(Module):

    """Perform a curl-like HTTP request."""

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
              payload = """curl -s -i ${ "-A '%s'" % user_agent if user_agent else "" } ${ '--connect-timeout %i' % connect_timeout } ${ '-X %s' % request if (not data and request) else '' } ${ " ".join([ "-H '%s'" % h for h in header ]) } ${ "-b '%s'" % cookie if cookie else '' } ${ ' '.join([ "-d '%s'" % d for d in data ]) } '${ url }'""",
              name = 'sh_curl'
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'url' },
          { 'name' : '--header', 'dest' : 'header', 'action' : 'append', 'default' : [] },
          { 'name' : '-H', 'dest' : 'header', 'action' : 'append', 'default' : [] },
          { 'name' : '--cookie', 'dest' : 'cookie' },
          { 'name' : '-b', 'dest' : 'cookie' },
          { 'name' : '--data', 'dest' : 'data', 'action' : 'append', 'default' : [] },
          { 'name' : '-d', 'dest' : 'data', 'action' : 'append', 'default' : [] },
          { 'name' : '--user-agent', 'dest' : 'user_agent' },
          { 'name' : '-A', 'dest' : 'user_agent' },
          { 'name' : '--connect-timeout', 'type' : int, 'default' : 5, 'help' : 'Default: 2' },
          { 'name' : '--request', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT' ), 'default' : 'GET' },
          { 'name' : '-X', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT' ), 'default' : 'GET' },
          { 'name' : '--output', 'dest' : 'output' },
          { 'name' : '-o', 'dest' : 'output' },
          { 'name' : '-i', 'dest' : 'include_headers', 'help' : 'Include response headers', 'action' : 'store_true', 'default' : False },
          { 'name' : '-local', 'action' : 'store_true', 'default' : False, 'help' : 'Save file locally with -o|--output' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'file_get_contents' }
        ])

    def run(self):

        headers = []
        saved = None

        vector_name, result = self.vectors.find_first_result(
                names = [ self.args.get('vector') ],
                format_args = self.args,
                condition = lambda r: r if r and r.strip() else None
            )

        # Print error and exit with no response or no headers
        if not (vector_name and result):
            log.warn(messages.module_net_curl.unexpected_response)
            return None, headers, saved
        elif not '\r\n'*2 in result:
            # If something is returned but there is \r\n*2, we consider
            # everything as header. It happen with responses 204 No contents
            # that end with \r\n\r (wtf).
            headers = result
            result = ''
        else:
            headers, result = result.split('\r\n'*2, 1)

        headers = (
            [
                h.rstrip() for h
                in headers.split('\r\n')
            ] if '\r\n' in headers
            else headers
        )

        output_path = self.args.get('output')
        if output_path:

            # If response must be saved, it's anyway safer to save it
            # within additional requests
            if not self.args.get('local'):
                saved = ModuleExec('file_upload', [ '-content', result, output_path ]).run()
            else:
                try:
                    open(output_path, 'wb').write(result)
                except Exception as e:
                    log.warning(
                      messages.generic.error_loading_file_s_s % (output_path, str(e)))
                    saved = False
                else:
                    saved = True

        return result, headers, saved

    def print_result(self, result):

        result, headers, saved = result

        # If is saved, we do not want output
        if self.args.get('output'):
            log.info(saved)
            return

        # Print headers if requested
        if self.args.get('include_headers'):
            log.info( '\r\n'.join(headers) + '\r\n')

        if result:
            log.info(result)
