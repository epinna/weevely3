from core.vectors import PhpCmd, ModuleCmd
from core.module import Module
from core import messages
from core.loggers import log
import random
import hashlib
import base64


class Upload(Module):

    """Upload file to remote filesystem."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments(
            # Declare mandatory arguments
            mandatory = [
                'lpath',
                'rpath'
            ],
            # Declare additional options
            optional = {
                'content': '',
                'vector': ''
            },
            bind_to_vectors = 'vector')

        self.register_vectors(
            [
            PhpCmd(
              "(file_put_contents('${rpath}', base64_decode('${content}'))&&print(1)) || print(0);",
              name = 'file_put_contents'
              ),

            PhpCmd(
              """($h=fopen("${rpath}","a+")&&fwrite($h, base64_decode('${content}'))&&fclose($h)&&print(1)) || print(0);""",
              name = "fwrite"
              )
            ]
        )

    def run(self, args):

        # Load local file
        content_orig = args.get('content')
        if not content_orig:

            lpath = args.get('lpath')

            try:
                content_orig = open(lpath, 'r').read()
            except Exception, e:
                log.warning(
                  messages.generic.error_loading_file_s_s % (lpath, str(e)))
                return

        content = base64.b64encode(content_orig)

        # Check remote file existence
        rpath_exists = ModuleCmd('file_check', [ args['rpath'], 'exists' ]).run()
        if rpath_exists:
            log.warning(messages.generic.error_file_s_already_exists % args['rpath'])
            return

        vector_name, result = self.vectors.find_first_result(
         format_args = { 'args' : args, 'content' : content },
         condition = lambda result: True if result == '1' else False
        )
