from core.vectors import PhpCode
from core.module import Module
from core import messages
import random
import datetime


class Check(Module):

    """Get remote file information."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        # Declared here since is used by multiple vectors
        payload_perms = """$f='${rpath}';if(@file_exists($f)){print('e');if(@is_readable($f))print('r');if(@is_writable($f))print('w');if(@is_executable($f))print('x');}"""

        self.register_vectors(
            [
            PhpCode(
              payload_perms,
              name = 'exists',
              postprocess = lambda x: True if 'e' in x else False
            ),
            PhpCode("print(md5_file('${rpath}'));",
              name = "md5"
            ),
            PhpCode( payload_perms,
              name = "perms",
            ),
            PhpCode( payload_perms,
              name = "readable",
              postprocess = lambda x: True if 'r' in x else False
            ),
            PhpCode( payload_perms,
              name = "writable",
              postprocess = lambda x: True if 'w' in x else False
            ),
            PhpCode( payload_perms,
              name = "executable",
              postprocess = lambda x: True if 'x' in x else False
            ),
            PhpCode("(is_file('${rpath}') && print(1)) || print(0);",
              name = "file",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCode("(is_dir('${rpath}') && print(1)) || print(0);",
              name = "dir",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCode("print(filesize('${rpath}'));",
              name = "size",
              postprocess = lambda x: int(x)
            ),
            PhpCode("print(filemtime('${rpath}'));",
              name = "time",
              postprocess = lambda x: int(x)
            ),
            PhpCode("print(filemtime('${rpath}'));",
              name = "datetime",
              postprocess = lambda x: datetime.datetime.fromtimestamp(float(x)).strftime('%Y-%m-%d %H:%M:%S')
            ),
            PhpCode("print(realpath('${rpath}'));",
              name = "abspath"
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Target path' },
          { 'name' : 'check', 'choices' : self.vectors.get_names() },
        ])

    def run(self):

        return self.vectors.get_result(
         name = self.args['check'],
         format_args = self.args
        )
