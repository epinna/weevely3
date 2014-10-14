from core.vectors import PhpCode
from core.module import Module
from core import messages
import random
import datetime


class Check(Module):

    """Check remote file type, md5, or permission."""

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
              "$f='${rpath}';((file_exists($f)||is_readable($f)||is_writable($f)||is_file($f)||is_dir($f))&&print(1))||print(0);",
              name = 'exists',
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCode("print(md5_file('${rpath}'));",
              name = "md5"
            ),
            PhpCode("(is_readable('${rpath}') && print(1)) || print(0);",
              name = "readable",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCode("(is_writable('${rpath}') && print(1))|| print(0);",
              name = "writable",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCode("(is_executable('${rpath}') && print(1)) || print(0);",
              name = "executable",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCode("(is_file('${rpath}') && print(1)) || print(0);",
              name = "file",
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
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Target path' },
          { 'name' : 'check', 'choices' : self.vectors.get_names() },
        ])

    def run(self, args):

        return self.vectors.get_result(
         name = args['check'],
         format_args = args
        )
