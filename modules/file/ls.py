from core.vector import Os, Vector
from core.module import Module
from core import messages
import random


class Ls(Module):

    """List directory content (replacement)

    Usage:
      file_ls [--dir=./folder]

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'List files',
                'description': __doc__,
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            options={
                'dir': '.'
            })

    def run(self, args):

        return Vector("""$p="${args['dir']}";if(@is_dir($p)){$d=@opendir($p);$a=array();if($d){while(($f=@readdir($d))){$a[]=$f;};sort($a);print(join('\n', $a));}}""").run(
        { 'args' : args }
        )
