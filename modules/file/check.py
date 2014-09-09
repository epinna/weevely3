from core.vector import Os, Vector
from core.module import Module
from core import messages
import random


class Check(Module):

    """Check remote files type, md5, or permissions

    Usage:
      file_check <path> <check>

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'Check file',
                'description': __doc__,
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            arguments=[
                'rpath',
                'check'
            ],
            vector_argument = 'check')

        self._register_vectors(
            [
            Vector(
              "$f='${args['rpath']}';((file_exists($f)||is_readable($f)||is_writable($f)||is_file($f)||is_dir($f))&&print(1))||print(0);",
              name = 'exists',
              postprocess = lambda x: True if x == '1' else False
            ),
            Vector("print(md5_file('${args['rpath']}'));",
              name = "md5"
            ),
            Vector("(is_readable('${args['rpath']}') && print(1)) || print(0);",
              name = "read",
              postprocess = lambda x: True if x == '1' else False
            ),
            Vector("(is_writable('${args['rpath']}') && print(1))|| print(0);",
              name = "write",
              postprocess = lambda x: True if x == '1' else False
            ),
            Vector("(is_executable('${args['rpath']}') && print(1)) || print(0);",
              name = "exec",
              postprocess = lambda x: True if x == '1' else False
            ),
            Vector("(is_file('${args['rpath']}') && print(1)) || print(0);",
              name = "isfile",
              postprocess = lambda x: True if x == '1' else False
            ),
            Vector("print(filesize('${args['rpath']}'));",
              name = "size",
              postprocess = lambda x: int(x)
            ),
            Vector("print(filemtime('${args['rpath']}'));",
              name = "time_epoch"
            ),
            Vector("print(filemtime('${args['rpath']}'));",
              name = "time",
              postprocess = lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
            )
            ]
        )

    def run(self, args):

        return self._run_vector(args['check'], { 'args' : args })
        

