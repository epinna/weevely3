from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import messages
from core.loggers import log
import random
import hashlib
import base64


class Download(Module):

    """Download file from remote filesystem."""

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
            PhpCode(
              "print(@base64_encode(implode('',@file('${rpath}'))));",
              name = 'file'
              ),
            PhpCode(
              "$f='${rpath}';print(@base64_encode(fread(fopen($f,'rb'),filesize($f))));",
              name = 'fread'
              ),
            PhpCode(
              "print(@base64_encode(file_get_contents('${rpath}')));",
              name = 'file_get_contents'
              ),
            ShellCmd(
              "base64 -w 0 ${rpath} 2>/dev/null",
              name = 'base64',
              target = Os.NIX
              ),
            ]
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Remote file path' },
          { 'name' : 'lpath', 'help' : 'Local file path' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'file' }
        ])

    def run(self):

        # Check remote file existance
        if not ModuleExec('file_check', [ self.args.get('rpath'), 'readable' ]).run():
            log.warning(messages.module_file_download.failed_download_file)
            return

        # Get the remote file MD5. If this is not available, still do a basic check
        # to see if the output is decodable as base64 string.
        expected_md5 = ModuleExec('file_check', [ self.args.get('rpath'), 'md5' ]).run()
        if expected_md5:
            check_md5 = lambda r: r != None and hashlib.md5(base64.b64decode(r)).hexdigest() == expected_md5
        else:
            log.debug(messages.module_file_download.skipping_md5_check)
            check_md5 = lambda r: r != None and bool(base64.b64decode(r))

        # Find the first vector that satisfy the md5 check
        vector_name, result = self.vectors.find_first_result(
         format_args = self.args,
         condition = check_md5
        )

        # Check if find_first_result failed
        if not vector_name:
            log.warning(messages.module_file_download.failed_download_file)
            return

        # Dump to local file
        lpath = self.args.get('lpath')

        try:
            result_decoded = base64.b64decode(result)
            with open(lpath, 'wb') as resultfile:
                resultfile.write(result_decoded)
        except Exception as e:
            log.warning(
              messages.generic.error_loading_file_s_s % (lpath, str(e)))
            return

        return result_decoded

    def print_result(self, result):
        """Override print_result to avoid to print the content"""
        pass
