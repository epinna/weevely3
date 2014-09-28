from core.vectors import PhpCmd, ShellCmd
from core.module import Module
from core import messages
import random
import datetime


class Webdownload(Module):

    """Download URL to the filesystem"""

    def init(self):

        self._register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )


        self._register_vectors(
            [
            PhpCmd("""@file_put_contents("${rpath}", file_get_contents("${url}"));""",
              name = "file_put_contents"
            ),
            ShellCmd("""wget ${url} -O ${rpath}""",
              name = "wget"
            ),
            ShellCmd("""curl -o ${rpath} ${url}""",
              name = "curl"
            )
            ]
        )

        self._register_arguments(
            mandatory = [
                'url',
                'rpath'
            ],
            optional = {
                'vector' : 'file_put_contents'
            },
            bind_to_vectors = 'vector')


    def run(self, args):

        return self.vectors.get_result(
         name = args['vector'],
         format_args = args
        )
