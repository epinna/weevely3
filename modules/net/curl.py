from core.vectors import PhpCode, ShellCmd, ModuleExec, PhpFile, Os
from core.module import Module
from core import modules
from core import messages
from utils.strings import str2hex
from core.loggers import log
import os
from ast import literal_eval
import urllib.request, urllib.parse, urllib.error

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
              arguments = [ '-raw-response' ]
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_context.tpl'),
              name = 'fopen_stream_get_contents',
              arguments = [ '-raw-response' ]
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_context.tpl'),
              name = 'fopen_fread',
              arguments = [ '-raw-response' ]
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_curl.tpl'),
              name = 'php_curl',
              arguments = [ '-raw-response' ]
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'php_httprequest1.tpl'),
              name = 'php_httprequest1',
              arguments = [ '-raw-response' ]
            ),
            
            # TODO: fix this, it fails the "POST request with binary string" test
            # due to some bash limitation with null bytes.
            
            # ShellCmd(
            #   payload = """curl -s -i ${ '-A "$(env echo -ne \"%s\")"' % user_agent if user_agent else "" } ${ '--connect-timeout %i' % connect_timeout } ${ '-X %s' % request if (not data and request) else '' } ${ " ".join([ '-H "$(env echo -ne \"%s\")"' % h for h in header ]) } ${ '-b "$(env echo -ne \"%s\")"' % cookie if cookie else '' } ${ '--data-binary $(env echo -ne "%s")' % ' '.join(data) if data else '' } ${ '$(env echo -ne "%s")' % url }""",
            #   name = 'sh_curl'
            # )
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
          { 'name' : '--request', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT', 'OPTIONS' ), 'default' : 'GET' },
          { 'name' : '-X', 'dest' : 'request', 'choices' : ( 'GET', 'HEAD', 'POST', 'PUT', 'OPTIONS' ), 'default' : 'GET' },
          { 'name' : '--output', 'dest' : 'output' },
          { 'name' : '-o', 'dest' : 'output' },
          { 'name' : '-i', 'dest' : 'include_headers', 'help' : 'Include response headers', 'action' : 'store_true', 'default' : False },
          { 'name' : '-local', 'action' : 'store_true', 'default' : False, 'help' : 'Save file locally with -o|--output' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'file_get_contents' }
        ])

    def _encode(self):
        
        self.args['url'] = str2hex(self.args['url'])
    
        if self.args['data']:
            self.args['data'] = [ str2hex(x) for x in self.args['data'] ]
        
        if self.args['user_agent']:
            self.args['user_agent'] = str2hex(self.args['user_agent'])
        
        if self.args['cookie']:
            self.args['cookie'] = str2hex(self.args['cookie'])

        if self.args['header']:
            self.args['header'] = [ str2hex(x) for x in self.args['header'] ]

    def run(self):

        headers = []
        saved = None
        
        self._encode()

        vector_name, result = self.vectors.find_first_result(
                names = [ self.args.get('vector') ],
                format_args = self.args,
                condition = lambda r: r if r and r.strip() else None
            )

        # Print error and exit with no response or no headers
        if not (vector_name and result):
            log.warning(messages.module_net_curl.unexpected_response)
            return None, headers, saved
        elif not b'\r\n'*2 in result:
            # If something is returned but there is \r\n*2, we consider
            # everything as header. It happen with responses 204 No contents
            # that end with \r\n\r (wtf).
            headers = result
            result = b''
        else:
            headers, result = result.split(b'\r\n'*2, 1)

        headers = (
            [
                h.rstrip() for h
                in headers.split(b'\r\n')
            ] if b'\r\n' in headers
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
                    with open(output_path, 'wb') as resultfile:
                        resultfile.write(result)
                except Exception as e:
                    log.warning(
                      messages.generic.error_loading_file_s_s % (output_path, str(e)))
                    saved = False
                else:
                    saved = True

        return result, headers, saved

    def print_result(self, result):

        resultstring = result[0].decode("utf-8", "replace") 
        headers = [ r.decode("utf-8", "replace") for r in result[1] ] 
        saved = result[2]

        # If is saved, we do not want output
        if self.args.get('output'):
            log.info(saved)
            return

        # Print headers if requested
        if self.args.get('include_headers'):
            log.info( '\r\n'.join(headers) + '\r\n')

        if resultstring:
            log.info(resultstring)
