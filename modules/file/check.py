from core.vectors import PhpCmd
from core.module import Module
from core import messages
import random
import datetime


class Check(Module):

    """Check remote files type, md5, or permissions"""

    def init(self):

        self._register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            mandatory = [
                'rpath',
                'check'
            ],
            bind_to_vectors = 'check')

        self._register_vectors(
            [
            PhpCmd(
              "$f='${rpath}';((file_exists($f)||is_readable($f)||is_writable($f)||is_file($f)||is_dir($f))&&print(1))||print(0);",
              name = 'exists',
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCmd("print(md5_file('${rpath}'));",
              name = "md5"
            ),
            PhpCmd("(is_readable('${rpath}') && print(1)) || print(0);",
              name = "readable",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCmd("(is_writable('${rpath}') && print(1))|| print(0);",
              name = "writable",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCmd("(is_executable('${rpath}') && print(1)) || print(0);",
              name = "executable",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCmd("(is_file('${rpath}') && print(1)) || print(0);",
              name = "file",
              postprocess = lambda x: True if x == '1' else False
            ),
            PhpCmd("print(filesize('${rpath}'));",
              name = "size",
              postprocess = lambda x: int(x)
            ),
            PhpCmd("print(filemtime('${rpath}'));",
              name = "time",
              postprocess = lambda x: int(x)
            ),
            PhpCmd("print(filemtime('${rpath}'));",
              name = "datetime",
              postprocess = lambda x: datetime.datetime.fromtimestamp(float(x)).strftime('%Y-%m-%d %H:%M:%S')
            )
            ]
        )

    def run(self, args):

        return self.vectors.get_result(
         name = args['check'],
         arguments = args
        )
