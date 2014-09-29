from core.vectors import PhpCmd
from core.module import Module
from core import messages
import random


class Ls(Module):

    """List directory content ('ls' replacement)"""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments(
            optional = {
                'dir': '.'
            })

    def run(self, args):
	
        return PhpCmd(
                """$p="${dir}";if(@is_dir($p)){$d=@opendir($p);$a=array();if($d){while(($f=@readdir($d))){$a[]=$f;};sort($a);print(join('\n', $a));}}""",
                postprocess = lambda x: x.split('\n')
               ).run(args)

    def print_result(self, result):
        log.info('\n'.join(result))
